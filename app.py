# Uber Go - Clean UI Rebuild (mobile-first, no-scroll home layout)

import streamlit as st
from datetime import datetime
from PIL import Image
import pytesseract
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# === Google Sheets Setup ===
def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    info = json.loads(st.secrets["gsheets"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    client = gspread.authorize(creds)
    return client

# === Sheet Config ===
SHEET_NAME = "Uber Go - Earnings Tracker"
TAB_NAME = "Shifts"

# === Layout Config ===
st.set_page_config(page_title="Uber Go", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
        color: #ffffff;
    }
    .stApp { padding: 1rem; }
    .section-box {
        background-color: #1c1f26;
        border-radius: 16px;
        padding: 12px;
        border: 1px solid #ffffff;
        margin-bottom: 12px;
    }
    .three-buttons {
        display: flex;
        justify-content: space-between;
    }
    .three-buttons button {
        flex: 1;
        margin: 0 4px;
        padding: 14px;
        border-radius: 12px;
        background-color: #1c1f26;
        border: 1px solid #ffffff;
        color: white;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# === Navigation ===
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to(page):
    st.session_state.page = page

# === HOME PAGE ===
if st.session_state.page == "home":
    st.title("Uber Go")

    # Graph + Stats button row
    col1, col2 = st.columns([4,1])
    with col1:
        st.line_chart({"This Week": [120, 240, 310, 420, 420, None, None]})
    with col2:
        st.button("📈 Stats", on_click=lambda: go_to("stats"))  # Placeholder for future stats page

    # Goal summary block
    st.markdown("**Goal:** $1000  \
                **Earned:** $420  \
                **On Track:** 42%")

    # New Shift section
    st.markdown("### New Shift")
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.time_input("Time", value=datetime.now().time(), label_visibility="collapsed")
    with col2:
        odo = st.number_input("ODO", value=198655, step=1, label_visibility="collapsed")

    if st.button("Submit Shift Start", use_container_width=True):
        client = connect_to_gsheet()
        sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)
        sheet.append_row([str(datetime.now().date()), str(start_time), odo, "START"])
        st.success("Start shift submitted!")

    # 3 button row
    st.markdown("###")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("End Shift"):
            go_to("end")
    with col2:
        st.empty()  # Spacer
    with col3:
        if st.button("Weekly Stats Upload"):
            go_to("weekly")

# === END SHIFT PAGE ===
elif st.session_state.page == "end":
    st.markdown("### End Shift")
    end_time = st.time_input("Time", value=datetime.now().time(), label_visibility="collapsed")
    odo_end = st.number_input("ODO", min_value=0, label_visibility="collapsed")
    image = st.file_uploader("Upload Uber screenshot", type=["jpg", "jpeg", "png"])

    if st.button("Submit End Shift", use_container_width=True):
        client = connect_to_gsheet()
        sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)
        sheet.append_row([str(datetime.now().date()), str(end_time), odo_end, "END"])
        st.success("End shift submitted!")
        go_to("home")

    if st.button("⬅ Back", type="secondary"):
        go_to("home")

# === WEEKLY STATS PAGE ===
elif st.session_state.page == "weekly":
    st.markdown("### Weekly Stats Upload")
    hnry = st.file_uploader("Upload Hnry Payout", type=["pdf", "jpg", "jpeg", "png"])
    uber_stats = st.file_uploader("Upload Uber Stats", type=["csv", "jpg", "jpeg", "png"])

    if st.button("Submit Weekly Data", use_container_width=True):
        client = connect_to_gsheet()
        sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)
        sheet.append_row([str(datetime.now().date()), "WEEKLY", "UPLOAD"])
        st.success("Weekly data submitted!")
        go_to("home")

    if st.button("⬅ Back", type="secondary"):
        go_to("home")
