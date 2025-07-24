import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Uber Go", layout="centered", page_icon="🚗")
st.title("Uber Go")

# Persistent session state for long idle durations
if "shift_started" not in st.session_state:
    st.session_state.shift_started = False

# Start Shift Screen
if not st.session_state.shift_started:
    st.header("Start Shift")
    with st.form("start_shift_form"):
        col1, col2 = st.columns(2)
        with col1:
            shift_date = st.date_input("Date", value=datetime.now().date(), key="start_date")
        with col2:
            shift_time = st.time_input("Time", value=datetime.now().time(), key="start_time")
        start_odo = st.number_input("Odometer", min_value=0, step=1, key="start_odo")
        submitted = st.form_submit_button("Submit Start")

        if submitted:
            st.session_state.shift_started = True
            st.session_state.shift_date = shift_date.strftime("%d/%m/%Y")
            st.session_state.shift_time = shift_time.strftime("%H:%M")
            st.session_state.start_odo = start_odo
            st.success("Start shift recorded. Leave this window open.")
            st.experimental_rerun()

# End Shift Screen
else:
    st.header("End Shift")
    with st.form("end_shift_form"):
        col1, col2 = st.columns(2)
        with col1:
            end_date = st.date_input("Date", value=datetime.now().date(), key="end_date")
        with col2:
            end_time = st.time_input("Time", value=datetime.now().time(), key="end_time")
        end_odo = st.number_input("Odometer", min_value=0, step=1, key="end_odo")
        uploaded_file = st.file_uploader("Upload Uber screenshot (optional)", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Submit End")

        if submitted:
            shift_data = {
                "Start Date": st.session_state.shift_date,
                "Start Time": st.session_state.shift_time,
                "Start Odometer": st.session_state.start_odo,
                "End Date": end_date.strftime("%d/%m/%Y"),
                "End Time": end_time.strftime("%H:%M"),
                "End Odometer": end_odo,
                "Source": "Uber"
            }
            st.success("Shift logged:")
            st.json(shift_data)  # Placeholder for actual Google Sheets write
            st.session_state.shift_started = False
            st.experimental_rerun()
