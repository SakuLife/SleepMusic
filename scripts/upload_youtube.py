import time
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
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
    publish_at=None,
    thumbnail_path=None,
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

    # Use resumable upload with chunking for large files
    media = MediaFileUpload(
        video_path,
        chunksize=10 * 1024 * 1024,  # 10MB chunks
        resumable=True,
    )

    # Build status object
    status = {
        "privacyStatus": privacy_status,
        "selfDeclaredMadeForKids": False,  # Not made for kids
    }

    # Add scheduled publish time if provided
    if publish_at:
        status["publishAt"] = publish_at
        # Must be private or unlisted for scheduled publishing
        if privacy_status == "public":
            status["privacyStatus"] = "private"

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "10",  # Music category
            },
            "status": status,
        },
        media_body=media,
    )

    # Execute resumable upload with retry logic
    response = None
    error = None
    retry_count = 0
    max_retries = 10

    while response is None:
        try:
            print("Uploading video chunk...")
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"Upload progress: {progress}%")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                # Retriable error
                error = f"Retriable error {e.resp.status}: {e}"
                retry_count += 1
                if retry_count > max_retries:
                    raise Exception(f"Upload failed after {max_retries} retries: {error}")
                print(f"{error}. Retrying in {retry_count * 2} seconds...")
                time.sleep(retry_count * 2)
            elif e.resp.status == 403 and "uploadLimitExceeded" in str(e):
                # Account not verified for 15+ minute videos
                raise Exception(
                    "YouTube account not verified for 15+ minute videos. "
                    "Please verify your account at https://www.youtube.com/verify"
                )
            else:
                raise

    print("Upload complete!")
    video_id = response.get("id")

    # Set custom thumbnail if provided
    if thumbnail_path:
        try:
            print("Setting custom thumbnail...")
            set_thumbnail(client_id, client_secret, refresh_token, video_id, thumbnail_path)
            print("Thumbnail set successfully!")
        except Exception as e:
            print(f"Warning: Failed to set thumbnail: {e}")
            print("Note: Custom thumbnails require a verified YouTube account")
            # Continue anyway - video upload succeeded

    return video_id


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
