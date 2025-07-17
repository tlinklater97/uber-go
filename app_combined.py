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

# ---- GLOBAL STYLING ----
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
        font-family: 'FFClanProBold', sans-serif;
        color: #ffffff;
    }}
    input[type="password"] {{
        font-size: 24px !important;
        text-align: center !important;
    }}
    </style>
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        const pinInput = document.querySelector('input[type="password"]');
        if (pinInput) {{
            pinInput.setAttribute("inputmode", "numeric");
            pinInput.setAttribute("pattern", "[0-9]*");
        }}
    }});
    </script>
""", unsafe_allow_html=True)

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Uber Go", layout="wide")

# ---- PIN AUTHENTICATION ----
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("Enter PIN to Access Uber Go")

    pin_input = st.text_input("Enter 4-digit PIN", type="password", max_chars=4)

    col_clear, col_enter = st.columns([1, 1])
    if col_clear.button("Clear"):
        st.session_state["pin_input"] = ""
    if col_enter.button("Enter"):
        if st.session_state.get("pin_input", "") == "1305" or pin_input == "1305":
            st.session_state["authenticated"] = True
            st.session_state.pop("pin_input", None)
            st.experimental_rerun()
        else:
            st.error("Incorrect PIN")

    if "pin_input" in st.session_state:
        st.write("Entered:", "•" * len(st.session_state["pin_input"]))

    st.stop()

# ---- MAIN APP ----
st.title("Uber Go")

SPREADSHEET_NAME = "Uber Go - Earnings Tracker"
shifts_sheet = connect_to_sheet(SPREADSHEET_NAME, "Shifts")

query_params = st.query_params
page = query_params.get("page", "Home")

if page == "Home":
    st.subheader("Start New Shift")

    start_date = st.date_input("Date", value=date.today())
    start_time = st.time_input("Start Time", value=datetime.now().time())
    start_odo = st.number_input("Starting Odometer", value=get_latest_odo(shifts_sheet), step=1, format="%d")

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
    st.subheader("End Shift")

    end_date = st.date_input("Date", value=date.today())
    end_time = st.time_input("End Time", value=datetime.now().time())
    end_odo = st.number_input("Ending Odometer", value=get_latest_odo(shifts_sheet), step=1, format="%d")

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

    if st.button("Back to Home"):
        st.query_params["page"] = "Home"
        st.rerun()
