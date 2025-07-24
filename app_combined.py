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
def get_current_time():
    return datetime.now(pytz.timezone("Pacific/Auckland"))

def get_today_date():
    return get_current_time().strftime("%Y-%m-%d")

def to_iso_timestamp():
    return get_current_time().isoformat()

# === DARK MODE SETUP ===
st.set_page_config(page_title="Uber Go", layout="centered")
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #121212;
        color: #fff;
    }
    input, textarea {
        background-color: #1e1e1e !important;
        color: #fff !important;
    }
    .css-1cpxqw2 {
        padding-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🚗 Uber Go")

# === SESSION STATE ===
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "start_odo" not in st.session_state:
    st.session_state.start_odo = None

# === START SHIFT ===
st.subheader("Start Shift")
with st.form("start_shift_form"):
    start_time = st.time_input("Start Time", value=datetime.now().time())
    start_odo = st.number_input("Start Odometer", min_value=0, step=1)
    submitted_start = st.form_submit_button("Start Shift")

    if submitted_start:
        st.session_state.start_time = start_time
        st.session_state.start_odo = start_odo
        st.success(f"Shift started at {start_time} with odo {start_odo}")

# === END SHIFT ===
st.subheader("End Shift")
with st.form("end_shift_form"):
    end_time = st.time_input("End Time", value=datetime.now().time())
    end_odo = st.number_input("End Odometer", min_value=0, step=1)
    date_input = st.date_input("Date", value=datetime.today())
    ocr_img = st.file_uploader("Upload Screenshot for Earnings (optional)", type=["jpg", "png"])
    source_type = st.radio("Entry Method", ["manual", "ocr", "manual + ocr"])
    submit_end = st.form_submit_button("End Shift")

    if submit_end:
        # === Parse OCR Text if given ===
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

        # === Build Row ===
        row = [
            st.session_state.start_time.strftime("%H:%M") if st.session_state.start_time else "",
            st.session_state.start_odo,
            end_time.strftime("%H:%M"),
            end_odo,
            date_input.strftime("%Y-%m-%d"),
            to_iso_timestamp(),
            gross if source_type in ["ocr", "manual + ocr"] else "",
            "",  # net_earnings
            "",  # trips
            "",  # tips
            "",  # boosts
            "",  # promotions
            ocr_text[:500],  # truncated for length
            source_type
        ]

        try:
            sheet = get_sheet()
            sheet.append_row(row, value_input_option="USER_ENTERED")
            st.success("Shift logged to Google Sheets!")
        except Exception as e:
            st.error(f"Error uploading to Google Sheets: {e}")
            st.text("Backup data:")
            st.json(dict(zip([
                "start_time", "start_odo", "end_time", "end_odo", "date", "timestamp", 
                "gross_earnings", "net_earnings", "trips", "tips", "boosts", 
                "promotions", "ocr_text", "source"
            ], row)))
