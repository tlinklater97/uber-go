import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime
from PIL import Image
import pytesseract
import io

# ------------------ CONFIG ------------------

st.set_page_config(page_title="Uber Go", layout="centered")

# Authenticate with Streamlit secrets
gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")
credentials = service_account.Credentials.from_service_account_info(gcp_info)
gc = gspread.authorize(credentials)
SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

st.title("Uber Go")

# ------------------ SHIFT LOGIC ------------------

if "shift_started" not in st.session_state:
    st.session_state.shift_started = False

if not st.session_state.shift_started:
    st.header("Start Shift")
    with st.form("start_form"):
        start_date = st.date_input("Date", value=datetime.today())
        start_time = st.time_input("Start Time", value=datetime.now().time())
        start_odo = st.number_input("Odometer", min_value=0, step=1)
        start_submit = st.form_submit_button("Submit")
        if start_submit:
            st.session_state.start_date = start_date.strftime("%d/%m/%Y")
            st.session_state.start_time = start_time.strftime("%H:%M")
            st.session_state.start_odo = start_odo
            st.session_state.shift_started = True
            st.success("Shift started.")
else:
    st.header("End Shift")
    with st.form("end_form"):
        end_date = st.date_input("Date", value=datetime.today())
        end_time = st.time_input("End Time", value=datetime.now().time())
        end_odo = st.number_input("Odometer", min_value=0, step=1)
        screenshot = st.file_uploader("Upload Uber screenshot", type=["png", "jpg", "jpeg"])
        end_submit = st.form_submit_button("Submit")

        if end_submit:
            gross_earnings = ""
            ocr_text = ""

            if screenshot:
                image_bytes = screenshot.read()
                image = Image.open(io.BytesIO(image_bytes))
                ocr_text = pytesseract.image_to_string(image)
                lines = ocr_text.splitlines()
                for line in lines:
                    if "$" in line or "NZ$" in line:
                        try:
                            gross_earnings = (
                                line.replace("NZ$", "")
                                .replace("$", "")
                                .replace(",", "")
                                .strip()
                            )
                            float(gross_earnings)
                            break
                        except:
                            continue

            # Log to Google Sheet
            row = [
                st.session_state.start_time,
                st.session_state.start_odo,
                end_time.strftime("%H:%M"),
                end_odo,
                st.session_state.start_date,
                datetime.now().isoformat(),
                gross_earnings,
                "", "", "", "", "", "", "", "",  # net, trips, tips, boosts, etc.
                end_odo - st.session_state.start_odo,
                "", "",  # online time
                ocr_text,
                "Uber"
            ]
            worksheet.append_row(row)
            st.success("Shift logged.")
            st.session_state.shift_started = False  # Reset for next shift