import gspread
import streamlit as st
import json
from google.oauth2.service_account import Credentials

def connect_to_sheet(spreadsheet_name, worksheet_name):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # ✅ Updated to use single JSON blob
    service_account_info = json.loads(st.secrets["secret_key_json"])
    
    credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    gc = gspread.authorize(credentials)
    sheet = gc.open(spreadsheet_name).worksheet(worksheet_name)
    return sheet

def get_latest_odo(sheet, odo_column_name="end_odo"):
    records = sheet.get_all_records()
    odos = [row[odo_column_name] for row in records if isinstance(row[odo_column_name], int)]
    return max(odos) if odos else 0
