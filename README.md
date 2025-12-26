# SleepMusic Pipeline

Automated daily pipeline to generate sleep BGM, create images, render a video, save to Drive/Sheets, and upload to YouTube.

## Structure
- `scripts/run_pipeline.py`: Orchestrates the end-to-end flow
- `scripts/`: API clients and processing utilities
- `config/templates.json`: Text templates and prompt seeds
- `.github/workflows/daily.yml`: GitHub Actions schedule

## Requirements
- Python 3.11+
- ffmpeg available on PATH

## Required Secrets (GitHub Actions / Environment Variables)

**Minimum required (for YouTube upload only)**:
- `KIEAI_API_KEY` - KieAI API key for Suno and Nano Banana
- `YOUTUBE_CLIENT_ID` - YouTube OAuth2 client ID
- `YOUTUBE_CLIENT_SECRET` - YouTube OAuth2 client secret
- `YOUTUBE_REFRESH_TOKEN` - YouTube OAuth2 refresh token

**Optional (for Drive backup and Sheets logging)**:
- `GCP_SERVICE_ACCOUNT_JSON` - Full GCP service account JSON
- `DRIVE_FOLDER_ID` - Google Drive **shared drive** folder ID (service accounts cannot use personal Drive)
- `SHEETS_ID` - Google Sheets ID for execution logging

**Optional (for notifications)**:
- `DISCORD_WEBHOOK_URL` - Discord webhook for success/error notifications

**Configuration defaults** (in `scripts/config.py`, rarely need to override):
- `LOWPASS_HZ=4000` - Audio lowpass filter frequency
- `TARGET_MINUTES=90` - Target video duration
- `CROSSFADE_SECONDS=12` - Audio loop crossfade duration
- `YOUTUBE_PRIVACY=public` - YouTube video privacy setting
- See `.env.example` for full list

## Running Locally
```bash
pip install -r requirements.txt
PYTHONPATH=. python scripts/run_pipeline.py
```

## Notes
- ffmpeg is required for video rendering.
- Output files are written under `output/YYYYMMDD/`.
