import streamlit as st
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
from utils.sheets import connect_to_sheet, get_latest_odo
from PIL import Image
import pytesseract
import io
import base64
import os

# ---- FONT & THEME ----
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
            overflow: hidden;
        }}
        .stApp {{ padding: 0 !important; }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.error("Missing font file: fonts/FFClanProBold.TTF")
    st.stop()

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Uber Go", layout="centered")

# ---- GOOGLE SHEETS ----
SPREADSHEET_NAME = "Uber Go - Earnings Tracker"
shifts_sheet = connect_to_sheet(SPREADSHEET_NAME, "Shifts")

# ---- AUTH (PIN) ----
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("""
        <style>
        .centered-box {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            text-align: center;
            background-color: #0e1117;
            color: white;
        }
        input[type="password"] {
            font-size: 32px !important;
            text-align: center !important;
            border-radius: 8px !important;
        }
        </style>
        <div class="centered-box">
    """, unsafe_allow_html=True)

    st.title("Enter PIN to Access Uber Go")
    pin_input = st.text_input("Enter 4-digit PIN", type="password", max_chars=4)

    st.markdown("</div>", unsafe_allow_html=True)

    if pin_input == "1305":
        st.session_state["authenticated"] = True
        st.rerun()
    elif len(pin_input) == 4:
        st.error("Incorrect PIN")
    st.stop()

# ---- MAIN APP ----
st.title("Uber Go")

page = st.radio("Choose Page", ["Start Shift", "End Shift"], horizontal=True)

# ---- START SHIFT ----
if page == "Start Shift":
    st.subheader("Start Shift")

    start_date = st.date_input("Date", value=date.today())
    start_time = st.time_input("Start Time", value=datetime.now().time())
    start_odo = st.number_input("Odometer", value=get_latest_odo(shifts_sheet), step=1, format="%d")

    if st.button("Submit Start"):
        st.session_state.start_date = start_date
        st.session_state.start_time = start_time
        st.session_state.start_odo = start_odo
        st.success("Start shift saved.")

# ---- END SHIFT ----
elif page == "End Shift":
    st.subheader("End Shift")

    end_date = st.date_input("Date", value=date.today())
    end_time = st.time_input("End Time", value=datetime.now().time())
    end_odo = st.number_input("Odometer", value=get_latest_odo(shifts_sheet), step=1, format="%d")

    uploaded_file = st.file_uploader("Upload Uber Earnings Screenshot", type=["png", "jpg", "jpeg"])
    ocr_text = ""

    if uploaded_file:
        image = Image.open(uploaded_file)
        ocr_text = pytesseract.image_to_string(image)

    if st.button("Submit End"):
        try:
            row = {
                "start_time": st.session_state.start_time.strftime("%H:%M"),
                "start_odo": st.session_state.start_odo,
                "end_time": end_time.strftime("%H:%M"),
                "end_odo": end_odo,
                "date": end_date.strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "mileage_estimate": end_odo - st.session_state.start_odo,
                "ocr_text": ocr_text,
                "source": "manual + ocr"
            }
            shifts_sheet.append_row(list(row.values()))
            st.success("Shift logged successfully.")
        except Exception as e:
            st.error(f"Error: {e}")
