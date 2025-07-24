import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime, date, time
from PIL import Image
import pytesseract

# --- CONFIG ---
st.set_page_config(page_title="Uber Go", layout="centered")
st.title("Uber Go")

# --- AUTHENTICATION ---
gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")
credentials = service_account.Credentials.from_service_account_info(gcp_info)
gc = gspread.authorize(credentials)
SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

# --- SESSION INIT ---
if "shift_started" not in st.session_state:
    st.session_state.shift_started = False

# --- SHIFT START ---
if not st.session_state.shift_started:
    st.subheader("Start Shift")
    start_date = st.date_input("Date", value=date.today(), key="start_date")
    start_time = st.time_input("Start Time", value=datetime.now().time(), key="start_time")
    start_odo = st.number_input("Start Odometer", min_value=0, step=1, key="start_odo")
    if st.button("Start Shift"):
        st.session_state.shift_started = True
        st.session_state.shift_data = {
            "start_time": start_time.strftime("%H:%M"),
            "start_odo": start_odo,
            "date": start_date.strftime("%d/%m/%Y")
        }
        st.success("Shift started.")

# --- SHIFT END ---
else:
    st.subheader("End Shift")
    end_date = st.date_input("Date", value=date.today(), key="end_date")
    end_time = st.time_input("End Time", value=datetime.now().time(), key="end_time")
    end_odo = st.number_input("End Odometer", min_value=0, step=1, key="end_odo")
    uploaded_file = st.file_uploader("Upload Uber screenshot (optional)", type=["png", "jpg", "jpeg"])

    ocr_text = ""
    gross_earnings = ""

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        ocr_text = pytesseract.image_to_string(image)
        st.text_area("Parsed Text", ocr_text, height=150)

        match = st.session_state.get("earnings_match")
        import re
        match = re.search(r"\$?(\d+\.\d{2})", ocr_text.replace(",", ""))
        if match:
            gross_earnings = match.group(1)
            st.success(f"OCR parsed gross earnings: ${gross_earnings}")
        else:
            st.warning("Could not find earnings in image.")

    if st.button("End Shift"):
        start = st.session_state.shift_data
        row = [
            start["start_time"],
            start["start_odo"],
            end_time.strftime("%H:%M"),
            end_odo,
            start["date"],
            datetime.now().isoformat(),
            gross_earnings,
            "",  # net_earnings
            "",  # trips
            "",  # tips
            "",  # boosts
            "",  # promotions
            "",  # adjustments
            "",  # cancellation_fees
            "",  # referrals
            end_odo - start["start_odo"],
            "",  # online_hours
            "",  # online_minutes
            ocr_text,
            "Uber"
        ]
        worksheet.append_row(row)
        st.success("Shift logged.")
        st.session_state.shift_started = False

# Footer
st.markdown("---")
st.caption("Built with ❤️ by Tom")

