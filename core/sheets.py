import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_client():
    json_creds = dict(st.secrets["gcp_service_account"])

    # Fix newline issue in private key
    json_creds["private_key"] = json_creds["private_key"].replace("\\n", "\n")

    credentials = Credentials.from_service_account_info(
        json_creds, scopes=SCOPES
    )
    return gspread.authorize(credentials)

client = get_client()

SHEET_ID = "1M84vmqH1Pz0kE197nH_reROOkWtwdcFXC5uqi0l31lI"
sheet = client.open_by_key(SHEET_ID)

def append_row(sheet_name: str, row: list):
    worksheet = sheet.worksheet(sheet_name)
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

    except:
        return []

def delete_row(sheet_name: str, row_index: int):
    worksheet = sheet.worksheet(sheet_name)
    worksheet.delete_rows(row_index)

def clear_sheet(sheet_name: str):
    worksheet = sheet.worksheet(sheet_name)
    headers = worksheet.row_values(1)
    worksheet.clear()
    if headers:
        worksheet.append_row(headers)
