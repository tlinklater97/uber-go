import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime

# --- Google Auth ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Decode \\n to real newlines in private key
gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")

credentials = service_account.Credentials.from_service_account_info(
    gcp_info, scopes=SCOPES
)

gc = gspread.authorize(credentials)
SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

# --- UI Config ---
st.set_page_config(page_title="Uber Go", layout="centered", page_icon="🚗")
st.title("Uber Go")

# --- Start Shift ---
st.header("Start Shift")
with st.form("start_shift_form"):
    start_time = st.time_input("Start Time")
    start_odo = st.number_input("Start Odometer", min_value=0, step=1)
    start_date = st.date_input("Shift Date", value=datetime.now().date())
    submitted_start = st.form_submit_button("Submit Start")

    if submitted_start:
        st.session_state["shift_start_time"] = start_time
        st.session_state["shift_start_odo"] = start_odo
        st.session_state["shift_start_date"] = start_date.strftime("%d/%m/%Y")
        st.success("Start shift recorded.")

# --- End Shift ---
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
            # Combine and save data
            row = [
                st.session_state["shift_start_time"].strftime("%H:%M"),
                st.session_state["shift_start_odo"],
                end_time.strftime("%H:%M"),
                end_odo,
                st.session_state["shift_start_date"],
                datetime.now().isoformat(),
                "",  # gross_earnings
                "",  # net_earnings
                "",  # trips
                "",  # tips
                "",  # boosts
                "",  # promotions
                "",  # adjustments
                "",  # cancellation_fees
                "",  # referrals
                end_odo - st.session_state["shift_start_odo"],
                "",  # online_hours
                "",  # online_minutes
                "",  # ocr_text
                "Uber"
            ]
            worksheet.append_row(row)
            st.success("Shift logged.")

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ by Tom")
