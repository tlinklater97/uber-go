import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# Load credentials from Streamlit secrets
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict)

# Authorize and access the spreadsheet
gc = gspread.authorize(creds)

def get_sheet(sheet_name="Uber Go - Earnings Tracker", tab_name="Shifts"):
    return gc.open(sheet_name).worksheet(tab_name)
