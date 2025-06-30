import streamlit as st
from datetime import datetime

# === Streamlit Config ===
st.set_page_config(page_title="Uber Go", layout="centered", initial_sidebar_state="collapsed")

# === Global Styles for Dark Mode + Fonts ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0e1117;
    color: #ffffff !important;
    font-size: 14px; /* Smaller font like mockup */
}

.stApp {
    background-color: #0e1117;
    padding: 1rem;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    color: #ffffff !important;
}

/* Inputs + Containers */
section, .stTextInput, .stNumberInput, .stFileUploader, .stTimeInput {
    background-color: #1c1f26;
    border-radius: 16px !important;
    padding: 12px;
    border: 1px solid #ffffff !important;
    color: #ffffff !important;
}

input, textarea, select {
    background-color: #0e1117 !important;
    color: white !important;
    border: none !important;
    outline: none !important;
}

/* File Uploader */
.stFileUploader > label {
    border: 2px dashed #ffffff !important;
    padding: 24px;
    border-radius: 12px;
    display: block;
    text-align: center;
    color: #ffffff !important;
}

/* Progress bar color */
.stProgress > div > div {
    background-color: #3b82f6 !important;
}

/* Button style */
.stButton button {
    background-color: #1f2937;
    color: white;
    font-weight: 600;
    border-radius: 12px;
    padding: 0.75rem 1.25rem;
    border: 1px solid #ffffff;
}

/* Dashboard button at bottom */
.center-button {
    text-align: center;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


# === App UI ===
st.title("Uber Go")

# === Week Goal Display ===
with st.container():
    st.subheader("Week Goal: $850")
    st.progress(0.49)
    st.markdown("**Earned So Far:** $420")
    st.markdown("**Remaining:** $430")

# === Add Shift ===
with st.container():
    st.subheader("Add Shift")
    start_time = st.time_input("Start Time", value=datetime.now().time())
    end_time = st.time_input("End Time")
    start_odo = st.number_input("Start Mileage (km)", min_value=0)
    end_odo = st.number_input("End Mileage (km)", min_value=0)

# === Upload Earnings ===
with st.container():
    st.subheader("Upload Earnings")
    selected_service = st.radio(
    "Service",
    options=["Uber", "DoorDash"],
    horizontal=True,
    index=0
)
    st.file_uploader("Upload Screenshot", type=["jpg", "jpeg", "png"], key="earnings")

# === Hnry Payout ===
with st.container():
    st.subheader("Hnry Payout")
    st.file_uploader("Upload File", type=["pdf", "jpg", "jpeg", "png"], key="hnry")

# === Dashboard Button ===
st.markdown("""
<div class="center-button">
    <button style="font-size: 1.2rem; padding: 0.8rem 2rem; border-radius: 12px; background-color: #1c1f26; color: white; border: 1px solid #333;">
        Dashboard
    </button>
</div>
""", unsafe_allow_html=True)
