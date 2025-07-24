import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime

# ------------------ CONFIG ------------------

st.set_page_config(page_title="Uber Go", layout="centered")
st.title("Uber Go")

# ------------------ PASSCODE PROTECTION ------------------

if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    code = st.text_input("Enter passcode to unlock:", type="password")
    if code == "1305":
        st.session_state.unlocked = True
        st.success("Access granted")
        st.experimental_rerun()
    else:
        st.stop()

# ------------------ GOOGLE SHEETS AUTH ------------------

# Fix: decode the private_key's \\n to actual newlines
gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")

credentials = service_account.Credentials.from_service_account_info(gcp_info)
gc = gspread.authorize(credentials)
SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

# ------------------ SHIFT LOGIC ------------------

if "shift_started" not in st.session_state:
    st.session_state.shift_started = False

# ------------------ START SHIFT FORM ------------------

if not st.session_state.shift_started:
    st.subheader("Start Shift")
    with st.form("start_shift_form"):
        col1, col2 = st.columns(2)
        with col1:
            shift_date = st.date_input("Date", value=datetime.now().date())
        with col2:
            shift_time = st.time_input("Time", value=datetime.now().time())

        start_odo = st.number_input("Odometer", min_value=0, step=1)
        submitted = st.form_submit_button("Submit Start")

        if submitted:
            st.session_state.shift_started = True
            st.session_state["shift_date"] = shift_date.strftime("%d/%m/%Y")
            st.session_state["shift_time"] = shift_time.strftime("%H:%M")
            st.session_state["start_odo"] = start_odo
            st.success("Start shift recorded. Leave this window open.")
            st.experimental_rerun()

# ------------------ END SHIFT FORM ------------------

else:
    st.subheader("End Shift")
    with st.form("end_shift_form"):
        col1, col2 = st.columns(2)
        with col1:
            end_date = st.date_input("Date", value=datetime.now().date())
        with col2:
            end_time = st.time_input("Time", value=datetime.now().time())

        end_odo = st.number_input("Odometer", min_value=0, step=1)
        uploaded_file = st.file_uploader("Upload Uber screenshot (optional)", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Submit End")

        if submitted:
            row = [
                st.session_state["shift_time"],
                st.session_state["start_odo"],
                end_time.strftime("%H:%M"),
                end_odo,
                st.session_state["shift_date"],
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
                end_odo - st.session_state["start_odo"],
                "",  # online_hours
                "",  # online_minutes
                "",  # ocr_text
                "Uber"
            ]
            worksheet.append_row(row)
            st.success("Shift logged.")
            st.session_state.shift_started = False
            st.experimental_rerun()

# ------------------ FOOTER ------------------

st.markdown("---")
st.caption("Built with ❤️ by Tom")
