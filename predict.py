import sys
import os

# Add backend directory to sys.path to reuse preprocessing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

import joblib
import pandas as pd
import numpy as np
import torch
from datetime import datetime, timedelta

from preprocessing import preprocessor
from app import Informer

# ==========================
# Load trained model
# ==========================
CHECKPOINT_PATH = os.path.join(BASE_DIR, "models", "checkpoints", "Informer", "epoch_10.pth")

num_features = len(preprocessor.feature_order)
num_classes = len(preprocessor.target_encoder.classes_)
seq_len = 5

model = Informer(c_in=num_features, c_out=num_classes, seq_len=seq_len)
model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location='cpu', weights_only=True))
model.eval()

# ==========================
# User Inputs
# ==========================

print("="*60)
print(" SMART GRID RISK PREDICTION")
print(" Forecast Horizon: Next 2 Hours")
print(" Input History: Previous 5 observations (~10 hours)")
print("="*60)

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

print("\nAvailable Divisions:")
divisions = list(division_districts.keys())
for i, d in enumerate(divisions):
    print(f"{i+1}. {d}")

try:
    div_idx = int(input("\nSelect Division Number: ")) - 1
    division = divisions[div_idx]
except (ValueError, IndexError):
    print("Invalid selection. Exiting.")
    sys.exit(1)

print(f"\nAvailable Districts in {division}:")
districts = sorted(division_districts[division])
for i, d in enumerate(districts):
    print(f"{i+1}. {d}")

try:
    dist_idx = int(input("\nSelect District Number: ")) - 1
    district = districts[dist_idx]
except (ValueError, IndexError):
    print("Invalid selection. Exiting.")
    sys.exit(1)

print(f"\nAvailable Upazilas in {district}:")
upazilas = sorted(preprocessor.df[preprocessor.df['district'] == district]['upazila'].unique())
for i, u in enumerate(upazilas):
    print(f"{i+1}. {u}")

try:
    up_idx = int(input("\nSelect Upazila Number: ")) - 1
    upazila = upazilas[up_idx]
except (ValueError, IndexError):
    print("Invalid selection. Exiting.")
    sys.exit(1)

# ==========================
# Feature Retrieval & Prediction
# ==========================
print("\nFetching latest historical telemetry...")

try:
    X_tensor, pred_time, interval_hours, history_df = preprocessor.get_historical_sequence(district, upazila)
except Exception as e:
    print(f"\nError: {e}")
    sys.exit(1)

X_torch = torch.tensor(X_tensor, dtype=torch.float32)

with torch.no_grad():
    out = model(X_torch)
    probs = torch.softmax(out, dim=1).numpy()[0]
    pred_idx = int(torch.argmax(out, dim=1).item())

risk = preprocessor.target_encoder.inverse_transform([pred_idx])[0]

# ==========================
# Display Results
# ==========================

print("\n" + "="*50)
print("SMART GRID RISK PREDICTION")
print("="*50)

print(f"\nLocation       : {district} - {upazila}")
print(f"Forecast       : Next {interval_hours} Hours")
print(f"History        : {len(history_df)} consecutive observations (~{len(history_df) * 2} hours)")

print(f"\nPredicted Risk : {risk.upper()}")

print("\nConfidence:")
for label, prob in zip(preprocessor.target_encoder.classes_, probs):
    print(f"{label:<14} : {prob*100:.1f}%")

# Generate Evidence and Explanation
latest_obs = history_df.iloc[-1]
evidence = {
    "transformer_load": float(latest_obs.get("transformer_load", 0.0)),
    "electricity_demand": float(latest_obs.get("electricity_demand", 0.0)),
    "renewable_generation": float(latest_obs.get("renewable_generation", 0.0)),
    "temperature": float(latest_obs.get("temperature", 0.0)),
    "rainfall": float(latest_obs.get("rainfall", 0.0)),
    "wind_speed": float(latest_obs.get("wind_speed", 0.0))
}

from nlp import generate_explanation
explanation = generate_explanation(risk, evidence)

print("\n" + "-"*50)
print("WHY THIS RISK?")
print("-"*50 + "\n")

import textwrap
print(textwrap.fill(explanation, width=50))

print("\n" + "-"*50)
print("LATEST TELEMETRY EVIDENCE")
print("-"*50 + "\n")

print(f"Transformer Load       : {evidence['transformer_load']:.1f}%")
print(f"Electricity Demand     : {evidence['electricity_demand']:.1f} MW")
print(f"Renewable Generation   : {evidence['renewable_generation']:.1f} MW")
print(f"Temperature            : {evidence['temperature']:.1f} °C")
print(f"Rainfall               : {evidence['rainfall']:.1f} mm")
print(f"Wind Speed             : {evidence['wind_speed']:.1f} m/s")
print()