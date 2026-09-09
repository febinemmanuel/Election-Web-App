import streamlit as st
import pandas as pd
import pickle
import re
from pathlib import Path


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Portugal Election Prediction",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# AUTHENTICATION CONFIG
# =========================================================

VALID_USERNAME = "admin"
VALID_PASSWORD = "admin@123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "theme" not in st.session_state:
    st.session_state.theme = "Light"


# =========================================================
# THEME / STYLING
#
# UI-only additions: color tokens + component styling.
# None of this touches the model, data, or prediction logic
# further down the file. Every color below is theme-aware —
# including the navbar and sidebar — so nothing is left
# hard-coded to one theme, and every interactive control gets
# an explicit background + text color pair so nothing renders
# as dark-on-dark or light-on-light.
# =========================================================

LIGHT_VARS = """
<style>
:root {
    --bg: #F6F5F1;
    --surface: #FFFFFF;
    --surface-alt: #FBFAF7;
    --ink: #1C2230;
    --ink-muted: #5B6472;
    --border: #E4E1D8;
    --navy: #1B2A4A;
    --accent: #B8433C;
    --accent-hover: #9E362F;
    --positive: #2D6A4F;
    --focus-ring: rgba(184, 67, 60, 0.18);

    /* Chrome = navbar + sidebar. Light in light mode, dark in dark mode. */
    --chrome-bg: #FFFFFF;
    --chrome-bg-alt: #EEF1F6;
    --chrome-text: #1B2A4A;
    --chrome-text-muted: #64708A;
    --chrome-border: #E4E1D8;
}
</style>
"""

DARK_VARS = """
<style>
:root {
    --bg: #0F1420;
    --surface: #171E2C;
    --surface-alt: #1D2536;
    --ink: #E7E9EC;
    --ink-muted: #9AA3B2;
    --border: #2A3346;
    --navy: #101828;
    --accent: #D9645C;
    --accent-hover: #C94F47;
    --positive: #4C9A7A;
    --focus-ring: rgba(217, 100, 92, 0.25);

    --chrome-bg: #0B111C;
    --chrome-bg-alt: #182238;
    --chrome-text: #E7E9EC;
    --chrome-text-muted: #9AA3B2;
    --chrome-border: #262E40;
}
</style>
"""

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background-color: var(--bg);
    color: var(--ink);
    transition: background-color 0.2s ease, color 0.2s ease;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

/* Base text color for every label / caption / paragraph in the main area.
   Fixes labels that used to stay a fixed dark color in dark mode. */
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] span,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
.stMarkdown, .stCaption {
    color: var(--ink) !important;
}

/* ---------- Top navbar (theme-aware) ---------- */
.app-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.6rem;
    background-color: var(--chrome-bg);
    color: var(--chrome-text);
    border: 1px solid var(--chrome-border);
    padding: 0.9rem 1.6rem;
    border-radius: 10px;
    margin-bottom: 1.6rem;
}
.app-navbar-left { display: flex; align-items: center; gap: 0.6rem; }
.app-navbar-emblem { font-size: 1.4rem; }
.app-navbar-title {
    font-family: 'Fraunces', serif;
    font-size: 1.15rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    color: var(--chrome-text) !important;
}
.app-navbar-right { display: flex; align-items: center; gap: 1rem; font-size: 0.85rem; flex-wrap: wrap; }
.app-navbar-page {
    padding: 0.25rem 0.7rem;
    background-color: var(--chrome-bg-alt);
    border-radius: 6px;
    color: var(--chrome-text) !important;
}
.app-navbar-user { font-weight: 500; color: var(--chrome-text) !important; }

/* ---------- Sidebar (theme-aware) ---------- */
section[data-testid="stSidebar"] {
    background-color: var(--chrome-bg);
    border-right: 1px solid var(--chrome-border);
}
section[data-testid="stSidebar"] * { color: var(--chrome-text) !important; }
section[data-testid="stSidebar"] hr { border-color: var(--chrome-border); }
.sidebar-brand { font-family: 'Fraunces', serif; font-size: 1.05rem; font-weight: 600; padding: 0.2rem 0 0.6rem 0; }
.sidebar-caption { font-size: 0.78rem; color: var(--chrome-text-muted) !important; margin-top: -0.6rem; }

