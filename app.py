import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# === Streamlit Page Setup ===
st.set_page_config(page_title="Uber Go", layout="centered", initial_sidebar_state="collapsed")
st.title("🚗 Uber Go")

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit Secrets
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)

# Access spreadsheet and worksheet
SHEET_NAME = "Uber Go - Earnings Tracker"
TAB_NAME = "Shifts"
sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)

# === Example UI to Test Google Sheets ===
st.subheader("✅ Google Sheets is connected!")

# Show current date
today = datetime.now().strftime("%Y-%m-%d")
st.write("Today's date:", today)

# Input form to test writing to sheet
with st.form("test_form"):
    name = st.text_input("Enter your name")
    odo = st.number_input("Odometer reading", step=1)
    submit = st.form_submit_button("Submit to Sheet")

if submit:
    row = [today, name, int(odo)]
    sheet.append_row(row)
    st.success("✅ Submitted to Google Sheet!")
