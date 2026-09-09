# 🗳️ Portugal Election 2019 — Final Mandates Prediction

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-Model-F7931E?logo=scikitlearn&logoColor=white)
![Status](https://img.shields.io/badge/Status-Deployed-2D6A4F)

A machine learning project that predicts `FinalMandates` from the *Real-Time Election Results Portugal 2019* dataset, deployed as an interactive Streamlit dashboard.

**Live app:** [portugalelection-2019.streamlit.app](https://portugalelection-2019.streamlit.app/)

---

## 📑 Table of Contents

- [Live Demo](#-live-demo)
- [Project Overview](#-project-overview)
- [Preprocessing Steps](#-preprocessing-steps)
- [Model Building](#-model-building)
- [Tech Stack](#️-tech-stack)
- [Project Structure](#-project-structure)
- [Running Locally](#️-running-locally)
- [Testing the Model](#-testing-the-model)
- [Notes](#-notes)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🚀 Live Demo

The trained model is deployed as a Streamlit dashboard where you can enter election data for a territory/party and get a predicted final mandate count in real time.

| | |
|---|---|
| **URL** | https://portugalelection-2019.streamlit.app/ |
| **Demo username** | `admin` |
| **Demo password** | `admin@123` |

### Dashboard features
- **Secure login gate** — access is gated behind a sign-in screen before any data or predictions are shown.
- **Prediction Dashboard** — grouped, labeled input sections (Election Information, Parish Information, Current Voting Information, Previous Election Information, Party Voting Information) feeding the trained model, with a one-click **Predict Final Mandates** action.
- **Model Overview page** — a read-only summary of the loaded artifacts: recognized territories, recognized parties, and the numeric/categorical columns the model expects.
- **Light / dark theme toggle** — switch appearance from the sidebar; navbar, sidebar, cards, and inputs all follow the selected theme.
- **Responsive layout** — top navbar, sidebar navigation, and input grid adapt down to mobile-width screens.
- **Transparent predictions** — expandable panels show the raw input row and the fully preprocessed (scaled + one-hot encoded) row that was actually passed to the model, alongside the rounded prediction and raw model output.

---

## 📊 Project Overview

This project predicts `FinalMandates` using the Real-Time Election Results Portugal 2019 dataset. It covers data preprocessing, feature engineering, and the implementation and evaluation of several regression models — with particular focus on a K-Nearest Neighbors (KNN) Regressor, Linear Regression, and a Decision Tree Regressor — before deploying the best-performing model behind the Streamlit dashboard above.

### Objectives
- Understand the dataset structure.
- Identify and handle missing or inconsistent values.
- Detect and address duplicate records.
- Analyze the distribution of numerical and categorical variables.
- Identify and manage outliers.
- Prepare the dataset for statistical analysis and machine learning.
- Build and evaluate regression models to predict `FinalMandates`.
- Ship the trained model behind an interactive, presentable dashboard.
- Verify the shipped model artifacts stay healthy over time with an automated sanity check (`test_model.py`).

**Dataset source:** [Real-Time Election Results Portugal 2019 — UCI ML Repository](https://archive.ics.uci.edu/dataset/513/real+time+election+results+portugal+2019)

---

## 🧹 Preprocessing Steps

### 1. Data Loading & Initial Exploration
Initial checks performed with `head()`, `shape()`, `info()`, and `describe()` to understand data types, dimensions, and basic statistics.

### 2. Missing Value & Duplicate Handling
- **Missing values:** checked with `isnull().sum()` — none found.
- **Duplicate records:** checked with `duplicated().sum()` — none found.

### 3. Outlier Detection & Handling
- Outliers identified using **boxplots** across numerical features.
- **IQR method** applied to quantify outliers per column.
- *Decision:* outliers were **kept** rather than removed or clipped, since they likely reflect real-world variation (e.g. large vote counts in major territories/parties).

### 4. Exploratory Data Analysis
- **Countplot** of political party (`Party`) distribution.
- **Histograms** of numerical feature distributions and skew.
- **Boxplots** for distribution/outlier inspection.
- **Scatterplots** of numerical features against the target (`FinalMandates`).

### 5. Feature Engineering
- Pearson correlation matrix + heatmap to spot multicollinearity.
- Mutual Information (MI) scores to rank feature importance.
- **Removed:** highly correlated features (`Hondt`, `Mandates`); low-MI / low-correlation features (`TimeElapsed`, `blankVotesPercentage`, `pre.blankVotesPercentage`, `nullVotesPercentage`, `pre.nullVotesPercentage`); the high-cardinality `time` column.

### 6. Feature Scaling
`StandardScaler` applied to all remaining numeric (`int64`/`float64`) features.

### 7. Categorical Encoding
`OneHotEncoder(sparse_output=False)` applied to `territoryName` and `Party`.

---

## 🧠 Model Building

**Train/test split:** 80/20 (`test_size=0.2`, `random_state=33`).

### Evaluation Comparison

| Model | MSE | MAE | R² Score |
|---|---|---|---|
| KNN Regressor (Baseline) | 0.1363 | 0.0236 | 0.9974 |
| **KNN Regressor (Boosting)** | **0.0002** | **0.0009** | **0.999996** |
| KNN Regressor (Grid Search CV) | 0.0160 | 0.0023 | 0.9997 |
| KNN Regressor (Randomized Search CV) | 0.0261 | 0.0088 | 0.9995 |
| SVR (Baseline) | 0.0043 | 0.0551 | 0.9999 |
| SVR (Bagging) | 0.0058 | 0.0562 | 0.9999 |
| Linear Regression (Baseline) | 13.7068 | 0.8314 | 0.7354 |
| Linear Regression (Boosting) | 14.0666 | 0.7960 | 0.7285 |
| Linear Regression (Grid Search CV) | 13.7068 | 0.8314 | 0.7354 |
| Linear Regression (Randomized Search CV) | 13.7068 | 0.8314 | 0.7354 |
| Decision Tree Regressor (Baseline) | 0.0018 | 0.0018 | 0.99996 |
| Decision Tree Regressor (Bagging/Random Forest) | 0.0758 | 0.0137 | 0.9985 |
| Decision Tree Regressor (Grid Search CV) | 0.0180 | 0.0219 | 0.9997 |
| Decision Tree Regressor (Randomized Search CV) | 0.3678 | 0.0294 | 0.9929 |
| TensorFlow ANN Model | 0.0111 | 0.0245 | 0.9998 |

Deep learning models (TensorFlow ANN, PyTorch regression ANN) were also trained and evaluated for comparison — see the notebook for the PyTorch results.

**Best performer:** the **KNN Regressor (Boosting)** model, with the highest R² (0.999996) and lowest MSE (0.0002) and MAE (0.0009) of all models tested. This is the model deployed behind the live app.

---

## 🛠️ Tech Stack

- **Modeling:** scikit-learn (KNN, Linear Regression, Decision Tree, SVR), TensorFlow, PyTorch
- **Preprocessing:** `StandardScaler`, `OneHotEncoder`
- **App:** Streamlit
- **Data handling:** pandas
- **Testing:** a standalone `test_model.py` sanity-check script (works with or without `pytest`)

---

## 📁 Project Structure

```
.
├── app.py                  # Streamlit dashboard (login, navbar, sidebar, prediction UI)
├── test_model.py           # Sanity-check script for the model artifacts
├── requirements.txt        # Python dependencies for the app + test script
├── model/
│   ├── knn_boost_model.pkl # Trained KNN (boosted) regressor
│   ├── scaler.pkl          # Fitted StandardScaler
│   └── encoder.pkl         # Fitted OneHotEncoder
├── notebook.ipynb          # EDA, preprocessing, model training & evaluation
└── README.md
```

---

## ▶️ Running Locally

```bash
git clone <your-repo-url>
cd <your-repo-folder>
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (typically `http://localhost:8501`) and sign in with the demo credentials above.

---

## ✅ Testing the Model

`test_model.py` is a standalone sanity check that confirms the deployed artifacts (`model/knn_boost_model.pkl`, `model/scaler.pkl`, `model/encoder.pkl`) are healthy and produce a valid prediction — useful after retraining the model, updating scikit-learn, or before every deploy.

It checks that:
1. all three pickle files exist and load without errors,
2. the scaler and encoder were fit on columns this project actually recognizes,
3. the encoder has learned at least one category per categorical column,
4. a full sample row can run end-to-end through the **exact same pipeline** `app.py` uses (scale → one-hot encode → concat → predict) and returns a single, non-`NaN`, sensibly-ranged prediction.

**Run it directly** (no extra dependencies beyond `requirements.txt`):

```bash
python test_model.py
```

Expected output when everything is healthy:

```
============================================================
Portugal Election Prediction - Model Sanity Check
============================================================
[PASS] Model / scaler / encoder files exist
[PASS] Artifacts load correctly
[PASS] Scaler columns match known features
[PASS] Encoder columns match known features
[PASS] Encoder has learned categories
[PASS] End-to-end sample prediction runs
------------------------------------------------------------
Sample input used  : {...}
All checks passed - the model is ready to serve predictions.
============================================================
```

**Or run it with `pytest`**, since every check is also a discoverable `test_*` function:

```bash
pytest test_model.py -v
```

If a check fails, the script prints exactly which one and why (e.g. a missing file, a column the scaler/encoder doesn't recognize, or an exception during prediction), so you know precisely what to fix before redeploying.

---

## 📝 Notes

- The app reads valid territory/party categories directly from the fitted `OneHotEncoder`, so the dropdowns always stay in sync with what the model was actually trained on.
- Predictions are rounded to the nearest whole mandate for display; the raw (unrounded) model output is also shown for transparency.
- `test_model.py` mirrors `app.py`'s feature list and preprocessing order on purpose — if you ever change the feature set in one, update the other.

---

## 📄 License

No license has been specified yet for this project. Add a `LICENSE` file (e.g. MIT, Apache-2.0) if you intend to share or reuse this code publicly.

---

## 🙏 Acknowledgments

- Dataset: [Real-Time Election Results Portugal 2019, UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/513/real+time+election+results+portugal+2019)
- Built with [Streamlit](https://streamlit.io/), [scikit-learn](https://scikit-learn.org/), [pandas](https://pandas.pydata.org/), [TensorFlow](https://www.tensorflow.org/), and [PyTorch](https://pytorch.org/).