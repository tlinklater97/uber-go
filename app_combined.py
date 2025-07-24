import streamlit as st
from datetime import datetime
import pytz
import gspread
from google.oauth2.service_account import Credentials
import pytesseract
from PIL import Image
import io

# === CONFIG ===
SERVICE_ACCOUNT_FILE = "ubergosync-13d16bd466a9.json"
SPREADSHEET_NAME = "Uber Go - Earnings Tracker"
SHEET_TAB = "Shifts"

# === SETUP GOOGLE SHEETS ===
def get_sheet():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    return client.open(SPREADSHEET_NAME).worksheet(SHEET_TAB)

# === TIME + DATE UTILS ===
def get_nz_now():
    return datetime.now(pytz.timezone("Pacific/Auckland"))

st.set_page_config(page_title="Uber Go", layout="centered")
st.markdown("""
    <style>
    body, .stApp {
        background-color: #121212;
        color: #fff;
    }
    input, textarea {
        background-color: #1e1e1e !important;
        color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚗 Uber Go")

# === SESSION STATE ===
if "shift_data" not in st.session_state:
    st.session_state.shift_data = {}

# === START SHIFT ===
st.subheader("Start Shift")
with st.form("start_shift"):
    start_time = st.time_input("Start Time", value=get_nz_now().time())
    start_date = st.date_input("Date", value=get_nz_now().date())
    start_odo = st.number_input("Start Odometer", min_value=0, step=1)
    start_submit = st.form_submit_button("Start Shift")
    if start_submit:
        st.session_state.shift_data = {
            "start_time": start_time.strftime("%H:%M"),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "start_odo": start_odo
        }
        st.success("Shift started!")

# === END SHIFT ===
st.subheader("End Shift")
if st.session_state.shift_data:
    with st.form("end_shift"):
        end_time = st.time_input("End Time", value=get_nz_now().time())
        end_odo = st.number_input("End Odometer", min_value=0, step=1)
        ocr_img = st.file_uploader("Upload Uber Earnings Screenshot", type=["jpg", "png"])
        end_submit = st.form_submit_button("End Shift")

        if end_submit:
            ocr_text = ""
            gross = ""
            if ocr_img:
                try:
                    img = Image.open(io.BytesIO(ocr_img.read()))
                    ocr_text = pytesseract.image_to_string(img)
                    if "Total earnings" in ocr_text:
                        match = [line for line in ocr_text.splitlines() if "$" in line or "NZ$" in line]
                        if match:
                            raw_val = match[-1].replace("NZ$", "").replace("$", "").strip()
                            gross = float(raw_val)
                except Exception as e:
                    st.warning(f"OCR failed: {e}")

            row = [
                st.session_state.shift_data.get("start_time", ""),
                st.session_state.shift_data.get("start_odo", ""),
                end_time.strftime("%H:%M"),
                end_odo,
                st.session_state.shift_data.get("start_date", ""),
                get_nz_now().isoformat(),
                gross,
                "", "", "", "", "", ocr_text[:500], "auto"
            ]

            try:
                sheet = get_sheet()
                sheet.append_row(row, value_input_option="USER_ENTERED")
                st.success("Shift logged to Google Sheets!")
            except Exception as e:
                st.error(f"Google Sheets upload failed: {e}")
                st.json(dict(zip([
                    "start_time", "start_odo", "end_time", "end_odo", "date", "timestamp", 
                    "gross_earnings", "net_earnings", "trips", "tips", "boosts", "promotions", "ocr_text", "source"
                ], row)))
else:
    st.info("Start a shift first to enable end shift logging.")
