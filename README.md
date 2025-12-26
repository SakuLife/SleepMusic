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

## Secrets / Environment Variables
Required:
- `KIEAI_API_KEY`
- `GCP_SERVICE_ACCOUNT_JSON` (service account JSON string)
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

Optional (defaults provided when empty):
- `KIEAI_API_BASE` (default: `https://api.kie.ai`)
- `KIEAI_SUNO_ENDPOINT` (default: `/api/v1/generate`)
- `KIEAI_NANOBANANA_ENDPOINT` (default: `/api/v1/jobs/createTask`)
- `DRIVE_FOLDER_ID`
- `SHEETS_ID`
- `SHEETS_RANGE` (default: `Sheet1!A1`)
- `DISCORD_WEBHOOK_URL`
- `YOUTUBE_PRIVACY` (default: `public`)
- `MAX_RETRIES` (default: `2`)
- `TARGET_MINUTES` (default: `90`)
- `TARGET_VARIANCE_MINUTES` (default: `5`)
- `LOWPASS_HZ` (default: `8000`)
- `CROSSFADE_SECONDS` (default: `12`)
- `FADEOUT_SECONDS` (default: `5`)

## Running Locally
```bash
pip install -r requirements.txt
python scripts/run_pipeline.py
```

## Notes
- ffmpeg is required for video rendering.
- Output files are written under `output/YYYYMMDD/`.
