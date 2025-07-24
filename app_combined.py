import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime

# -- FIX: define required scopes --
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# -- FIX: properly decode private key newlines and set scopes --
gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")

credentials = service_account.Credentials.from_service_account_info(
    gcp_info, scopes=SCOPES
)

# -- Load Spreadsheet ID from secrets --
SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]

# -- Google Sheets setup --
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

# -- Streamlit UI --
st.set_page_config(page_title="Uber Go", layout="centered", page_icon="🚗")
st.title("Uber Go")

# Section: Start a new shift
st.header("Start Shift")
with st.form("start_shift_form"):
    start_time = st.time_input("Start Time")
    start_odo = st.number_input("Start Odometer", min_value=0, step=1)
    submitted_start = st.form_submit_button("Submit Start")
    if submitted_start:
        st.session_state["shift_start_time"] = start_time
        st.session_state["shift_start_odo"] = start_odo
        st.session_state["shift_start_date"] = datetime.now().strftime("%d/%m/%Y")
        st.success("Start shift recorded.")

# Section: End shift
st.header("End Shift")
with st.form("end_shift_form"):
    end_time = st.time_input("End Time")
    end_odo = st.number_input("End Odometer", min_value=0, step=1)
    uploaded_file = st.file_uploader("Upload Uber screenshot (optional)", type=["png", "jpg", "jpeg"])
    submitted_end = st.form_submit_button("Submit End")
    if submitted_end:
        if "shift_start_time" not in st.session_state:
            st.error("You must start a shift first.")
        else:
            row = [
                st.session_state["shift_start_time"].strftime("%H:%M"),
                st.session_state["shift_start_odo"],
                end_time.strftime("%H:%M"),
                end_odo,
                st.session_state["shift_start_date"],
                datetime.now().isoformat(),
                "", "", "", "", "", "", "", "", "",  # placeholder earnings data
                end_odo - st.session_state["shift_start_odo"],
                "", "", "", "Uber"
            ]
            worksheet.append_row(row)
            st.success("Shift logged.")

# Footer
st.markdown("---")
st.caption("Built with ❤️ by Tom")
