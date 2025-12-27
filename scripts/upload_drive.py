from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_to_drive(client_id, client_secret, refresh_token, file_path, file_name, folder_id=None):
    """Upload file to Google Drive using OAuth credentials"""
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    service = build("drive", "v3", credentials=creds)

    metadata = {"name": file_name}
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    file_obj = service.files().create(
        body=metadata,
        media_body=media,
        fields="id",
    ).execute()
    file_id = file_obj["id"]
    link = f"https://drive.google.com/file/d/{file_id}/view"
    return link
