import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES,
)

client = gspread.authorize(credentials)

SHEET_ID = "1M84vmqH1Pz0kE197nH_reROOkWtwdcFXC5uqi0l31lI"
sheet = client.open_by_key(SHEET_ID)


def get_worksheet(sheet_name):
    try:
        return sheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return sheet.add_worksheet(title=sheet_name, rows="1000", cols="20")


def append_row(sheet_name, row):
    ws = get_worksheet(sheet_name)
    ws.append_row(row, value_input_option="USER_ENTERED")


def load_sheet(sheet_name):
    ws = get_worksheet(sheet_name)
    return ws.get_all_records()
