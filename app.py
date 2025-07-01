import streamlit as st
from PIL import Image
import pytesseract
import gspread
import re
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials


import streamlit as st

st.write("Secrets keys available:", list(st.secrets.keys()))

# === Streamlit Page Config ===
st.set_page_config(page_title="Uber Go", layout="centered", initial_sidebar_state="collapsed")
st.title("🚗 Uber Go")

# === Google Sheets Auth via Streamlit Secrets ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)

# === Sheet Settings ===
SHEET_NAME = "Uber Go - Earnings Tracker"
TAB_NAME = "Shifts"
sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)

# === Session State Defaults ===
if "shift_start_time" not in st.session_state:
    st.session_state.shift_start_time = ""
if "shift_start_odo" not in st.session_state:
    st.session_state.shift_start_odo = ""

# === Start Shift Form ===
st.header("🟢 Start Shift")
with st.form("start_shift_form"):
    start_time = st.time_input("Start Time", value=datetime.now().time())
    start_odo = st.number_input("Starting Odometer", min_value=0, step=1, value=198655)
    submitted = st.form_submit_button("Start Shift")

    if submitted:
        st.session_state.shift_start_time = start_time.strftime("%H:%M")
        st.session_state.shift_start_odo = start_odo
        st.success("✅ Shift started!")

# === End Shift Form ===
st.header("🔴 End Shift")
with st.form("end_shift_form"):
    end_time = st.time_input("End Time", value=datetime.now().time())
    end_odo = st.number_input("Ending Odometer", min_value=0, step=1, value=int(st.session_state.shift_start_odo))
    image = st.file_uploader("Upload Earnings Screenshot", type=["jpg", "jpeg", "png"])
    submitted2 = st.form_submit_button("End Shift")

    if submitted2:
        earnings = ""
        if image:
            img = Image.open(image)
            raw_text = pytesseract.image_to_string(img)
            match = re.search(r"Total earnings[:\s]*\$?([0-9]+\.[0-9]{2})", raw_text)
            if match:
                earnings = float(match.group(1))
            else:
                st.warning("⚠️ Could not detect earnings from screenshot. Please check image quality.")

        shift_data = [
            str(datetime.now().date()),                   # Date
            st.session_state.shift_start_time,            # Start Time
            end_time.strftime("%H:%M"),                   # End Time
            st.session_state.shift_start_odo,             # Start ODO
            end_odo,                                      # End ODO
            earnings                                      # Earnings
        ]
        sheet.append_row(shift_data)
        st.success("✅ Shift submitted!")

# === Optional Debug Info ===
with st.expander("See raw session state"):
    st.write(st.session_state)
