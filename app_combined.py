import streamlit as st
from datetime import datetime, date
import base64
import os
import pytz
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image
import pytesseract

# ---- CONFIG ----
SERVICE_ACCOUNT_FILE = "ubergosync-13d16bd466a9.json"
SPREADSHEET_NAME = "Uber Go - Earnings Tracker"
SHEET_TAB = "Shifts"

# ---- SHEET CONNECT ----
def connect_sheet():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_TAB)
    return sheet

# ---- FONT INJECTION ----
font_path = "fonts/FFClanProBold.TTF"
if os.path.exists(font_path):
    with open(font_path, "rb") as f:
        ttf_base64 = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(f"""
        <style>
        @font-face {{
            font-family: 'FFClanProBold';
            src: url(data:font/ttf;base64,{ttf_base64}) format('truetype');
        }}
        html, body {{
            font-family: 'FFClanProBold', sans-serif;
            background-color: #0e1117;
            color: #f5f5f5;
        }}
        .stApp {{ padding: 1rem; }}
        </style>
    """, unsafe_allow_html=True)

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Uber Go", layout="centered")
st.title("Uber Go – Shift Logger")

# ---- SESSION INIT ----
if "start_date" not in st.session_state:
    st.session_state.start_date = date.today()
    st.session_state.start_time = datetime.now().strftime("%H:%M")
    st.session_state.start_odo = 0

# ---- START SHIFT ----
st.subheader("Start Shift")
start_date = st.date_input("Date", value=st.session_state.start_date)
start_time = st.text_input("Start Time (HH:MM)", value=st.session_state.start_time)
start_odo = st.number_input("Start Odometer", step=1, value=st.session_state.start_odo)

if st.button("Save Start Shift"):
    st.session_state.start_date = start_date
    st.session_state.start_time = start_time
    st.session_state.start_odo = start_odo
    st.success("Start shift saved!")

# ---- END SHIFT ----
st.markdown("---")
st.subheader("End Shift")
end_time = st.text_input("End Time (HH:MM)")
end_odo = st.number_input("End Odometer", step=1)
image_file = st.file_uploader("Upload Earnings Screenshot", type=["png", "jpg", "jpeg"])

ocr_text = ""
gross = ""
net = ""
tips = ""
boosts = ""
promos = ""
trips = ""

if image_file:
    try:
        image = Image.open(image_file)
        ocr_text = pytesseract.image_to_string(image)

        # Try to parse total earnings
        import re
        earnings_match = re.search(r"Total earnings\s*\$?([0-9]+\.?[0-9]*)", ocr_text)
        if earnings_match:
            gross = earnings_match.group(1)
        else:
            st.warning("Could not extract total earnings from screenshot.")
    except Exception as e:
        st.error(f"OCR failed: {e}")

if st.button("Submit End Shift"):
    try:
        sheet = connect_sheet()
        tz = pytz.timezone("Pacific/Auckland")
        now = datetime.now(tz).isoformat()
        row = {
            "start_time": st.session_state.start_time,
            "start_odo": st.session_state.start_odo,
            "end_time": end_time,
            "end_odo": end_odo,
            "date": start_date.strftime("%Y-%m-%d"),
            "timestamp": now,
            "gross_earnings": gross,
            "net_earnings": net,
            "trips": trips,
            "tips": tips,
            "boosts": boosts,
            "promotions": promos,
            "ocr_text": ocr_text,
            "source": "auto"
        }
        sheet.append_row(list(row.values()))
        st.success("Shift submitted to Google Sheets!")
    except Exception as e:
        st.error(f"Google Sheets upload failed: {e}")
