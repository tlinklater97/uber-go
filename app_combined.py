import streamlit as st
import pytesseract
from PIL import Image
import io
import re
import gspread
from google.oauth2 import service_account

st.write("Loaded secrets:", st.secrets.keys())


# Set Streamlit page config
st.set_page_config(page_title="Uber Go - OCR Earnings Parser", layout="centered", initial_sidebar_state="collapsed")
st.title("📸 Upload Uber Screenshot for Earnings Parsing")

# Google Sheets setup from st.secrets
credentials_dict = {
    "type": st.secrets["gcp_service_account"]["type"],
    "project_id": st.secrets["gcp_service_account"]["project_id"],
    "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
    "private_key": st.secrets["gcp_service_account"]["private_key"],
    "client_email": st.secrets["gcp_service_account"]["client_email"],
    "client_id": st.secrets["gcp_service_account"]["client_id"],
    "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
    "token_uri": st.secrets["gcp_service_account"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
}

credentials = service_account.Credentials.from_service_account_info(credentials_dict)
client = gspread.authorize(credentials)
spreadsheet = client.open_by_key(st.secrets["secrets"]["spreadsheet_id"])

worksheet = spreadsheet.worksheet("Shifts")

def extract_earnings_from_text(ocr_text):
    # Preferred: match after "Total earnings"
    total_earnings_match = re.search(r"Total earnings.*?\$([0-9]+\.[0-9]{2})", ocr_text, re.IGNORECASE)
    if total_earnings_match:
        return float(total_earnings_match.group(1))

    # Fallback: match first dollar amount
    fallback_match = re.search(r"\$([0-9]+\.[0-9]{2})", ocr_text)
    if fallback_match:
        return float(fallback_match.group(1))

    return 0.0

uploaded_file = st.file_uploader("Upload Uber Earnings Screenshot", type=["png", "jpg", "jpeg"])

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
