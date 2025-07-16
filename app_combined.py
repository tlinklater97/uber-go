import streamlit as st
from datetime import datetime, date
import pytesseract
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
from utils.sheets import connect_to_sheet, get_latest_odo

# Constants
SPREADSHEET_NAME = "Uber Go - Earnings Tracker"
shifts_sheet = connect_to_sheet(SPREADSHEET_NAME, "Shifts")

# Page Setup
st.set_page_config(page_title="Uber Go", layout="wide")

# Page routing
query_params = st.query_params
page = query_params.get("page", "Home")

# Goal summary (example values)
WEEKLY_GOAL = 1000
EARNED = 450
PERCENT = int(EARNED / WEEKLY_GOAL * 100)

# --- HOME PAGE ---
if page == "Home":
    st.title("Uber Go")

    st.subheader("New Shift")
    col_date, col_time, col_odo = st.columns(3)
    with col_date:
        start_date = st.date_input("Date", value=date.today())
    with col_time:
        start_time = st.time_input("Start Time", value=datetime.now().time())
    with col_odo:
        start_odo = st.number_input("Odometer", min_value=0, value=get_latest_odo(shifts_sheet))

    if st.button("Submit Start Shift"):
        st.session_state["start_date"] = start_date
        st.session_state["start_time"] = start_time
        st.session_state["start_odo"] = start_odo
        st.success("Start shift saved in session.")

    st.markdown("---")
    col
