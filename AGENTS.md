# Repository Guidelines

## Project Structure & Module Organization
- `scripts/`: Python modules for the pipeline (API calls, audio processing, video rendering, uploads).
- `config/templates.json`: JP/EN prompt and title/description templates.
- `.github/workflows/`: GitHub Actions cron workflow.
- `output/YYYYMMDD/`: Generated assets (audio, images, video). This is gitignored.
- `README.md`: Setup and environment variables.

## Build, Test, and Development Commands
- `pip install -r requirements.txt`: install Python dependencies.
- `python scripts/run_pipeline.py`: run the full pipeline locally (requires `ffmpeg` and API keys).
- `python scripts/get_youtube_token.py`: obtain and store the YouTube refresh token in `.env`.

## Coding Style & Naming Conventions
- Python: 4-space indentation, follow PEP 8 naming (`snake_case` for functions/vars).
- Keep modules small and single-purpose (e.g., `upload_drive.py`, `audio_process.py`).
- Config values live in `.env`; do not hardcode secrets in code or docs.

## Testing Guidelines
- No automated tests yet. If adding tests, prefer `pytest` and place them under `tests/`.
- Name tests `test_*.py` and keep fixtures minimal.

## Commit & Pull Request Guidelines
- No strict commit convention found. Use clear, imperative messages (e.g., "Add YouTube token helper").
- PRs should include: summary of changes, how to run/verify, and any new env vars.

## Security & Configuration Tips
- Store secrets in `.env` locally and GitHub Actions Secrets in CI.
- Never commit `GCP_SERVICE_ACCOUNT_JSON`, API keys, or refresh tokens.
