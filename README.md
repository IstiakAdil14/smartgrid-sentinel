# SmartGrid Sentinel ⚡

SmartGrid Sentinel is an advanced AI-powered risk prediction and monitoring system designed to forecast and prevent failures in smart power grids. By analyzing a multitude of factors—ranging from grid loads and transformer states to real-time weather conditions—it accurately predicts the grid's risk level over a 4-hour horizon. The project focuses specifically on the **Sylhet Division** of Bangladesh, providing insights at both the district and upazila levels.

## 🌟 Key Features

- **LSTM-Based Risk Prediction:** Utilizes a Long Short-Term Memory (LSTM) neural network to capture sequential dependencies in grid data and output one of three risk levels: `Low`, `Medium`, or `High`.
- **Live Weather Integration:** Connects seamlessly with the **Open-Meteo API** to fetch real-time geographic-specific weather data (temperature, humidity, rainfall, wind speed, etc.) for predictions.
- **Rich Dashboard Interface:** A Next.js and TailwindCSS-powered frontend that displays the risk level, probability confidence (via Recharts), live weather conditions, and automated actionable recommendations.
- **Synthetic Data Generator:** A modular Python engine (`generator/`) that builds highly realistic, time-series datasets of grid behavior incorporating weather, fluctuating demand, renewable generation, and asset degradation.
- **Microservices Architecture:** A FastAPI backend decoupled from the Next.js frontend, ensuring scalability and easy integration of new ML models.

---

## 📁 Project Architecture & Structure

The repository is organized into distinct modules:

```text
smartgrid-sentinel/
├── backend/          # FastAPI server for serving predictions and dataset assets
│   ├── app.py        # Main API router and LSTM inference logic
│   └── requirements.txt
├── frontend/         # Next.js 14 web application (React, TailwindCSS, Recharts)
│   ├── src/app/      # Next.js app router pages and layout
│   └── package.json
├── dataset/          # Generated synthetic datasets (e.g., smartgrid_risk_dataset.csv)
│   └── grid_assets.csv
├── generator/        # Python scripts to synthesize realistic grid telemetry data
│   ├── generate_dataset.py
│   ├── weather.py, demand.py, risk.py, etc.
│   └── config.py     # Configuration for data generation constraints
├── models/           # Exported ML artifacts (Models, Scalers, Encoders)
│   ├── lstm_model.keras
│   ├── scaler.pkl
│   └── target_encoder.pkl
├── notebooks/        # Jupyter Notebooks detailing the Data Science lifecycle
│   ├── 01_preprocessing.ipynb
│   ├── 02_train_models.ipynb
│   ├── 03_Notebook_2_LSTM.ipynb
│   └── 04_model_evaluation.ipynb
└── predict.py        # CLI script for local, manual inference
```

---

## 🛠️ Technology Stack

### Machine Learning & Data Science
- **TensorFlow / Keras:** For building and training the LSTM sequence model.
- **Scikit-Learn:** For data preprocessing, scaling (`StandardScaler`), and label encoding.
- **Pandas & NumPy:** For high-performance data manipulation and synthetic dataset generation.
- **Jupyter:** Interactive development and exploratory data analysis (EDA).

### Backend (API)
- **FastAPI:** High-performance async API framework for serving predictions.
- **Uvicorn:** ASGI server for running the FastAPI application.
- **Joblib:** To load scikit-learn preprocessing pipelines.

### Frontend (Dashboard)
- **Next.js 14 (App Router):** React framework for building the user interface.
- **Tailwind CSS:** Utility-first CSS framework for rapid and responsive UI styling.
- **Recharts:** Composable charting library to visualize prediction confidences.
- **Lucide React:** Iconography for a modern look and feel.

---

## 📊 The Data Engine & Features

The model analyzes 21 distinct features to compute the grid risk:

1. **Temporal Features:** `hour`, `weekday`
2. **Weather Features:** `temperature`, `humidity`, `rainfall`, `wind_speed`, `weather_state`
3. **Grid Load Features:** `electricity_demand`, `renewable_generation`, `transformer_load`
4. **Asset & Geographic Features:** `district`, `upazila`, `area_type` (Urban/Rural), `substation_id`, `feeder_id`
5. **Asset Health Features:** `transformer_age`, `transformer_capacity`, `outage_history`, `maintenance_due`
6. **Demographics:** `population_density`, `industrial_load_ratio`

### Generating the Dataset
To recreate the synthetic dataset (e.g., if you modify the constraints in `generator/config.py`):
```bash
cd generator
python generate_dataset.py
```
This script coordinates `weather.py`, `demand.py`, `generation.py`, and `risk.py` to create a massive time-series CSV file (`smartgrid_risk_dataset.csv`) placed in the `dataset/` directory. You can also run individual unit tests in this directory (e.g. `python test_risk.py`).

---

## 📡 API Endpoints (Backend)

The FastAPI backend exposes the following core endpoints:

- `GET /districts`: Returns a list of all supported districts.
- `GET /upazilas/{district}`: Returns the list of upazilas within a specific district.
- `POST /predict`: Accepts a JSON payload containing the `district` and `upazila`. 
  - *Action:* Looks up the static grid assets for that area, fetches real-time Open-Meteo weather data based on geographic coordinates, applies scaling, and passes the tensor to the LSTM model.
  - *Response:* Returns `risk_level`, `confidence` (probabilities for each class), `weather`, `prediction_time` (now + 4 hours), and an array of `recommendation` strings.

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

pip install fastapi uvicorn pandas numpy scikit-learn tensorflow joblib
uvicorn app:app --reload --port 8000
```
The API Swagger documentation will be instantly available at `http://localhost:8000/docs`.

### 2. Start the Frontend Dashboard

Open a separate terminal, navigate to the `frontend` directory, and run the Next.js app:

```bash
cd frontend
npm install
npm run dev
```
The modern dashboard will be available at `http://localhost:3000`. Select your district and upazila from the UI to view real-time grid risk predictions!

---

## 💻 Manual CLI Prediction

If you wish to test the model manually without spinning up the servers, you can use the interactive `predict.py` script from the project root:

```bash
python predict.py
```
The script will prompt you for exact telemetry values (temperature, humidity, transformer age, load, etc.), scale the inputs using `models/scaler.pkl`, and provide an instant prediction of the risk level along with automated recommendations.
