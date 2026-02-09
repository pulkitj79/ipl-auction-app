import os
import time
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# -------------------------------------------------
# GOOGLE AUTH
# -------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    creds = Credentials.from_service_account_info(
        {
            "type": "service_account",
            "project_id": os.environ["GCP_PROJECT_ID"],
            "private_key_id": os.environ["GCP_PRIVATE_KEY_ID"],
            "private_key": os.environ["GCP_PRIVATE_KEY"].replace("\\n", "\n"),
            "client_email": os.environ["GCP_CLIENT_EMAIL"],
            "client_id": os.environ["GCP_CLIENT_ID"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ["GCP_CLIENT_CERT_URL"],
        },
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def get_spreadsheet():
    client = get_client()
    return client.open_by_key(os.environ["GOOGLE_SHEET_ID"])

# -------------------------------------------------
# READ SHEET
# -------------------------------------------------
def read_sheet(sheet_name, retries=3):
    for attempt in range(retries):
        try:
            sh = get_spreadsheet()
            ws = sh.worksheet(sheet_name)
            data = ws.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(1)

# -------------------------------------------------
# WRITE KEY–VALUE (Live_Auction)
# -------------------------------------------------
def write_kv(sheet_name, key, value, retries=3):
    for attempt in range(retries):
        try:
            sh = get_spreadsheet()
            ws = sh.worksheet(sheet_name)

            records = ws.get_all_records()
            for idx, row in enumerate(records, start=2):
                if row.get("key") == key:
                    ws.update_cell(idx, 2, value)
                    return

            # key not found → append
            ws.append_row([key, value])
            return

        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(1)

# -------------------------------------------------
# UPDATE ROW BY ID
# -------------------------------------------------
def update_row(sheet_name, id_col, id_val, updates, retries=3):
    for attempt in range(retries):
        try:
            sh = get_spreadsheet()
            ws = sh.worksheet(sheet_name)

            header = ws.row_values(1)
            id_index = header.index(id_col) + 1

            rows = ws.get_all_values()
            for row_num, row in enumerate(rows[1:], start=2):
                if row[id_index - 1] == str(id_val):
                    for col, val in updates.items():
                        col_index = header.index(col) + 1
                        ws.update_cell(row_num, col_index, val)
                    return
            return

        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(1)

# -------------------------------------------------
# APPEND ROW (Auction_Log)
# -------------------------------------------------
def append_row(sheet_name, row_dict, retries=3):
    for attempt in range(retries):
        try:
            sh = get_spreadsheet()
            ws = sh.worksheet(sheet_name)

            header = ws.row_values(1)
            row = [row_dict.get(col, "") for col in header]
            ws.append_row(row)
            return

        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(1)
