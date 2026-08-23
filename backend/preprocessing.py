import os
import joblib
import pandas as pd
import numpy as np

# Global paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "datasetNew", "mergeDataset.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

class Preprocessor:
    def __init__(self):
        # Load dataset
        self.df = pd.read_csv(DATASET_PATH)
        self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        
        # Build deterministic upazila -> (substation, feeder) map
        self.upazila_asset_map = {}
        for upazila, group in self.df.groupby('upazila'):
            first_row = group.iloc[0]
            self.upazila_asset_map[upazila] = (first_row['substation_id'], first_row['feeder_id'])
            
        # Load encoders and scaler
        self.categorical_encoders = joblib.load(os.path.join(MODELS_DIR, "categorical_encoders.pkl"))
        self.scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
        self.target_encoder = joblib.load(os.path.join(MODELS_DIR, "target_encoder.pkl"))
        self.feature_order = list(self.scaler.feature_names_in_)

    def get_asset_for_upazila(self, upazila: str):
        return self.upazila_asset_map.get(upazila, (None, None))

    def get_historical_sequence(self, district: str, upazila: str, live_weather: dict = None):
        """
        Retrieves the last 5 chronological observations and processes them 
        into a (1, 5, 28) tensor equivalent for Informer.
        If live_weather is provided, the latest observation's weather features
        are overridden with live internet data before inference.
        """
        substation_id, feeder_id = self.get_asset_for_upazila(upazila)
        if not substation_id:
            raise ValueError(f"No asset mapping found for upazila {upazila}")
            
        # Filter same asset stream
        asset_df = self.df[
            (self.df['district'] == district) & 
            (self.df['upazila'] == upazila) & 
            (self.df['substation_id'] == substation_id) & 
            (self.df['feeder_id'] == feeder_id)
        ].copy()
        
        # Sort chronological order
        asset_df = asset_df.sort_values("datetime")
        
        if len(asset_df) < 5:
            raise ValueError("Not enough historical observations. Expected at least 5.")
            
        # Take the most recent 5 observations regardless of intervals
        history = asset_df.tail(5).copy()
        times = history['datetime'].tolist()
        
        # The Informer model is strictly a 2-hour-ahead forecasting model.
        # Even if the dataset has missing gaps, we mathematically predict T+2H.
        interval_hours = 2
        prediction_time = times[-1] + pd.Timedelta(hours=2)
        
        # Override the latest observation with live weather data if provided
        if live_weather:
            last_idx = history.index[-1]
            if 'temperature' in live_weather:
                history.loc[last_idx, 'temperature'] = live_weather['temperature']
            if 'humidity' in live_weather:
                history.loc[last_idx, 'humidity'] = live_weather['humidity']
            if 'rainfall' in live_weather:
                history.loc[last_idx, 'rainfall'] = live_weather['rainfall']
            if 'wind_speed' in live_weather:
                history.loc[last_idx, 'wind_speed'] = live_weather['wind_speed']
        
        # Feature Engineering (exactly as in notebook 01)
        cap_smooth = history['transformer_capacity'] + 1e-5
        history['load_utilization'] = history['transformer_load'] / cap_smooth
        history['demand_utilization'] = history['electricity_demand'] / cap_smooth
        history['renewable_ratio'] = history['renewable_generation'] / (history['electricity_demand'] + 1e-5)
        history['thi'] = history['temperature'] + 0.55 * (1 - history['humidity']/100.0) * (history['temperature'] - 14.5)
        history['wind_temp_interaction'] = history['wind_speed'] * history['temperature']
        history['is_peak_hour'] = history['hour'].apply(lambda h: 1 if 18 <= h <= 22 else 0)
        history['is_weekend'] = history['weekday'].apply(lambda w: 1 if w >= 5 else 0)
        
        # Categorical Encoding
        for col, le in self.categorical_encoders.items():
            # Strict mapping: raise error if unknown category appears
            unknowns = set(history[col]) - set(le.classes_)
            if unknowns:
                raise ValueError(f"Unknown categories {unknowns} found in column '{col}'. Valid categories are {le.classes_}.")
            history[col] = le.transform(history[col])
            
        # Select and order features
        X = history[self.feature_order]
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Reshape to (1, 5, 28)
        X_tensor = X_scaled.reshape(1, 5, len(self.feature_order))
        
        return X_tensor, prediction_time, interval_hours, history

# Instantiate a singleton to be imported by app.py and predict.py
preprocessor = Preprocessor()
