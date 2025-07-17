import streamlit as st
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
from utils.sheets import connect_to_sheet, get_latest_odo
import base64


# ---- FONT INJECTION ----
with open("fonts/FFClanProBold.TTF", "rb") as f:
    ttf_base64 = base64.b64encode(f.read()).decode("utf-8")


st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'FFClanProBold';
        src: url(data:font/ttf;base64,{ttf_base64}) format('truetype');
    }}
    html, body, [class*="css"] {{
        font-family: 'FFClanProBold', sans-serif;
    }}
    </style>
""", unsafe_allow_html=True)

# ---- SETUP ----
st.set_page_config(page_title="Uber Go", layout="wide")
st.title("Uber Go")

SPREADSHEET_NAME = "Uber Go - Earnings Tracker"
shifts_sheet = connect_to_sheet(SPREADSHEET_NAME, "Shifts")
# ---- AUTHENTICATION GATE ----
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Enter PIN to Access Uber Go")
    pin_input = st.text_input("Enter 4-digit PIN", type="password", max_chars=4)

    # Optional: numpad buttons (for mobile UX)
    cols = st.columns(3)
    for i in range(1, 10):
        if cols[(i - 1) % 3].button(str(i)):
            st.session_state["pin_input"] = st.session_state.get("pin_input", "") + str(i)
    if st.columns(3)[1].button("0"):
        st.session_state["pin_input"] = st.session_state.get("pin_input", "") + "0"

    # Clear and submit
    col_clear, col_enter = st.columns([1, 1])
    if col_clear.button("Clear"):
        st.session_state["pin_input"] = ""
    if col_enter.button("Enter"):
        if st.session_state.get("pin_input") == "1305" or pin_input == "1305":
            st.session_state["authenticated"] = True
            st.experimental_rerun()
        else:
            st.error("Incorrect PIN")

    # Show current input
    if "pin_input" in st.session_state:
        st.write("Entered:", "•" * len(st.session_state["pin_input"]))

    st.stop()
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
        end_date = st.date_input("Date", value=date.today())
    with col2:
        end_time = st.time_input("End Time", value=datetime.now().time())
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
