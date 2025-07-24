import streamlit as st
from datetime import datetime, date
from PIL import Image
import pytesseract
import io
import gspread
from google.oauth2.service_account import Credentials

# Authenticate using Streamlit secrets
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
gc = gspread.authorize(creds)
sheet = gc.open("Uber Go - Earnings Tracker").worksheet("Shifts")

st.set_page_config(page_title="Uber Go", layout="centered", initial_sidebar_state="collapsed")
st.title("Uber Go")

# Initialize session state
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "start_odo" not in st.session_state:
    st.session_state.start_odo = None

st.subheader("Start Shift")
with st.form("start_shift_form"):
    start_time = st.time_input("Start Time", value=datetime.now().time())
    start_odo = st.number_input("Starting Odometer", min_value=0, step=1)
    submitted_start = st.form_submit_button("Start Shift")
    if submitted_start:
        st.session_state.start_time = start_time.strftime("%H:%M")
        st.session_state.start_odo = start_odo
        st.success("Shift started.")

st.subheader("End Shift")
with st.form("end_shift_form"):
    end_time = st.time_input("End Time", value=datetime.now().time())
    end_odo = st.number_input("Ending Odometer", min_value=0, step=1)
    uploaded_image = st.file_uploader("Upload Screenshot", type=["png", "jpg", "jpeg"])
    manual_date = st.date_input("Shift Date", value=date.today())
    submitted_end = st.form_submit_button("End Shift")

if submitted_end:
    timestamp = datetime.now().isoformat()
    ocr_text = ""
    gross = ""

    if uploaded_image:
        image = Image.open(uploaded_image)
        text = pytesseract.image_to_string(image)
        ocr_text = text

        # Extract gross earnings
        for line in text.splitlines():
            if "Total earnings" in line:
                try:
                    gross = float(line.split()[-1].replace("$", "").strip())
                    break
                except ValueError:
                    pass

    data = [
        st.session_state.start_time,
        st.session_state.start_odo,
        end_time.strftime("%H:%M"),
        end_odo,
        manual_date.strftime("%Y-%m-%d"),
        timestamp,
        gross,
        "",  # net earnings
        "",  # trips
        "",  # tips
        "",  # boosts
        "",  # promotions
        ocr_text,
        "auto"
    ]

    try:
        sheet.append_row(data)
        st.success("Shift data uploaded successfully.")
    except Exception as e:
        st.error(f"Google Sheets upload failed: {e}")
