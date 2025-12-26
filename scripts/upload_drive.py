from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_to_drive(service_account_info, file_path, file_name, folder_id=None):
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    service = build("drive", "v3", credentials=creds)

    metadata = {"name": file_name}
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    file_obj = service.files().create(body=metadata, media_body=media, fields="id").execute()
    file_id = file_obj["id"]
    link = f"https://drive.google.com/file/d/{file_id}/view"
    return link
