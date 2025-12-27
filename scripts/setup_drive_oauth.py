"""Setup Google Drive OAuth tokens for the pipeline"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',  # Upload files to Drive
    'https://www.googleapis.com/auth/youtube.upload',  # YouTube upload (if not already authorized)
]

def main():
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET must be set in .env")
        return

    print("=" * 60)
    print("Google Drive OAuth Setup")
    print("=" * 60)
    print("\nOpening browser for authorization...")
    print("Scopes: Google Drive (upload files) + YouTube (upload videos)")

    # Create OAuth flow
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

    # Run local server to get authorization
    credentials = flow.run_local_server(port=0)

    print("\n" + "=" * 60)
    print("SUCCESS! Authorization complete.")
    print("=" * 60)
    print("\nAdd this to your .env file:")
    print(f"\nGOOGLE_REFRESH_TOKEN={credentials.refresh_token}")
    print("\nOr if using GitHub Secrets, add:")
    print("Secret name: GOOGLE_REFRESH_TOKEN")
    print(f"Secret value: {credentials.refresh_token}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
