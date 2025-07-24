import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime
import pytesseract
from PIL import Image

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Uber Go", layout="centered")
st.title("Uber Go")

# -------------------- GOOGLE SHEETS AUTH --------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")

credentials = service_account.Credentials.from_service_account_info(gcp_info, scopes=SCOPES)
gc = gspread.authorize(credentials)

SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

# -------------------- SHIFT LOGIC --------------------
if "shift_started" not in st.session_state:
    st.session_state.shift_started = False

# -------------------- START SHIFT --------------------
if not st.session_state.shift_started:
    st.header("Start Shift")
    with st.form("start_shift_form"):
        shift_date = st.date_input("Date")
        start_time = st.time_input("Start Time")
        start_odo = st.number_input("Start Odometer", min_value=0, step=1)
        submitted = st.form_submit_button("Submit Start")

    if submitted:
        st.session_state.shift_started = True
        st.session_state.start_date = shift_date.strftime("%d/%m/%Y")
        st.session_state.start_time = start_time.strftime("%H:%M")
        st.session_state.start_odo = start_odo
        st.success("Shift started.")

# -------------------- END SHIFT --------------------
if st.session_state.shift_started:
    st.header("End Shift")
    with st.form("end_shift_form"):
        end_date = st.date_input("End Date")
        end_time = st.time_input("End Time")
        end_odo = st.number_input("End Odometer", min_value=0, step=1)
        uploaded_file = st.file_uploader("Upload Uber screenshot", type=["png", "jpg", "jpeg"])

        parsed_earnings = ""
        if uploaded_file:
            image = Image.open(uploaded_file)
            ocr_text = pytesseract.image_to_string(image)
            st.text_area("Parsed OCR Text", ocr_text, height=200)

            # Extract only the first number with $ to simulate earnings
            import re
            match = re.search(r"\$?(\d{1,4}\.\d{2})", ocr_text)
            if match:
                parsed_earnings = match.group(1)
                st.success(f"Earnings parsed: ${parsed_earnings}")
            else:
                st.warning("No earnings value detected.")

        submitted = st.form_submit_button("Submit End")
        if submitted:
            row = [
                st.session_state.start_time,
                st.session_state.start_odo,
                end_time.strftime("%H:%M"),
                end_odo,
                st.session_state.start_date,
                datetime.now().isoformat(),
                parsed_earnings,
                "", "", "", "", "", "", "", "",
                end_odo - st.session_state.start_odo,
                "", "", ocr_text if uploaded_file else "",
                "Uber"
            ]
            worksheet.append_row(row)
            st.success("Shift logged.")
            st.session_state.shift_started = False

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("Built with ❤️ by Tom")