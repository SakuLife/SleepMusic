from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_video(
    client_id,
    client_secret,
    refresh_token,
    video_path,
    title,
    description,
    tags,
    privacy_status="public",
):
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    youtube = build("youtube", "v3", credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "10",
            },
            "status": {"privacyStatus": privacy_status},
        },
        media_body=MediaFileUpload(video_path, resumable=True),
    )
    response = request.execute()
    return response.get("id")


def set_thumbnail(client_id, client_secret, refresh_token, video_id, thumbnail_path):
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path),
    )
    request.execute()
