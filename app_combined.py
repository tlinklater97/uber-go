import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime
from PIL import Image
import pytesseract
import io
import re

# --- Streamlit Page Config ---
st.set_page_config(page_title="Uber Go", layout="centered")

st.title("Uber Go")

# --- Passcode Lock ---
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    code = st.text_input("Enter passcode to unlock:", type="password")
    if code == "1305":
        st.session_state.unlocked = True
        st.success("Access granted. You can now continue.")
    else:
        st.stop()

# --- GCP Auth ---
gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")
credentials = service_account.Credentials.from_service_account_info(gcp_info)
gc = gspread.authorize(credentials)

# --- Sheet Setup ---
SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

# --- Start Shift ---
if "shift_started" not in st.session_state:
    st.session_state.shift_started = False

if not st.session_state.shift_started:
    st.subheader("Start Shift")
    with st.form("start_form"):
        start_date = st.date_input("Date", value=datetime.now())
        start_time = st.time_input("Start Time", value=datetime.now().time())
        start_odo = st.number_input("Start Odometer", min_value=0, step=1)
        start_submit = st.form_submit_button("Submit")
        if start_submit:
            st.session_state.shift_started = True
            st.session_state.start_date = start_date.strftime("%d/%m/%Y")
            st.session_state.start_time = start_time.strftime("%H:%M")
            st.session_state.start_odo = start_odo
            st.success("Shift started.")
else:
    st.subheader("End Shift")
    with st.form("end_form"):
        end_date = st.date_input("Date", value=datetime.now())
        end_time = st.time_input("End Time", value=datetime.now().time())
        end_odo = st.number_input("End Odometer", min_value=0, step=1)
        uploaded_file = st.file_uploader("Upload Uber screenshot", type=["png", "jpg", "jpeg"])

        parsed_earnings = ""
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            text = pytesseract.image_to_string(image)
            earnings_match = re.search(r"\$?(\d{2,5}\.\d{2})", text)
            if earnings_match:
                parsed_earnings = earnings_match.group(1)

        earnings = st.text_input("Gross Earnings", value=parsed_earnings)

        end_submit = st.form_submit_button("Submit")
        if end_submit:
            row = [
                st.session_state.start_time,
                st.session_state.start_odo,
                end_time.strftime("%H:%M"),
                end_odo,
                st.session_state.start_date,
                datetime.now().isoformat(),
                earnings,
                "",  # net_earnings
                "",  # trips
                "",  # tips
                "",  # boosts
                "",  # promotions
                "",  # adjustments
                "",  # cancellation_fees
                "",  # referrals
                end_odo - st.session_state.start_odo,
                "",  # online_hours
                "",  # online_minutes
                "",  # ocr_text
                "Uber"
            ]
            worksheet.append_row(row)
            st.success("Shift logged.")
            st.session_state.shift_started = False  # reset for next use

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ by Tom")
