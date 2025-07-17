import streamlit as st
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
from utils.sheets import connect_to_sheet, get_latest_odo

# ---- SETUP ----
st.set_page_config(page_title="Uber Go", layout="wide")
st.title("Uber Go")

SPREADSHEET_NAME = "Uber Go - Earnings Tracker"
shifts_sheet = connect_to_sheet(SPREADSHEET_NAME, "Shifts")

# ---- ROUTER ----
query_params = st.query_params
page = query_params.get("page", "Home")

# ---- MOCK STATS ----
WEEKLY_GOAL = 1000
EARNED = 450
PERCENT = int(EARNED / WEEKLY_GOAL * 100)

if page == "Home":
    st.subheader("New Shift")

    # Input fields
    col_date, col_time, col_odo = st.columns(3)
    with col_date:
        start_date = st.date_input("Date", value=date.today())
    with col_time:
        start_time = st.time_input("Start Time", value=datetime.now().time())
    with col_odo:
        start_odo = st.number_input("Odometer", value=get_latest_odo(shifts_sheet))

    if st.button("Submit Start Shift"):
        st.session_state.start_date = start_date
        st.session_state.start_time = start_time
        st.session_state.start_odo = start_odo
        st.success("Start shift saved in session.")

    st.markdown("---")
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
        end_time = st.time_input("End Time", value=datetime.now().time())
    with col2:
        end_date = st.date_input("Date", value=date.today())
    with col3:
        end_odo = st.number_input("Odometer", value=get_latest_odo(shifts_sheet))
    

    if st.button("Submit End Shift"):
        try:
            row = {
                "start_time": st.session_state.start_time.strftime("%H:%M"),
                "start_odo": st.session_state.start_odo,
                "end_time": end_time.strftime("%H:%M"),
                "end_odo": end_odo,
                "date": end_date.strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "mileage_estimate": end_odo - st.session_state.start_odo,
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
