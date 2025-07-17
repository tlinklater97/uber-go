import streamlit as st
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
from utils.sheets import connect_to_sheet, get_latest_odo
import base64
import os

# ---- FONT INJECTION ----
font_path = "fonts/FFClanProBold.TTF"
if not os.path.exists(font_path):
    st.markdown("""
        <style>
        html, body {
            background-color: #ff0033 !important;
            color: white !important;
            font-size: 24px !important;
            text-align: center !important;
            padding: 2em;
        }
        </style>
    """, unsafe_allow_html=True)
    st.error("FONT ERROR: `fonts/FFClanProBold.TTF` is missing.")
    st.stop()

with open(font_path, "rb") as f:
    ttf_base64 = base64.b64encode(f.read()).decode("utf-8")

# ---- DARK MODE STYLING ----
st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'FFClanProBold';
        src: url(data:font/ttf;base64,{ttf_base64}) format('truetype');
    }}
    html, body {{
        background-color: #0e1117;
        color: #f5f5f5;
        font-family: 'FFClanProBold', sans-serif;
    }}
    h1, h2, h3, .stTitle, .stHeader, .stSubheader {{
        color: #ffffff;
    }}
    .stTextInput > div > input,
    .stDateInput, .stNumberInput, .stTimeInput {{
        background-color: #262730;
        color: #ffffff;
    }}
    .stButton > button {{
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.5em 1.2em;
        font-size: 1.1em;
    }}
    input[type="password"] {{
        font-size: 24px;
        text-align: center;
    }}
    </style>
""", unsafe_allow_html=True)

# ---- SETUP ----
st.set_page_config(page_title="Uber Go", layout="wide")
st.title("Uber Go")

# ---- PIN LOGIN ----
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("Enter PIN to Access Uber Go")
    pin_input = st.text_input("Enter 4-digit PIN", type="password", max_chars=4, key="pin", input_type="number")

    if pin_input == "1305":
        st.session_state["authenticated"] = True
        st.rerun()
    elif pin_input:
        st.error("Incorrect PIN")
    st.stop()

# ---- SHEET SETUP ----
SPREADSHEET_NAME = "Uber Go - Earnings Tracker"
shifts_sheet = connect_to_sheet(SPREADSHEET_NAME, "Shifts")

# ---- PAGE ROUTER ----
query_params = st.query_params
page = query_params.get("page", "Home")

# ---- HOME PAGE ----
if page == "Home":
    st.subheader("Start New Shift")

    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("Date", value=date.today())
    with col2:
        start_time = st.time_input("Start Time", value=datetime.now().time())
    with col3:
        start_odo = st.number_input("Starting Odometer", value=get_latest_odo(shifts_sheet), step=1, format="%d")

    if st.button("Submit Start Shift"):
        st.session_state["start_date"] = start_date
        st.session_state["start_time"] = start_time
        st.session_state["start_odo"] = start_odo
        st.success("Start shift saved in session.")

    st.markdown("---")
    if st.button("Go to End Shift"):
        st.query_params["page"] = "End Shift"
        st.rerun()

# ---- END SHIFT PAGE ----
elif page == "End Shift":
    st.subheader("End Shift")

    col1, col2, col3 = st.columns(3)
    with col1:
        end_date = st.date_input("Date", value=date.today())
    with col2:
        end_time = st.time_input("End Time", value=datetime.now().time())
    with col3:
        end_odo = st.number_input("Ending Odometer", value=get_latest_odo(shifts_sheet), step=1, format="%d")

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

    if st.button("Back to Home"):
        st.query_params["page"] = "Home"
        st.rerun()
