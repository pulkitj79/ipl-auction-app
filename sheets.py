import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def get_gsheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    client = gspread.authorize(creds)
    files = client.list_spreadsheet_files()
    print(files)

    sheet = client.open("https://docs.google.com/spreadsheets/d/1qMuGvmyuzSaFIIExgVUQqghYwsoGNctPGnHx44_s1fY/edit?gid=0#gid=0")
    return sheet


def read_sheet(sheet_name):
    sheet = get_gsheet()
    ws = sheet.worksheet(sheet_name)
    data = ws.get_all_records()
    return pd.DataFrame(data)

