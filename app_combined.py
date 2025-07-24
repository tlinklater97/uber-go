import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime
import pytesseract
from PIL import Image
import io

# ------------------ PAGE SETUP ------------------
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
    st.stop()

# ------------------ GOOGLE SHEETS SETUP ------------------

# Convert \\n to \n in the private key
gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\n")

# Set correct scopes
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

# ------------------ SHIFT ENTRY ------------------

if "shift_started" not in st.session_state:
    st.session_state.shift_started = False

if not st.session_state.shift_started:
    st.header("Start Shift")
    with st.form("start_shift_form"):
        shift_date = st.date_input("Date", value=datetime.now())
        start_time = st.time_input("Start Time", value=datetime.now().time())
        start_odo = st.number_input("Start Odometer", min_value=0, step=1)
        submitted = st.form_submit_button("Submit")

    if submitted:
        st.session_state.shift_date = shift_date.strftime("%d/%m/%Y")
        st.session_state.start_time = start_time.strftime("%H:%M")
        st.session_state.start_odo = start_odo
        st.session_state.shift_started = True
        st.success("Shift started.")

# ------------------ END SHIFT ------------------

if st.session_state.shift_started:
    st.header("End Shift")
    with st.form("end_shift_form"):
        end_time = st.time_input("End Time", value=datetime.now().time())
        end_odo = st.number_input("End Odometer", min_value=0, step=1)
        uploaded_file = st.file_uploader("Upload Uber Earnings Screenshot (optional)", type=["png", "jpg", "jpeg"])

        earnings = ""
        if uploaded_file:
            image = Image.open(uploaded_file)
            text = pytesseract.image_to_string(image)
            lines = text.split("\n")
            for line in lines:
                if "Earnings" in line and "$" in line:
                    earnings = line.split("$")[-1].strip()
                    break

        earnings = st.text_input("Gross Earnings ($)", value=earnings)

        submitted = st.form_submit_button("Submit")
        if submitted:
            mileage = end_odo - st.session_state.start_odo

            row = [
                st.session_state.start_time,
                st.session_state.start_odo,
                end_time.strftime("%H:%M"),
                end_odo,
                st.session_state.shift_date,
                datetime.now().isoformat(),
                earnings,
                "", "", "", "", "", "", "", "",  # placeholders
                mileage,
                "", "", text if uploaded_file else "",
                "Uber"
            ]
            worksheet.append_row(row)
            st.success("Shift logged.")
            st.session_state.shift_started = False

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption("Built with ❤️ by Tom")
