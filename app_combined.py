import streamlit as st
from datetime import datetime, date
import base64
import os
import pytesseract
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials

# -------------------------
# FONT + DARK MODE STYLING
# -------------------------
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
            overflow-x: hidden;
        }}
        .stApp {{ padding: 0 !important; }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.warning("Missing font file: fonts/FFClanProBold.TTF")

# --------------------
# GOOGLE SHEETS SETUP
# --------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_NAME = "Uber Go - Earnings Tracker"

creds = Credentials.from_service_account_info(
    st.secrets["google_service_account"], scopes=SCOPES
)
client = gspread.authorize(creds)
shifts_sheet = client.open(SPREADSHEET_NAME).worksheet("Shifts")

# ------------------
# AUTHENTICATION PIN
# ------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
        <style>
        .centered-box {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #0e1117;
        }
        input[type="password"] {
            font-size: 32px;
            text-align: center;
            border-radius: 8px;
        }
        </style>
        <div class="centered-box">
    """, unsafe_allow_html=True)

    st.title("Enter PIN to Access Uber Go")
    pin_input = st.text_input("Enter 4-digit PIN", type="password", max_chars=4, key="pin")

    st.markdown("</div>", unsafe_allow_html=True)

    if pin_input == "1305":
        st.session_state.authenticated = True
        st.rerun()
    elif len(pin_input) == 4:
        st.error("Incorrect PIN")
    st.stop()

# -----------------
# SHIFT ENTRY PAGE
# -----------------
st.set_page_config(page_title="Uber Go", layout="centered")
st.title("Uber Go Shift Logger")

if "start_data" not in st.session_state:
    st.session_state.start_data = {}

st.subheader("Start Shift")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Date", value=date.today())
    start_time = st.time_input("Start Time", value=datetime.now().time())
with col2:
    start_odo = st.number_input("Starting Odometer", step=1, format="%d")

if st.button("Start Shift"):
    st.session_state.start_data = {
        "start_date": start_date,
        "start_time": start_time,
        "start_odo": start_odo
    }
    st.success("Shift started. Now enter End Shift details below.")

st.markdown("---")

st.subheader("End Shift")
col3, col4 = st.columns(2)
with col3:
    end_time = st.time_input("End Time", value=datetime.now().time())
    end_odo = st.number_input("Ending Odometer", step=1, format="%d")
with col4:
    screenshot = st.file_uploader("Upload Uber Earnings Screenshot", type=["png", "jpg", "jpeg"])

if st.button("Finish Shift"):
    try:
        start = st.session_state.start_data

        # Default values
        gross, net, trips, tips, boosts, promos = "", "", "", "", "", ""
        ocr_text = ""

        if screenshot is not None:
            image = Image.open(screenshot)
            ocr_text = pytesseract.image_to_string(image)

            # Try extracting "Total earnings" and other values
            lines = ocr_text.splitlines()
            for i, line in enumerate(lines):
                if "Total earnings" in line:
                    parts = line.split()
                    for p in parts:
                        if "$" in p or "." in p:
                            try:
                                gross = float(p.replace("$", "").replace(",", ""))
                                break
                            except:
                                pass

        row = {
            "start_time": start["start_time"].strftime("%H:%M"),
            "start_odo": int(start["start_odo"]),
            "end_time": end_time.strftime("%H:%M"),
            "end_odo": int(end_odo),
            "date": start["start_date"].strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "gross_earnings": gross,
            "net_earnings": net,
            "trips": trips,
            "tips": tips,
            "boosts": boosts,
            "promotions": promos,
            "ocr_text": ocr_text,
            "source": "auto"
        }

        shifts_sheet.append_row(list(row.values()))
        st.success("Shift successfully logged!")

    except Exception as e:
        st.error(f"Failed to save shift: {e}")
