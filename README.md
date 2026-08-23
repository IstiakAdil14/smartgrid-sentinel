# SmartGrid Sentinel ⚡

SmartGrid Sentinel is an advanced AI-powered risk prediction and monitoring system designed to forecast and prevent failures in smart power grids. By analyzing a multitude of factors—ranging from historical grid loads and transformer states to real-time weather conditions—it accurately predicts the grid's risk level over a 2-hour horizon using a state-of-the-art **Informer** neural network architecture. The project focuses on providing actionable insights at both the district and upazila levels for the **Sylhet** and **Chattogram** divisions of Bangladesh, specifically catering to general citizens and grid operators.

## 🌟 Key Features

- **Informer-Based Risk Prediction:** Utilizes the cutting-edge Informer model (a Transformer-based architecture optimized for long time-series forecasting) to capture sequential dependencies across a 5-step historical window (~10 hours) and output one of three risk levels: `Low`, `Medium`, or `High`.
- **Live Weather Injection:** Connects seamlessly with the **Open-Meteo API** to fetch real-time geographic-specific weather data. This live data is dynamically injected into the historical sequence during inference, ensuring the model's predictions reflect the immediate environmental reality.
- **Evidence-Based NLP Explanation:** Features a deterministic, rule-based Natural Language Generation (NLG) layer that translates the numerical telemetry into a human-readable, conversational narrative. It explains the exact conditions associated with the risk without falsely claiming model interpretability.
- **Citizen-Oriented Suggestions:** Dynamically issues non-technical, user-oriented guidance (e.g., "Charge essential devices," "Avoid high-power appliances") based on the severity of the predicted risk, making the dashboard highly actionable for the general public.
- **Extensive Geographic Scope:** Models grid behaviors across two major divisions of Bangladesh: **Sylhet** and **Chattogram**, utilizing real-world demographic and asset characteristics to synthesize the data.
- **Rich Dashboard Interface:** A Next.js and TailwindCSS-powered frontend that beautifully visualizes the Informer Risk Forecast, Probability Confidence Chart, Live Telemetry Evidence, and User Suggestions.
- **Microservices Architecture:** A robust FastAPI backend completely decoupled from the React frontend, handling preprocessing, model inference, and NLP generation.

---

## 📁 Project Architecture & Structure

The repository is organized into distinct modules:

```text
smartgrid-sentinel/
├── backend/          # FastAPI server for serving predictions and NLP explanations
│   ├── app.py        # Main API router and Informer inference logic
│   ├── nlp.py        # Rule-based Natural Language Generation for risk explanations
│   ├── preprocessing.py # Data sequence extraction and feature engineering
│   └── requirements.txt
├── frontend/         # Next.js 14 web application (React, TailwindCSS, Recharts)
│   ├── src/app/      # Next.js app router pages and layout
│   └── package.json
├── dataset/          # Generated synthetic datasets (e.g., smartgrid_risk_dataset.csv)
├── generator/        # Python scripts to synthesize realistic grid telemetry data
├── models/           # Exported ML artifacts (Checkpoints, Scalers, Encoders)
│   ├── checkpoints/  # Training epochs (Informer, LSTM, Autoformer, etc.)
│   ├── scaler.pkl
│   └── target_encoder.pkl
├── notebooks/        # Jupyter Notebooks detailing the Data Science lifecycle
│   ├── 01_preprocessing.ipynb
│   ├── 04_train_Informer.ipynb
│   └── ...
└── predict.py        # Interactive CLI script for terminal-based inference
```

---

## 🛠️ Technology Stack

### Machine Learning & Data Science
- **PyTorch:** For building, training, and running inference with the Informer neural network.
- **Scikit-Learn:** For data preprocessing, scaling (`StandardScaler`), and label encoding.
- **Pandas & NumPy:** For high-performance data manipulation, sequence extraction, and feature engineering.

### Backend (API)
- **FastAPI:** High-performance async API framework for serving predictions and NLP generation.
- **Uvicorn:** ASGI server for running the FastAPI application.

### Frontend (Dashboard)
- **Next.js 14 (App Router):** React framework for building the user interface.
- **Tailwind CSS:** Utility-first CSS framework for rapid and responsive UI styling.
- **Recharts:** Composable charting library to visualize prediction confidences.
- **Lucide React:** Iconography for a modern look and feel.

