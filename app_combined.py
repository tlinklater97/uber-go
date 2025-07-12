import streamlit as st
from datetime import datetime, date
import pytesseract
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
from utils.sheets import connect_to_sheet, get_latest_odo

# Constants
SPREADSHEET_NAME = "Uber Go - Earnings Tracker"
JSON_FILE = "ubergosync-684421f92830.json"

# Connect to sheets
shifts_sheet = connect_to_sheet(SPREADSHEET_NAME, "Shifts", JSON_FILE)

# Set page config
st.set_page_config(page_title="Uber Go", layout="wide")

# Page routing
query_params = st.query_params
page = query_params.get("page", "Home")

# Goal summary (mocked for now)
WEEKLY_GOAL = 1000
EARNED = 450
PERCENT = int(EARNED / WEEKLY_GOAL * 100)

if page == "Home":
    st.title("Uber Go")


    # New Shift Inputs
    st.subheader("New Shift")
    col_date, col_time, col_odo = st.columns(3)
    with col_date:
        start_date = st.date_input("Date", value=date.today(), key="start_date")
    with col_time:
        start_time = st.time_input("Start Time", value=datetime.now().time(), key="start_time")
    with col_odo:
        start_odo = st.number_input("Odometer", value=get_latest_odo(shifts_sheet), key="start_odo")

    if st.button("Submit Start Shift"):
        st.session_state["start_date"] = start_date
        st.session_state["start_time"] = start_time
        st.session_state["start_odo"] = start_odo
        st.success("Start shift saved in session.")

    st.markdown("---")

    # Navigation buttons
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("End Shift"):
            st.query_params["page"] = "End Shift"
            st.rerun()
    with colB:
        if st.button("Weekly Stats Upload"):
            st.query_params["page"] = "Weekly Upload"
            st.rerun()
    with colC:
        if st.button("Paste Uber Trips Table"):
            st.query_params["page"] = "Paste Uber Trips Table"
            st.rerun()

elif page == "End Shift":
    st.title("End Shift")
    col1, col2, col3 = st.columns(3)
    with col1:
        end_time = st.time_input("End Time", value=datetime.now().time(), key="end_time")
    with col2:
        end_odo = st.number_input("End Odometer", min_value=0, value=0, key="end_odo")
    with col3:
        end_date = st.date_input("Date", value=date.today(), key="end_date")

    if st.button("Submit End Shift"):
        try:
            row = {
                "start_time": st.session_state["start_time"].strftime("%H:%M"),
                "start_odo": st.session_state["start_odo"],
                "end_time": end_time.strftime("%H:%M"),
                "end_odo": end_odo,
                "date": end_date.strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "mileage_estimate": end_odo - st.session_state["start_odo"],
                "source": "manual"
            }
            shifts_sheet.append_row(list(row.values()))
            st.success("Shift logged successfully.")
            st.query_params["page"] = "Home"
            st.rerun()
        except Exception as e:
            st.error(f"Error saving shift: {e}")
    if st.button("Back"):
        st.query_params["page"] = "Home"
        st.rerun()