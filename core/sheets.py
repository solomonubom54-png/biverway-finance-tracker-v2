import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
json_creds = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(json_creds, scopes=SCOPES)
client = gspread.authorize(credentials)

SHEET_ID = "1M84vmqH1Pz0kE197nH_reROOkWtwdcFXC5uqi0l31lI"
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
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)

        for col in headers:
            if col not in df.columns:
                df[col] = ""

        return df.to_dict(orient="records")

    except gspread.WorksheetNotFound:
        return []

def delete_by_id(sheet_name: str, record_id: str):
    try:
        worksheet = sheet.worksheet(sheet_name)
        records = worksheet.get_all_records()

        for i, row in enumerate(records):
            if str(row.get("id")) == str(record_id):
                worksheet.delete_rows(i + 2)
                break

    except Exception as e:
        st.warning(f"Error deleting record: {e}")
