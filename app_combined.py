import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime
import pytesseract
from PIL import Image
import re

# Page setup
st.set_page_config(page_title="Uber Go", layout="centered")
st.title("Uber Go")

# ------------------ PASSCODE PROTECTION ------------------
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    code = st.text_input("Enter passcode to unlock:", type="password")
    if code == "1305":
        st.session_state.unlocked = True
        st.success("Access granted. You can now continue.")
        st.experimental_rerun()
    else:
        st.stop()

# ------------------ GOOGLE SHEETS SETUP ------------------
gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")

credentials = service_account.Credentials.from_service_account_info(
    gcp_info,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

gc = gspread.authorize(credentials)
SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

# ------------------ SHIFT LOGIC ------------------
if "shift_started" not in st.session_state:
    st.session_state.shift_started = False

if not st.session_state.shift_started:
    st.subheader("Start Shift")
    with st.form("start_shift_form"):
        start_date = st.date_input("Date", value=datetime.today())
        start_time = st.time_input("Start Time")
        start_odo = st.number_input("Start Odometer", min_value=0, step=1)
        submitted = st.form_submit_button("Submit Start")
        if submitted:
            st.session_state.start_datetime = datetime.combine(start_date, start_time)
            st.session_state.start_odo = start_odo
            st.session_state.shift_started = True
            st.success("Shift started.")
            st.experimental_rerun()
else:
    st.subheader("End Shift")
    with st.form("end_shift_form"):
        end_date = st.date_input("Date", value=datetime.today(), key="end_date")
        end_time = st.time_input("End Time", key="end_time")
        end_odo = st.number_input("End Odometer", min_value=0, step=1)
        uploaded_file = st.file_uploader("Upload Uber screenshot (optional)", type=["png", "jpg", "jpeg"])
        ocr_text = ""
        parsed_earnings = ""

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            ocr_text = pytesseract.image_to_string(image)
            st.text_area("OCR Result", ocr_text, height=150)
            match = re.search(r"NZ\\$([0-9]+(?:\\.[0-9]{2})?)", ocr_text)
            if not match:
                match = re.search(r"NZ\\?\\$?\\s*([0-9]+(?:\\.[0-9]{2})?)", ocr_text)
            if match:
                parsed_earnings = match.group(1)

        earnings = st.text_input("Gross Earnings", value=parsed_earnings)

        submitted = st.form_submit_button("Submit End")
        if submitted:
            end_datetime = datetime.combine(end_date, end_time)
            duration = (end_datetime - st.session_state.start_datetime).total_seconds()
            online_hours = int(duration // 3600)
            online_minutes = int((duration % 3600) // 60)

            row = [
                st.session_state.start_datetime.strftime("%H:%M"),
                st.session_state.start_odo,
                end_time.strftime("%H:%M"),
                end_odo,
                st.session_state.start_datetime.strftime("%d/%m/%Y"),
                datetime.now().isoformat(),
                earnings,
                "", "", "", "", "", "", "", "",  # Additional fields
                end_odo - st.session_state.start_odo,
                online_hours,
                online_minutes,
                ocr_text if uploaded_file else "",
                "Uber"
            ]
            worksheet.append_row(row)
            st.success("Shift logged.")
            st.session_state.shift_started = False
            st.experimental_rerun()

st.markdown("---")
st.caption("Built with ❤️ by Tom")