---

## 📊 The Data Engine & Features

The Informer model analyzes a 5-step historical sequence containing 28 distinct features to compute the grid risk:

1. **Temporal Features:** `hour`, `weekday`, `is_peak_hour`, `is_weekend`
2. **Weather Features:** `temperature`, `humidity`, `rainfall`, `wind_speed`, `thi`, `wind_temp_interaction`
3. **Grid Load Features:** `electricity_demand`, `renewable_generation`, `transformer_load`, `load_utilization`, `demand_utilization`, `renewable_ratio`
4. **Asset & Geographic Features:** `district`, `upazila`, `area_type`, `substation_id`, `feeder_id`
5. **Asset Health Features:** `transformer_age`, `transformer_capacity`, `outage_history`, `maintenance_due`
6. **Demographics:** `population_density`, `industrial_load_ratio`

---

## 🏆 Model Architectures & Performance Comparison

During the data science lifecycle, we rigorously trained and evaluated **8 different advanced deep learning architectures** to determine the optimal model for 2-hour ahead sequential forecasting on our telemetry dataset. 

The models tested include:
1. **Recurrent Networks:** LSTM, GRU, CNN-LSTM
2. **Transformers:** Informer, Autoformer, PatchTST, TFT (Temporal Fusion Transformer)
3. **Advanced Time-Series:** TimesNet

**Key Findings:**
- The **Informer** architecture drastically outperformed standard recurrent networks like LSTM and GRU in both accuracy (99.70%) and F1-Score (0.99) on our 5-step multivariate time-series sequences. 
- Models like PatchTST and TimesNet were highly computationally expensive and achieved marginal returns or underperformed on our specific feature set.
- Due to its optimized ProbSparse Self-Attention mechanism, the **Informer** was selected for production as it efficiently captures long-range dependencies while remaining lightweight enough for real-time API inference.

---

## 📡 API Endpoints (Backend)

The FastAPI backend exposes the following core endpoints:

- `GET /divisions`: Returns a list of all supported divisions.
- `GET /districts/{division}`: Returns a list of all supported districts.
- `GET /upazilas/{district}`: Returns the list of upazilas within a specific district.
- `POST /predict`: Accepts a JSON payload containing the `district` and `upazila`. 
  - *Action:* Looks up the static grid assets for that area, retrieves the last 5 historical observations, fetches real-time Open-Meteo weather data, injects the live weather into the sequence, scales the features, and executes Informer inference.
  - *Response:* Returns `risk_level`, `confidence`, `weather`, `forecast_horizon_hours`, `evidence` (the final row of telemetry), `explanation` (dynamic NLP narrative), and an array of `recommendation` strings (citizen suggestions).

---

## ⚙️ Setup and Installation Guide

### Prerequisites
- Python 3.8 or higher
- Node.js 18 or higher

### 1. Start the Backend API

Open a terminal and navigate to the `backend` directory. Install the dependencies and run the server:

```bash
cd backend
# We recommend using a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt # (Ensure torch, fastapi, uvicorn, pandas, numpy, scikit-learn are installed)

# Run the backend
python -m uvicorn app:app --reload --port 8000
```
The API Swagger documentation will be instantly available at `http://localhost:8000/docs`.

### 2. Start the Frontend Dashboard

Open a separate terminal, navigate to the `frontend` directory, and run the Next.js app:

```bash
cd frontend
npm install
npm run dev
```
The modern dashboard will be available at `http://localhost:3000`. Select your division, district, and upazila from the UI to view real-time grid risk predictions and NLP explanations!

**Demo Video:** [Watch Demo Video](https://drive.google.com/file/d/1jSmiQn70eyOF-cmLPmA6pbxFwiAXJIr7/view?usp=drive_link)

---

## 💻 Manual CLI Prediction

If you wish to test the end-to-end pipeline manually in your terminal, you can use the interactive `predict.py` script from the project root:

```bash
python predict.py
```
The script will prompt you to select a geographic location, run the exact same preprocessor logic, execute the Informer model, and print out a beautifully formatted summary including the NLP explanation and the telemetry evidence table.
