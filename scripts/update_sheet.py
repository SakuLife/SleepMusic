from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


def ensure_header_row(service_account_info, sheets_id, range_name):
    """Add header row if the sheet is empty."""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)

    # Check if sheet has data
    try:
        # Use simple range "A1:H1" to check first row
        result = service.spreadsheets().values().get(
            spreadsheetId=sheets_id,
            range="A1:H1",
        ).execute()
        values = result.get("values", [])

        # If empty or first row doesn't look like a header, add one
        if not values or len(values[0]) < 5:
            header = [
                "実行日時",
                "Seed",
                "音楽プロンプト",
                "背景画像プロンプト",
                "サムネイルプロンプト",
                "Drive URL",
                "YouTube URL",
                "ステータス",
            ]
            service.spreadsheets().values().update(
                spreadsheetId=sheets_id,
                range="A1:H1",
                valueInputOption="USER_ENTERED",
                body={"values": [header]},
            ).execute()
            print("Added header row to Sheets")
    except Exception as e:
        print(f"Note: Could not check/add header (continuing anyway): {e}")


def append_row(service_account_info, sheets_id, range_name, values):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)

    # Ensure header exists
    ensure_header_row(service_account_info, sheets_id, range_name)

    # Format column A (Date column) as datetime
    try:
        sheet_metadata = service.spreadsheets().get(spreadsheetId=sheets_id).execute()
        sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']

        format_request = {
            "requests": [{
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                                "type": "DATE_TIME",
                                "pattern": "yyyy-mm-dd hh:mm:ss"
                            }
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat"
                }
            }]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheets_id,
            body=format_request
        ).execute()
    except Exception as e:
        print(f"Note: Could not format date column (continuing anyway): {e}")

    body = {"values": [values]}
    service.spreadsheets().values().append(
        spreadsheetId=sheets_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()
