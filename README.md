# SleepMusic Pipeline

Automated daily pipeline to generate sleep BGM, create images, render a video, save to Drive/Sheets, and upload to YouTube with scheduled publishing.

**Schedule**: Runs daily at 17:00 JST, publishes to YouTube at 20:00 JST.

## Structure
- `scripts/run_pipeline.py`: Orchestrates the end-to-end flow
- `scripts/`: API clients and processing utilities
- `config/templates.json`: Text templates and prompt seeds
- `.github/workflows/daily.yml`: GitHub Actions schedule

## Requirements
- Python 3.11+
- ffmpeg available on PATH
- **YouTube account verified** (required for 15+ minute videos): https://www.youtube.com/verify

## Required Secrets (GitHub Actions / Environment Variables)

**Minimum required (for YouTube upload only)**:
- `KIEAI_API_KEY` - KieAI API key for Suno and Nano Banana
- `GEMINI_API_KEY` - Google Gemini API key for AI-generated image prompt variations
- `YOUTUBE_CLIENT_ID` - YouTube OAuth2 client ID
- `YOUTUBE_CLIENT_SECRET` - YouTube OAuth2 client secret
- `YOUTUBE_REFRESH_TOKEN` - YouTube OAuth2 refresh token

**Optional (for Drive backup and Sheets logging)**:
- `GOOGLE_REFRESH_TOKEN` - Google OAuth refresh token for Drive uploads (obtained via `python scripts/setup_drive_oauth.py`)
- `DRIVE_FOLDER_ID` - Google Drive folder ID (example: `1rd89Gs8aM2h2wB5ot0_MJc2NK9Fi_KzB`)
- `GCP_SERVICE_ACCOUNT_JSON` - GCP service account JSON (for Sheets logging only)
- `SHEETS_ID` - Google Sheets ID for execution logging
  - Header row is automatically added on first run: `Date | Seed | Music Prompt | BG Image Prompt | Thumbnail Prompt | Drive URL | YouTube URL | Status`

**Optional (for notifications)**:
- `DISCORD_WEBHOOK_URL` - Discord webhook for success/error notifications

**Configuration defaults** (in `scripts/config.py`, rarely need to override):
- `LOWPASS_HZ=4000` - Audio lowpass filter frequency
- `TARGET_MINUTES=90` - Target video duration
- `CROSSFADE_SECONDS=12` - Audio loop crossfade duration
- `YOUTUBE_PRIVACY=public` - YouTube video privacy setting
- `KIEAI_NANOBANANA_BG_MODEL=google/nano-banana` - Background image model (no text, uses image_size parameter)
- `KIEAI_NANOBANANA_THUMB_MODEL=nano-banana-pro` - Thumbnail model (supports Japanese text, uses aspect_ratio+resolution)
- See `.env.example` for full list

## Running Locally
```bash
pip install -r requirements.txt
PYTHONPATH=. python scripts/run_pipeline.py
```

## Notes
- ffmpeg is required for video rendering.
- Output files are written under `output/YYYYMMDD/`.
