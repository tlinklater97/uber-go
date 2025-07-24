import textwrap

app_combined_code = textwrap.dedent("""
import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime, date, time
from PIL import Image
import pytesseract
import io
import re

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

# ------------------ GOOGLE SHEETS AUTH ------------------

gcp_info = dict(st.secrets["gcp_service_account"])
gcp_info["private_key"] = gcp_info["private_key"].replace("\\n", "\\n").replace("\\\\n", "\\n").replace("\\n", "\n")

scoped_credentials = service_account.Credentials.from_service_account_info(
    gcp_info,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)
gc = gspread.authorize(scoped_credentials)
SPREADSHEET_ID = st.secrets["general"]["spreadsheet_id"]
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet("Shifts")

# ------------------ START SHIFT ------------------

if "shift_started" not in st.session_state:
    st.session_state.shift_started = False

if not st.session_state.shift_started:
    st.subheader("Start Shift")
    shift_date = st.date_input("Date", value=date.today())
    start_time = st.time_input("Start Time", value=datetime.now().time())
    start_odo = st.number_input("Start Odometer", min_value=0, step=1)
    if st.button("Start Shift"):
        st.session_state.shift_date = shift_date.strftime("%d/%m/%Y")
        st.session_state.start_time = start_time.strftime("%H:%M")
        st.session_state.start_odo = start_odo
        st.session_state.shift_started = True
        st.success("Shift started.")

# ------------------ END SHIFT ------------------

else:
    st.subheader("End Shift")
    end_date = st.date_input("End Date", value=date.today())
    end_time = st.time_input("End Time", value=datetime.now().time())
    end_odo = st.number_input("End Odometer", min_value=0, step=1)
    uploaded_file = st.file_uploader("Upload Uber screenshot (optional)", type=["png", "jpg", "jpeg"])

    parsed_text = ""
    gross_earnings = ""

    if uploaded_file:
        image = Image.open(uploaded_file)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()

        parsed_text = pytesseract.image_to_string(Image.open(io.BytesIO(img_bytes)))
        st.text_area("Parsed Text", parsed_text, height=150)

        match = re.search(r"NZ\\$?\\s?([0-9]+\\.[0-9]{2})", parsed_text)
        if match:
            gross_earnings = match.group(1)

    if st.button("End Shift"):
        row = [
            st.session_state.start_time,
            st.session_state.start_odo,
            end_time.strftime("%H:%M"),
            end_odo,
            st.session_state.shift_date,
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
            end_odo - st.session_state.start_odo,
            "",  # online_hours
            "",  # online_minutes
            parsed_text,
            "Uber"
        ]
        worksheet.append_row(row)
        st.success("Shift logged.")
        st.session_state.shift_started = False

# ------------------ FOOTER ------------------

st.markdown("---")
st.caption("Built with ❤️ by Tom")
""")

# Save to file
with open("/mnt/data/app_combined.py", "w") as f:
    f.write(app_combined_code)

"/mnt/data/app_combined.py"
