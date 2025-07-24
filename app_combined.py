import streamlit as st
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image
import pytesseract
import base64
import io
import re

# ------------------ SETUP ------------------ #

st.set_page_config(page_title="Uber Go", layout="centered")

# Load custom font and dark theme
font_path = "fonts/FFClanProBold.TTF"
with open(font_path, "rb") as f:
    ttf_base64 = base64.b64encode(f.read()).decode("utf-8")
st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'UberFont';
        src: url(data:font/ttf;base64,{ttf_base64}) format('truetype');
    }}
    html, body, [class*="css"] {{
        font-family: 'UberFont', sans-serif;
        background-color: #0e1117;
        color: #f5f5f5;
    }}
    .stApp {{ padding: 0; }}
    </style>
""", unsafe_allow_html=True)

# ------------------ AUTH ------------------ #

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Uber Go")
    pin = st.text_input("Enter PIN", type="password", max_chars=4)
    if pin == "1305":
        st.session_state["authenticated"] = True
        st.rerun()
    elif len(pin) == 4:
        st.error("Incorrect PIN")
    st.stop()

# ------------------ GOOGLE SHEETS ------------------ #

SPREADSHEET_ID = "1MGOID38_FqkfmJDyCcG5L7wAyuC7L-OAg3LaHbAMb0g"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Shifts")

# ------------------ HELPER FUNCTIONS ------------------ #

def extract_gross_earnings(ocr_text):
    matches = re.findall(r"\$([0-9]+\.[0-9]{2})", ocr_text)
    if matches:
        # Return the largest $ amount (usually gross fare)
        return float(max(matches, key=lambda x: float(x)))
    return 0.0

# ------------------ MAIN APP ------------------ #

st.title("Uber Go")
page = st.radio("Select Page", ["Start Shift", "End Shift"], horizontal=True)

# ------------------ START SHIFT ------------------ #

if page == "Start Shift":
    st.subheader("🚗 Start Shift")
    date_input = st.date_input("Date", value=date.today())
    time_input = st.time_input("Start Time", value=datetime.now().time())
    odo_input = st.number_input("Odometer (km)", min_value=0, step=1)

    if st.button("Save Start"):
        st.session_state["shift_start"] = {
            "date": date_input,
            "time": time_input,
            "odo": odo_input
        }
        st.success("Start shift saved!")

# ------------------ END SHIFT ------------------ #

if page == "End Shift":
    st.subheader("🏁 End Shift")

    if "shift_start" not in st.session_state:
        st.warning("Please start a shift first.")
        st.stop()

    end_date = st.date_input("Date", value=date.today())
    end_time = st.time_input("End Time", value=datetime.now().time())
    end_odo = st.number_input("Odometer (km)", min_value=0, step=1)

    screenshot = st.file_uploader("Upload Uber Screenshot", type=["png", "jpg", "jpeg"])
    ocr_text = ""
    gross_earnings = 0.0

    if screenshot:
        img = Image.open(screenshot)
        ocr_text = pytesseract.image_to_string(img)
        gross_earnings = extract_gross_earnings(ocr_text)
        st.markdown(f"**Parsed Gross Earnings:** ${gross_earnings:.2f}")

    if st.button("Submit Shift"):
        start = st.session_state["shift_start"]
        mileage = end_odo - start["odo"]
        row = [
            start["time"].strftime("%H:%M"),
            start["odo"],
            end_time.strftime("%H:%M"),
            end_odo,
            end_date.strftime("%Y-%m-%d"),
            datetime.now().isoformat(),
            gross_earnings, "", "", "", "", "", "", "",  # Only gross filled
            mileage,
            "", "",  # online hours/minutes placeholders
            ocr_text,
            "manual + ocr"
        ]
        try:
            sheet.append_row(row)
            st.success("Shift saved to Google Sheets.")
            del st.session_state["shift_start"]
        except Exception as e:
            st.error(f"Failed to save shift: {e}")
