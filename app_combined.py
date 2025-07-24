import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime

st.set_page_config(page_title="Uber Go", layout="centered")
st.title("Uber Go")

# ------------------ PASSCODE PROTECTION ------------------

if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    code = st.text_input("Enter passcode to unlock:", type="password")
    if code == "1305":
        st.session_state.unlocked = True
        st.success("Access granted. You can now continue.")
    else:
        st.stop()

# ------------------ GOOGLE SHEETS SETUP ------------------

# Decode the private key newlines
gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = service_account.Credentials.from_service_account_info(
    gcp_info, scopes=scopes
)

gc = gspread.authorize(credentials)
SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

# ------------------ SHIFT LOGIC ------------------

if "shift_started" not in st.session_state:
    st.session_state.shift_started = False

st.markdown("---")

if not st.session_state.shift_started:
    st.subheader("Start Shift")

    with st.form("start_shift_form"):
        start_date = st.date_input("Date", value=datetime.now())
        start_time = st.time_input("Start Time", value=datetime.now().time())
        start_odo = st.number_input("Start Odometer", min_value=0, step=1)
        start_submit = st.form_submit_button("Start Shift")

    if start_submit:
        st.session_state.shift_started = True
        st.session_state.start_date = start_date.strftime("%d/%m/%Y")
        st.session_state.start_time = start_time.strftime("%H:%M")
        st.session_state.start_odo = start_odo
        st.success("Shift started.")
        st.experimental_rerun()

else:
    st.subheader("End Shift")

    with st.form("end_shift_form"):
        end_date = st.date_input("Date", value=datetime.now())
        end_time = st.time_input("End Time", value=datetime.now().time())
        end_odo = st.number_input("End Odometer", min_value=0, step=1)
        uploaded_file = st.file_uploader("Upload Uber screenshot (optional)", type=["png", "jpg", "jpeg"])
        end_submit = st.form_submit_button("End Shift")

    if end_submit:
        mileage = end_odo - st.session_state.start_odo

        row = [
            st.session_state.start_time,
            st.session_state.start_odo,
            end_time.strftime("%H:%M"),
            end_odo,
            st.session_state.start_date,
            datetime.now().isoformat(),
            "", "", "", "", "", "", "", "", "",  # earnings placeholders
            mileage,
            "", "", "",  # time placeholders
            "Uber"
        ]

        worksheet.append_row(row)
        st.success("Shift logged.")

        # Reset for next shift
        st.session_state.shift_started = False
        st.experimental_rerun()

st.markdown("---")
st.caption("Built with ❤️ by Tom")
