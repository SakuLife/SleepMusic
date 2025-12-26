from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


def append_row(service_account_info, sheets_id, range_name, values):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)
    body = {"values": [values]}
    service.spreadsheets().values().append(
        spreadsheetId=sheets_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()
