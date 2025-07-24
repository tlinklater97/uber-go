import streamlit as st
import pytesseract
from PIL import Image
import re
import gspread
from google.oauth2 import service_account

# Load service account credentials from secrets
credentials_dict = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(credentials_dict)
client = gspread.authorize(credentials)

# Load spreadsheet using the nested 'general' key
spreadsheet = client.open_by_key(st.secrets["general"]["spreadsheet_id"])
worksheet = spreadsheet.worksheet("Shifts")

# Streamlit UI setup
st.set_page_config(page_title="Uber Go - OCR Earnings Parser", layout="centered", initial_sidebar_state="collapsed")
st.title("📸 Upload Uber Screenshot for Earnings Parsing")

uploaded_file = st.file_uploader("Upload Uber Earnings Screenshot", type=["png", "jpg", "jpeg"])

def extract_earnings_from_text(ocr_text):
    # Try to match "Total earnings" first
    match = re.search(r"Total earnings.*?\$([0-9]+\.[0-9]{2})", ocr_text, re.IGNORECASE)
    if match:
        return float(match.group(1))

    # Fallback: find first dollar amount
    fallback = re.search(r"\$([0-9]+\.[0-9]{2})", ocr_text)
    if fallback:
        return float(fallback.group(1))

    return 0.0

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Screenshot", use_column_width=True)

    with st.spinner("Extracting text with OCR..."):
        ocr_text = pytesseract.image_to_string(image)

    st.text_area("🔍 OCR Extracted Text", ocr_text, height=300)

    gross_earnings = extract_earnings_from_text(ocr_text)
    st.success(f"Detected Gross Earnings: ${gross_earnings:.2f}")

    if st.button("✅ Save to Google Sheet"):
        new_row = [None, None, None, None, None, None, gross_earnings, None, None, None, None, None, None, None, None, None, ocr_text, "screenshot"]
        worksheet.append_row(new_row)
        st.success("Data saved to Google Sheet ✅")
else:
    st.info("Please upload a screenshot of your Uber weekly earnings screen.")
