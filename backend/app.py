import sympy
import sympy.core
import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import urllib.request
import json
import os

from preprocessing import preprocessor
from nlp import generate_explanation, generate_recommendations

# Define the model architecture exactly as used in training
class Informer(nn.Module):
    def __init__(self, c_in, c_out, seq_len):
        super().__init__()
        self.proj = nn.Linear(c_in, 64)
        self.attn = nn.MultiheadAttention(embed_dim=64, num_heads=4, batch_first=True)
        self.fc1 = nn.Linear(64 * seq_len, 128)
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(128, c_out)
        
    def forward(self, x):
        x = self.proj(x)
        x, _ = self.attn(x, x, x)
        x = x.reshape(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        return self.fc2(x)

app = FastAPI(title="SmartGrid Risk Prediction API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize and load Informer model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINT_PATH = os.path.join(BASE_DIR, "models", "checkpoints", "Informer", "epoch_10.pth")

num_features = len(preprocessor.feature_order)
num_classes = len(preprocessor.target_encoder.classes_)
seq_len = 5

model = Informer(c_in=num_features, c_out=num_classes, seq_len=seq_len)
model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location='cpu', weights_only=True))
model.eval()

# District coordinates for live weather (display only)
district_coords = {
    "Sylhet": {"lat": 24.8949, "lon": 91.8687},
    "Habiganj": {"lat": 24.3840, "lon": 91.4169},
    "Moulvibazar": {"lat": 24.4842, "lon": 91.7685},
    "Sunamganj": {"lat": 25.0664, "lon": 91.4074},
    "Cox's Bazar": {"lat": 21.4272, "lon": 92.0058},
    "Chattogram": {"lat": 22.3569, "lon": 91.7832},
    "Rangamati": {"lat": 22.6533, "lon": 92.1525},
    "Chandpur": {"lat": 23.2333, "lon": 90.6667},
    "Noakhali": {"lat": 22.8696, "lon": 91.0993},
    "Bandarban": {"lat": 22.1953, "lon": 92.2184},
    "Cumilla": {"lat": 23.4683, "lon": 91.1799},
    "Lakshmipur": {"lat": 22.9425, "lon": 90.8412},
    "Khagrachhari": {"lat": 23.1193, "lon": 91.9847},
    "Brahmanbaria": {"lat": 23.9571, "lon": 91.1119},
    "Feni": {"lat": 23.0159, "lon": 91.3976}
}

division_districts = {
    "Chattogram": [
        "Cox's Bazar", "Chattogram", "Rangamati", "Chandpur", 
        "Noakhali", "Bandarban", "Cumilla", "Lakshmipur", 
        "Khagrachhari", "Brahmanbaria", "Feni"
    ],
    "Sylhet": [
        "Habiganj", "Sylhet", "Moulvibazar", "Sunamganj"
    ]
}

class PredictionRequest(BaseModel):
    district: str
    upazila: str

class PredictionResponse(BaseModel):
    risk_level: str
    confidence: dict
    weather: dict
    prediction_time: str
    forecast_horizon_hours: int
    history_observations: int
    history_duration_hours: int
    evidence: dict
    explanation: str
    recommendation: List[str]

@app.get("/divisions")
def get_divisions():
    """Get list of available divisions."""
    return list(division_districts.keys())

@app.get("/districts/{division}")
def get_districts(division: str):
    """Get list of available districts for a division."""
    if division not in division_districts:
        return []
    return sorted(division_districts[division])

@app.get("/upazilas/{district}")
def get_upazilas(district: str):
    """Get upazilas for a given district."""
    upazilas = preprocessor.df[preprocessor.df["district"] == district]["upazila"].unique().tolist()
    return upazilas

@app.post("/predict", response_model=PredictionResponse)
def predict_risk(request: PredictionRequest):
    """Predict risk level for the next 2 hours using Historical Data and Informer Model."""
    
    # 1. Fetch live weather strictly for DISPLAY on dashboard
    base_coords = district_coords.get(request.district, {"lat": 24.8949, "lon": 91.8687})
    upazila_hash = sum(ord(c) for c in request.upazila)
    lat_offset = ((upazila_hash % 100) / 100.0) * 0.4 - 0.2
    lon_offset = (((upazila_hash * 3) % 100) / 100.0) * 0.4 - 0.2
    target_lat = round(base_coords['lat'] + lat_offset, 4)
    target_lon = round(base_coords['lon'] + lon_offset, 4)

    url = f"https://api.open-meteo.com/v1/forecast?latitude={target_lat}&longitude={target_lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'SmartGrid/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            weather_data = json.loads(response.read().decode())
        current_w = weather_data['current']
        temp = current_w['temperature_2m']
        hum = current_w['relative_humidity_2m']
        rain = current_w['precipitation']
        wind = current_w['wind_speed_10m']
        w_code = current_w['weather_code']
        cond_str = "Sunny" if w_code in [0, 1] else "Cloudy" if w_code in [2, 3, 45, 48] else "Stormy" if w_code in [95, 96, 99] else "Rainy"
    except Exception as e:
        temp, hum, rain, wind, cond_str = 30.0, 70.0, 0.0, 5.0, "API Error"

    weather = {
        "temperature": temp,
        "humidity": hum,
        "rainfall": rain,
        "wind_speed": wind,
        "condition": cond_str
    }

    # 2. Get Historical Sequence & Run Inference
    try:
        X_tensor, pred_time, interval_hours, history_df = preprocessor.get_historical_sequence(
            request.district, request.upazila, live_weather=weather
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    X_torch = torch.tensor(X_tensor, dtype=torch.float32)
    
    with torch.no_grad():
        out = model(X_torch)
        probs = torch.softmax(out, dim=1).numpy()[0]
        pred_idx = int(torch.argmax(out, dim=1).item())

    # Map target encoded prediction to string
    risk_level = preprocessor.target_encoder.inverse_transform([pred_idx])[0]
    
    conf_dict = {}
    for label, prob in zip(preprocessor.target_encoder.classes_, probs):
        conf_dict[label] = float(prob)

    # Extract Evidence from the latest observation (5th row)
    latest_obs = history_df.iloc[-1]
    evidence = {
        "transformer_load": float(latest_obs.get("transformer_load", 0.0)),
        "electricity_demand": float(latest_obs.get("electricity_demand", 0.0)),
        "renewable_generation": float(latest_obs.get("renewable_generation", 0.0)),
        "temperature": float(latest_obs.get("temperature", 0.0)),
        "rainfall": float(latest_obs.get("rainfall", 0.0)),
        "wind_speed": float(latest_obs.get("wind_speed", 0.0)),
        "humidity": float(latest_obs.get("humidity", 0.0))
    }
    
    # Generate Natural Language Explanation
    explanation = generate_explanation(risk_level, evidence)

    # 3. Generate Dynamic Action Protocols (Recommendations)
    recs = generate_recommendations(risk_level, evidence)

    return {
        "risk_level": risk_level,
        "confidence": conf_dict,
        "weather": weather,
        "prediction_time": pred_time.strftime("%H:%M"),
        "forecast_horizon_hours": interval_hours,
        "history_observations": len(history_df),
        "history_duration_hours": len(history_df) * 2,
        "evidence": evidence,
        "explanation": explanation,
        "recommendation": recs
    }