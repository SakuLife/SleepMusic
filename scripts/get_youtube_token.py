import os
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow


def update_env_refresh_token(token):
    env_path = ".env"
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"YOUTUBE_REFRESH_TOKEN={token}\n")
        return

    lines = []
    updated = False
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("YOUTUBE_REFRESH_TOKEN="):
                lines.append(f"YOUTUBE_REFRESH_TOKEN={token}\n")
                updated = True
            else:
                lines.append(line)
    if not updated:
        lines.append(f"YOUTUBE_REFRESH_TOKEN={token}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def extract_code(value):
    if value.startswith("http"):
        parsed = urlparse(value)
        query = parse_qs(parsed.query)
        code = query.get("code", [""])[0]
        return code
    return value.strip()


def main():
    load_dotenv()
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    auth_code = os.getenv("YOUTUBE_AUTH_CODE")
    auth_url = os.getenv("YOUTUBE_AUTH_URL")
    redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", "http://localhost:8765")

    if not client_id or not client_secret:
        raise RuntimeError("Missing YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET in .env")

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                "urn:ietf:wg:oauth:2.0:oob",
                "http://localhost",
            ],
        }
    }

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)
    flow.redirect_uri = redirect_uri

    if not auth_code:
        if not auth_url:
            auth_url, _ = flow.authorization_url(
                access_type="offline",
                prompt="consent",
            )
            print("Open this URL in your browser:")
            print(auth_url)
        auth_code = input("Paste the code or full redirected URL: ").strip()

    auth_code = extract_code(auth_code)
    flow.fetch_token(code=auth_code)
    creds = flow.credentials

    if not creds.refresh_token:
        raise RuntimeError("Refresh token not returned. Try again with prompt=consent.")

    update_env_refresh_token(creds.refresh_token)
    print("Refresh token saved to .env")


if __name__ == "__main__":
    main()