/* ---------- Headings ---------- */
h1, h2, h3, h4 { font-family: 'Fraunces', serif; color: var(--ink) !important; }

/* ---------- Buttons ---------- */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--accent);
    color: #FFFFFF !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.55rem 1.2rem;
    transition: background-color 0.15s ease, transform 0.1s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--accent-hover);
    color: #FFFFFF !important;
    transform: translateY(-1px);
}
.stButton > button:active, .stFormSubmitButton > button:active { transform: translateY(0); }

/* ---------- Text / number / password inputs ----------
   Targeted directly at the real <input> elements so they always
   get an explicit background + text pair, regardless of theme. */
input[type="text"], input[type="password"], input[type="number"], textarea {
    background-color: var(--surface) !important;
    color: var(--ink) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
input[type="text"]:focus, input[type="password"]:focus, input[type="number"]:focus, textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--focus-ring);
}
[data-testid="stNumberInput"] button { background-color: var(--surface-alt) !important; color: var(--ink) !important; border-color: var(--border) !important; }

/* ---------- Select boxes (closed control + open dropdown) ---------- */
div[data-baseweb="select"] > div {
    background-color: var(--surface) !important;
    color: var(--ink) !important;
    border-color: var(--border) !important;
    border-radius: 6px !important;
}
div[data-baseweb="select"] * { color: var(--ink) !important; }
div[data-baseweb="popover"] { background-color: var(--surface) !important; }
ul[data-baseweb="menu"], ul[role="listbox"] { background-color: var(--surface) !important; }
li[role="option"] { color: var(--ink) !important; background-color: var(--surface) !important; }
li[role="option"]:hover, li[aria-selected="true"] { background-color: var(--surface-alt) !important; }

/* ---------- Radio / toggle / checkbox labels in the main area ---------- */
[data-testid="stAppViewContainer"] [data-testid="stRadio"] label p,
[data-testid="stAppViewContainer"] [data-testid="stCheckbox"] label p,
[data-testid="stAppViewContainer"] [data-testid="stToggle"] label p {
    color: var(--ink) !important;
}

/* ---------- Expanders as cards ---------- */
details[data-testid="stExpander"] {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--navy);
    border-radius: 8px;
    margin-bottom: 1rem;
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
details[data-testid="stExpander"]:hover {
    border-left-color: var(--accent);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
}
details[data-testid="stExpander"] summary { font-weight: 600; color: var(--ink) !important; }
details[data-testid="stExpander"] [data-testid="stExpanderDetails"] { padding-top: 0.4rem; }

/* ---------- Metric ---------- */
div[data-testid="stMetric"] {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-left: 4px solid var(--positive);
    border-radius: 8px;
    padding: 1rem 1.2rem;
}
div[data-testid="stMetricValue"] { font-family: 'Fraunces', serif; color: var(--navy) !important; }
div[data-testid="stMetricLabel"] { color: var(--ink-muted) !important; }

/* ---------- Alerts + dataframe ----------
   Kept on a fixed light surface on purpose: their internal
   text color isn't theme-aware, so pairing it with a fixed
   light background keeps it legible in both modes. */
div[data-testid="stAlert"] { border-radius: 8px; }
div[data-testid="stDataFrame"] {
    background-color: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
}

/* ---------- Login ---------- */
.login-card { text-align: center; padding: 1.4rem 0 0.6rem 0; }
.login-emblem { font-size: 2.4rem; }
.login-title { font-family: 'Fraunces', serif; font-size: 1.5rem; margin: 0.4rem 0 0.1rem 0; color: var(--ink) !important; }
.login-subtitle { color: var(--ink-muted) !important; font-size: 0.92rem; margin-bottom: 1.2rem; }
.login-footnote { text-align: center; color: var(--ink-muted) !important; font-size: 0.78rem; margin-top: 0.8rem; }
div[data-testid="stForm"] {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.6rem 1.8rem;
}

hr { border-color: var(--border); }

