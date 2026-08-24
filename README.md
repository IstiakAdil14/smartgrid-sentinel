# SmartGrid Sentinel ⚡

SmartGrid Sentinel is an advanced AI-powered risk prediction and monitoring system designed to forecast and prevent failures in smart power grids. By analyzing a multitude of factors—ranging from historical grid loads and transformer states to real-time weather conditions—it accurately predicts the grid's risk level over a 2-hour horizon using a state-of-the-art **PyTorch Informer** neural network architecture. 

The project provides actionable insights at both the district and upazila levels for the Sylhet and Chattogram divisions of Bangladesh, generating human-readable explanations and action protocols for general citizens and grid operators alike.

## 🌟 Key Features

- **Informer-Based Risk Prediction:** Utilizes the cutting-edge Informer model (a Transformer-based architecture optimized for long time-series forecasting) to capture sequential dependencies across a 5-step historical window (~10 hours) and output one of three risk levels: `Low`, `Medium`, or `High`.
- **Live Weather Injection:** Connects seamlessly with the **Open-Meteo API** to fetch real-time geographic-specific weather data. This live data is dynamically injected into the historical sequence during inference, ensuring predictions reflect immediate environmental realities.
- **Evidence-Based NLP Explanation:** Features a deterministic, rule-based Natural Language Generation (NLG) layer that translates the numerical telemetry into a conversational narrative. It explains the exact conditions associated with the risk without falsely claiming model interpretability.
- **Citizen-Oriented Suggestions:** Dynamically issues non-technical, user-oriented guidance (e.g., "Charge essential devices," "Avoid high-power appliances") based on the severity of the predicted risk.
- **Rich Dashboard Interface:** A Next.js and TailwindCSS-powered frontend that beautifully visualizes the Informer Risk Forecast, Probability Confidence Chart, Live Telemetry Evidence, and User Suggestions.
- **Microservices Architecture:** A robust FastAPI backend completely decoupled from the React frontend, handling data scaling, sequence extraction, model inference, and NLP generation.

---

## 📁 Project Architecture & Structure

The repository is organized into a modular full-stack architecture:

```text
smartgrid-sentinel/
├── backend/          # FastAPI server for serving predictions and NLP explanations
│   ├── app.py        # Main API router, Inference engine, and PyTorch Informer definition
│   ├── nlp.py        # Rule-based Natural Language Generation for risk explanations
│   ├── preprocessing.py # Data sequence extraction, scaling, and feature engineering
│   └── requirements.txt
├── frontend/         # Next.js 14 web application (React, TailwindCSS, Recharts)
│   ├── src/          # Next.js app router pages and UI components
│   └── package.json
├── dataset/          # Static grid asset data and simulated telemetry
├── models/           # Exported ML artifacts (Checkpoints, Scalers, Encoders)
│   ├── checkpoints/  # Saved PyTorch training epochs
│   └── best_model_info.json # Automated best-model selection artifact
├── notebooks/        # Data Science lifecycle and evaluation
│   ├── 01_preprocessing.ipynb
│   ├── 04_model_evaluation.ipynb # Final empirical test set analysis
│   └── ...
├── results/          # Training dynamics (Epoch-by-epoch loss/accuracy tracking)
└── predict.py        # Interactive CLI script for terminal-based inference
```

---

## 🛠️ Technology Stack

### Machine Learning & Data Engine
- **PyTorch:** For building, training, and running inference with the advanced Informer neural network.
- **Scikit-Learn:** For data preprocessing, Standard scaling, and target label encoding.
- **Pandas & NumPy:** High-performance data manipulation and sequential history extraction.

### Backend (Microservice API)
- **FastAPI:** High-performance async API framework serving predictions.
- **Uvicorn:** ASGI server for running the FastAPI application.

