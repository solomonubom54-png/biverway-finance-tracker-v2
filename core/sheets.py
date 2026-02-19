import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ====================== CONFIG ======================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
json_creds = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(json_creds, scopes=SCOPES)
client = gspread.authorize(credentials)

SHEET_ID = "1M84vmqH1Pz0kE197nH_reROOkWtwdcFXC5uqi0l31lI"
sheet = client.open_by_key(SHEET_ID)

# ====================== FUNCTIONS ======================
def append_row(sheet_name: str, row: list):
    try:
        worksheet = sheet.worksheet(sheet_name)
        worksheet.append_row(row, value_input_option="USER_ENTERED")
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
        worksheet.append_row(row, value_input_option="USER_ENTERED")

def load_sheet(sheet_name: str, headers: list):
    try:
        worksheet = sheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        for col in headers:
            if col not in df.columns:
                df[col] = ""
        return df.to_dict(orient="records")
    except gspread.WorksheetNotFound:
        return []

def delete_row(sheet_name: str, row_index: int):
    try:
        worksheet = sheet.worksheet(sheet_name)
        worksheet.delete_rows(row_index)
    except gspread.WorksheetNotFound:
        st.warning(f"Worksheet '{sheet_name}' not found.")
    except Exception as e:
        st.warning(f"Unable to delete row {row_index} in '{sheet_name}': {e}")

def clear_sheet(sheet_name: str):
    try:
        worksheet = sheet.worksheet(sheet_name)
        headers = worksheet.row_values(1)
        worksheet.clear()
        if headers:
            worksheet.append_row(headers, value_input_option="USER_ENTERED")
    except gspread.WorksheetNotFound:
        st.warning(f"Worksheet '{sheet_name}' not found.")
    except Exception as e:
        st.warning(f"Unable to clear sheet '{sheet_name}': {e}")