/* ---------- Responsive tweaks ---------- */
@media (max-width: 768px) {
    .app-navbar { flex-direction: column; align-items: flex-start; padding: 0.8rem 1.1rem; }
    .app-navbar-right { width: 100%; justify-content: space-between; }
    div[data-testid="stForm"] { padding: 1.2rem 1rem; }
    .login-card { padding: 1rem 0 0.3rem 0; }
}
</style>
"""


def inject_theme(theme: str) -> None:
    st.markdown(DARK_VARS if theme == "Dark" else LIGHT_VARS, unsafe_allow_html=True)
    st.markdown(BASE_CSS, unsafe_allow_html=True)


inject_theme(st.session_state.theme)


# =========================================================
# LOGIN GATE
# =========================================================

def render_login() -> None:
    left, center, right = st.columns([1, 1.1, 1])
    with center:
        st.markdown(
            """
            <div class="login-card">
                <div class="login-emblem">🗳️</div>
                <div class="login-title">Portugal Election Prediction</div>
                <div class="login-subtitle">Sign in to access the dashboard</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if username == VALID_USERNAME and password == VALID_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        st.markdown('<div class="login-footnote">Authorized personnel only</div>', unsafe_allow_html=True)


if not st.session_state.authenticated:
    render_login()
    st.stop()


# =========================================================
# SIDEBAR (navigation + theme toggle + session controls)
# =========================================================