### Frontend (Dashboard)
- **Next.js 14 (App Router):** Modern React framework for building the user interface.
- **Tailwind CSS:** Utility-first CSS framework for rapid and responsive UI styling.
- **Recharts:** Composable charting library to visualize class prediction probabilities.
- **Lucide React:** Sleek, modern iconography.

---

## 🏆 Model Architectures & Empirical Analysis

During the data science lifecycle, we rigorously trained and evaluated **12 different machine learning architectures** (spanning Classical ML, Recurrent Neural Networks, and Transformers) to determine the optimal model for 2-hour ahead sequential risk forecasting.

The models tested include:
1. **Classical ML:** Logistic Regression, Decision Tree, Random Forest, XGBoost
2. **Recurrent Networks:** LSTM, GRU, CNN-LSTM
3. **Transformers & Advanced Time-Series:** Informer, Autoformer, PatchTST, TFT, TimesNet

**Key Findings from our Deep Analysis:**
- **The Overfitting Trap:** While standard RNNs like GRU achieved slightly higher raw accuracy (~87.69%), epoch analysis revealed they suffered from severe overfitting—aggressively memorizing the training sequence while their validation loss ballooned.
- **The Classical Baseline:** Random Forest proved to be an exceptionally strong baseline, achieving the absolute highest Macro F1 Score (~77.87%) across all classes, proving its resilience to the class imbalance.
- **Computational Cost:** Heavy architectures like PatchTST (~350s training time) and TimesNet were computationally expensive and offered diminishing returns on our specific feature set.
- **The Production Winner:** The **Informer** was selected for backend production because it offered the perfect balance: it achieved the highest Weighted F1 Score (~88.44%), demonstrated highly stable training dynamics without severe overfitting, trained 3x faster than heavy transformers, and maintained strong, reliable recall for catching critical High-Risk grid failures.

---

## 📡 API Endpoints (FastAPI)

The backend exposes the following core endpoints for the frontend application:

- `GET /divisions`: Returns a list of all supported geographical divisions.
- `GET /districts/{division}`: Returns a list of supported districts within a division.
- `GET /upazilas/{district}`: Returns the list of localized upazilas within a specific district.
- `POST /predict`: 
  - **Payload:** Accepts a JSON body containing `district` and `upazila`.
  - **Action:** Looks up static grid assets, retrieves the last 5 historical observations (10 hours of telemetry), fetches real-time Open-Meteo weather data based on geographic coordinates, injects live weather into the sequence, scales features, and executes PyTorch Informer inference.
  - **Response:** Returns `risk_level`, `confidence` dictionaries, live `weather`, `evidence` (the final row of telemetry), `explanation` (dynamic NLP narrative), and an array of `recommendation` action protocols.

---

## ⚙️ Setup and Installation Guide

### Prerequisites
- Python 3.8 or higher
- Node.js 18 or higher

### 1. Start the Backend API
Navigate to the `backend` directory, install dependencies, and run the FastAPI server:

```bash
cd backend
# We recommend using a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required dependencies
pip install fastapi uvicorn torch pandas numpy scikit-learn sympy

# Run the backend server
python -m uvicorn app:app --reload --port 8000
```
The API Swagger documentation will be available instantly at `http://localhost:8000/docs`.

### 2. Start the Frontend Dashboard
Open a separate terminal, navigate to the `frontend` directory, install Node packages, and run the Next.js app:

```bash
cd frontend
npm install
npm run dev
```
The modern SmartGrid Sentinel dashboard will be available at `http://localhost:3000`. Select your division, district, and upazila from the UI to view real-time grid risk predictions, live weather integration, and NLP explanations!

---

## 💻 Manual CLI Prediction

If you wish to test the end-to-end AI pipeline manually in your terminal (bypassing the web dashboard), you can use the interactive `predict.py` script from the project root:

```bash
python predict.py
```
The script will prompt you to select a geographic location, run the exact same data extraction and preprocessor logic, execute the PyTorch Informer model, and print out a beautifully formatted summary in your terminal—including the NLP explanation and the telemetry evidence.
