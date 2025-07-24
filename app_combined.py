import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Uber Go", layout="centered")
st.title("Uber Go")

# ------------------ PASSCODE PROTECTION ------------------
if not st.session_state.get("unlocked", False):
    code = st.text_input("Enter passcode to unlock:", type="password")
    if code == "1305":
        st.session_state.unlocked = True
        st.success("Access granted. Please refresh to continue.")
    st.stop()

# ------------------ GOOGLE SHEETS SETUP ------------------
# Fix newline encoding in private key
gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")

credentials = service_account.Credentials.from_service_account_info(gcp_info)
gc = gspread.authorize(credentials)

SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

# ------------------ SHIFT UI LOGIC ------------------

def reset_shift_state():
    st.session_state.pop("shift_started", None)
    st.session_state.pop("start_datetime", None)
    st.session_state.pop("start_odo", None)

if not st.session_state.get("shift_started", False):
    st.subheader("Start Shift")
    with st.form("start_shift_form"):
        start_date = st.date_input("Start Date", value=datetime.now().date())
        start_time = st.time_input("Start Time", value=datetime.now().time())
        start_odo = st.number_input("Odometer", min_value=0, step=1)
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.session_state.shift_started = True
            st.session_state.start_datetime = datetime.combine(start_date, start_time)
            st.session_state.start_odo = start_odo
            st.success("Shift started!")
else:
    st.subheader("End Shift")
    with st.form("end_shift_form"):
        end_date = st.date_input("End Date", value=datetime.now().date())
        end_time = st.time_input("End Time", value=datetime.now().time())
        end_odo = st.number_input("Odometer", min_value=0, step=1)
        uploaded_file = st.file_uploader("Upload Uber screenshot (optional)", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Submit")
        if submitted:
            start_dt = st.session_state.start_datetime
            end_dt = datetime.combine(end_date, end_time)

            row = [
                start_dt.strftime("%H:%M"),
                st.session_state.start_odo,
                end_dt.strftime("%H:%M"),
                end_odo,
                start_dt.strftime("%d/%m/%Y"),
                datetime.now().isoformat(),  # Timestamp of entry
                "", "", "", "", "", "", "", "",  # Uber earnings placeholders
                end_odo - st.session_state.start_odo,
                "", "", "",  # Online hours/minutes, OCR
                "Uber"
            ]
            worksheet.append_row(row)
            st.success("Shift logged!")
            reset_shift_state()

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption("Built with ❤️ by Tom")