with st.sidebar:
    st.markdown('<div class="sidebar-brand">🗳️ Election Predictor</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-caption">Signed in as {st.session_state.username}</div>', unsafe_allow_html=True)
    st.markdown("---")

    nav_choice = st.radio(
        "Navigate",
        ["📊 Prediction Dashboard", "ℹ️ Model Overview"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Appearance**")
    dark_mode = st.toggle("🌙 Dark mode", value=(st.session_state.theme == "Dark"))
    desired_theme = "Dark" if dark_mode else "Light"
    if desired_theme != st.session_state.theme:
        st.session_state.theme = desired_theme
        st.rerun()

    st.markdown("---")
    if st.button("🚪 Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()


# =========================================================
# TOP NAVBAR
# =========================================================

active_page_label = "Prediction Dashboard" if nav_choice.startswith("📊") else "Model Overview"

st.markdown(
    f"""
    <div class="app-navbar">
        <div class="app-navbar-left">
            <span class="app-navbar-emblem">🗳️</span>
            <span class="app-navbar-title">Portugal Election Prediction</span>
        </div>
        <div class="app-navbar-right">
            <span class="app-navbar-page">{active_page_label}</span>
            <span class="app-navbar-user">👤 {st.session_state.username.capitalize()}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "model"

MODEL_PATH = MODEL_DIR / "knn_boost_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
ENCODER_PATH = MODEL_DIR / "encoder.pkl"


# =========================================================
# LOAD MODEL + PREPROCESSORS
#
# These are three SEPARATE pickles, all produced from the
# same notebook run: the fitted StandardScaler, the fitted
# OneHotEncoder, and the fitted regressor. All three must
# come from the same training run or the columns/scaling
# won't line up with what the model expects.
# =========================================================

@st.cache_resource
def load_artifacts():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    with open(ENCODER_PATH, "rb") as f:
        encoder = pickle.load(f)
    return model, scaler, encoder


model, scaler, encoder = load_artifacts()

# Columns each preprocessor was fit on (sklearn stores this automatically
# when fit on a DataFrame) — avoids hard-coding the lists a second time.
numeric_columns = list(scaler.feature_names_in_)
cat_cols = list(encoder.feature_names_in_)


# =========================================================
# RAW FEATURE NAMES
# These are the raw input columns, BEFORE scaling/encoding.
# =========================================================

feature_names = [
    "territoryName",
    "Party",
    "totalMandates",
    "availableMandates",
    "numParishes",
    "numParishesApproved",
    "blankVotes",
    "nullVotes",
    "votersPercentage",
    "subscribedVoters",
    "totalVoters",
    "pre.blankVotes",
    "pre.nullVotes",
    "pre.votersPercentage",
    "pre.subscribedVoters",
    "pre.totalVoters",
    "Percentage",
    "validVotesPercentage",
    "Votes"
]


# =========================================================
# PULL VALID CATEGORIES DIRECTLY FROM THE FITTED ENCODER
#
# This is the key fix for the original bug: instead of
# hard-coding territory/party lists that can drift out of
# sync with what the model was actually trained on, we read
# the categories straight off the fitted OneHotEncoder.
# They are guaranteed to match (right spelling, right order,
# right punctuation e.g. "B.E." vs "BE").
# =========================================================

category_options = dict(zip(cat_cols, [list(c) for c in encoder.categories_]))
territory_options = category_options.get("territoryName", [])
party_options = category_options.get("Party", [])


# =========================================================
# NUMERIC DEFAULTS
# =========================================================

numeric_defaults = {
    "totalMandates": 10.0,
    "availableMandates": 10.0,
    "numParishes": 100.0,
    "numParishesApproved": 100.0,
    "blankVotes": 0.0,
    "nullVotes": 0.0,
    "votersPercentage": 50.0,
    "subscribedVoters": 10000.0,
    "totalVoters": 5000.0,
    "pre.blankVotes": 0.0,
    "pre.nullVotes": 0.0,
    "pre.votersPercentage": 50.0,
    "pre.subscribedVoters": 10000.0,
    "pre.totalVoters": 5000.0,
    "Percentage": 10.0,
    "validVotesPercentage": 10.0,
    "Votes": 500.0
}


# =========================================================
# DISPLAY-ONLY LABEL HELPER
#
# Cosmetic only: turns a raw column name like "pre.blankVotes"
# into "Previous Blank Votes" for the widget label. The raw
# `feature` string is still used untouched as the dict key
# (input_data[feature] = ...) and everywhere downstream, so the
# columns fed to the scaler/encoder/model are exactly the same
# as before — only what the user reads on screen changes.
# =========================================================

def humanize_label(raw: str) -> str:
    text = raw.replace("pre.", "Previous ")
    text = re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
    return text.title()


# =========================================================
# MODEL OVERVIEW PAGE (new, read-only — reuses the same
# already-loaded variables above; touches no prediction logic)
# =========================================================

if active_page_label == "Model Overview":
    st.subheader("Model Overview")
    st.caption("Read-only summary of the loaded model artifacts")

    col1, col2, col3 = st.columns(3, gap="large")
    col1.metric("Territories", len(territory_options))
    col2.metric("Parties", len(party_options))
    col3.metric("Input Features", len(feature_names))

    st.markdown("#### Numeric columns (scaled)")
    st.dataframe(pd.DataFrame({"column": numeric_columns}), use_container_width=True)

    st.markdown("#### Categorical columns (encoded)")
    st.dataframe(pd.DataFrame({"column": cat_cols}), use_container_width=True)

    with st.expander("Territories recognized by the model"):
        st.dataframe(pd.DataFrame({"territoryName": territory_options}), use_container_width=True)

    with st.expander("Parties recognized by the model"):
        st.dataframe(pd.DataFrame({"Party": party_options}), use_container_width=True)

    st.stop()


# =========================================================
# APPLICATION HEADER
# =========================================================

st.title("🗳️ Portugal Election Prediction")
st.caption("Machine Learning Powered Election Prediction System")
st.divider()


# =========================================================
# USER INPUT
# =========================================================

st.subheader("Enter Election Information")

input_data = {}


# =========================================================
# ELECTION INFORMATION
# =========================================================

with st.expander("🏛️ Election Information", expanded=True):

    col1, col2 = st.columns(2, gap="large")

    with col1:
        input_data["territoryName"] = st.selectbox(
            "Territory Name",
            options=territory_options,
            help="Territories recognized by the trained model."
        )

    with col2:
        input_data["Party"] = st.selectbox(
            "Political Party",
            options=party_options,
            help="Parties recognized by the trained model."
        )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        input_data["totalMandates"] = st.number_input(
            "Total Mandates",
            value=numeric_defaults["totalMandates"],
            min_value=0.0
        )

    with col2:
        input_data["availableMandates"] = st.number_input(
            "Available Mandates",
            value=numeric_defaults["availableMandates"],
            min_value=0.0
        )


# =========================================================
# PARISH INFORMATION
# =========================================================

with st.expander("🏘️ Parish Information"):

    col1, col2 = st.columns(2, gap="large")

    with col1:
        input_data["numParishes"] = st.number_input(
            "Number of Parishes",
            value=numeric_defaults["numParishes"],
            min_value=0.0
        )

    with col2:
        input_data["numParishesApproved"] = st.number_input(
            "Approved Parishes",
            value=numeric_defaults["numParishesApproved"],
            min_value=0.0
        )


# =========================================================
# CURRENT VOTING INFORMATION
# =========================================================

with st.expander("🗳️ Current Voting Information"):

    col1, col2 = st.columns(2, gap="large")

    current_features = [
        "blankVotes",
        "nullVotes",
        "votersPercentage",
        "subscribedVoters",
        "totalVoters"
    ]

    for index, feature in enumerate(current_features):
        column = col1 if index % 2 == 0 else col2
        with column:
            input_data[feature] = st.number_input(
                humanize_label(feature),
                value=numeric_defaults[feature],
                min_value=0.0
            )


# =========================================================
# PREVIOUS ELECTION INFORMATION
# =========================================================

with st.expander("📊 Previous Election Information"):

    col1, col2 = st.columns(2, gap="large")

    previous_features = [
        "pre.blankVotes",
        "pre.nullVotes",
        "pre.votersPercentage",
        "pre.subscribedVoters",
        "pre.totalVoters"
    ]

    for index, feature in enumerate(previous_features):
        column = col1 if index % 2 == 0 else col2
        with column:
            input_data[feature] = st.number_input(
                humanize_label(feature),
                value=numeric_defaults[feature],
                min_value=0.0
            )


# =========================================================
# PARTY VOTING INFORMATION
# =========================================================

with st.expander("📈 Party Voting Information"):

    col1, col2 = st.columns(2, gap="large")

    party_features = [
        "Percentage",
        "validVotesPercentage",
        "Votes"
    ]

    for index, feature in enumerate(party_features):
        column = col1 if index % 2 == 0 else col2
        with column:
            input_data[feature] = st.number_input(
                humanize_label(feature),
                value=numeric_defaults[feature],
                min_value=0.0
            )


# =========================================================
# PREDICTION
# =========================================================

st.divider()

if st.button("🔮 Predict Final Mandates", use_container_width=True):

    try:
        # ---------------------------------------------
        # 1. Build the RAW input dataframe from user input
        # ---------------------------------------------
        raw_input = pd.DataFrame([input_data])[feature_names]

        with st.expander("🔍 View Raw Input Data"):
            st.dataframe(raw_input, use_container_width=True)

        # ---------------------------------------------
        # 2. Scale numeric columns using the SAME fitted
        #    scaler from training (transform, not fit_transform)
        # ---------------------------------------------
        processed_input = raw_input.copy()
        processed_input[numeric_columns] = scaler.transform(
            raw_input[numeric_columns]
        )

        # ---------------------------------------------
        # 3. One-hot encode categorical columns using the
        #    SAME fitted encoder from training
        # ---------------------------------------------
        encoded_array = encoder.transform(raw_input[cat_cols])
        encoded_df = pd.DataFrame(
            encoded_array,
            columns=encoder.get_feature_names_out(cat_cols),
            index=raw_input.index
        )

        # ---------------------------------------------
        # 4. Combine, dropping the original raw categorical
        #    columns — mirrors exactly what the notebook did:
        #    X = X.drop(columns=cat_cols); X = pd.concat([X, encoded_df])
        # ---------------------------------------------
        processed_input = processed_input.drop(columns=cat_cols)
        processed_input = pd.concat([processed_input, encoded_df], axis=1)

        with st.expander("⚙️ View Preprocessed Model Input"):
            st.dataframe(processed_input, use_container_width=True)

        # ---------------------------------------------
        # 5. Predict
        # ---------------------------------------------
        prediction = model.predict(processed_input)
        predicted_mandates = prediction[0]

        st.success("Prediction completed successfully!")

        rounded_mandates = max(0, round(predicted_mandates))

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric(
                label="Predicted Final Mandates",
                value=f"{rounded_mandates}"
            )
            st.caption(f"Raw model output: {predicted_mandates:.2f}")

    except Exception as error:
        st.error(f"Prediction Error: {error}")