import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

json_creds = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(json_creds, scopes=SCOPES)
client = gspread.authorize(credentials)

SHEET_ID = "YOUR_NEW_SHEET_ID"  # replace after rotating key
sheet = client.open_by_key(SHEET_ID)

def append_row(sheet_name: str, row: list):
    try:
        worksheet = sheet.worksheet(sheet_name)
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
    except Exception as e:
        st.warning(f"Delete failed: {e}")

def clear_sheet(sheet_name: str):
    try:
        worksheet = sheet.worksheet(sheet_name)
        headers = worksheet.row_values(1)
        worksheet.clear()
        if headers:
            worksheet.append_row(headers)
    except Exception as e:
        st.warning(f"Clear failed: {e}")
