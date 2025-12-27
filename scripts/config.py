import json
import os


def get_env(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def load_json_env(name, required=False):
    raw = get_env(name, required=required)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        # Show first 100 chars to help debug
        preview = raw[:100] + "..." if len(raw) > 100 else raw
        raise RuntimeError(
            f"Invalid JSON in env var: {name}\n"
            f"Preview: {preview}\n"
            f"Error: {exc}"
        ) from exc


def load_settings():
    return {
        "kieai_api_key": get_env("KIEAI_API_KEY", required=True),
        "kieai_api_base": get_env("KIEAI_API_BASE", "https://api.kie.ai"),
        "kieai_suno_endpoint": get_env("KIEAI_SUNO_ENDPOINT", "/api/v1/generate"),
        "kieai_nanobanana_endpoint": get_env(
            "KIEAI_NANOBANANA_ENDPOINT", "/api/v1/jobs/createTask"
        ),
        "kieai_nanobanana_model": get_env(
            "KIEAI_NANOBANANA_MODEL", "google/nano-banana"
        ),
        "drive_folder_id": get_env("DRIVE_FOLDER_ID"),
        "sheets_id": get_env("SHEETS_ID"),
        "sheets_range": get_env("SHEETS_RANGE", "Sheet1!A2"),
        "discord_webhook_url": get_env("DISCORD_WEBHOOK_URL"),
        "gcp_service_account": load_json_env("GCP_SERVICE_ACCOUNT_JSON"),
        "youtube_client_id": get_env("YOUTUBE_CLIENT_ID", required=True),
        "youtube_client_secret": get_env("YOUTUBE_CLIENT_SECRET", required=True),
        "youtube_refresh_token": get_env("YOUTUBE_REFRESH_TOKEN", required=True),
        "youtube_privacy": get_env("YOUTUBE_PRIVACY", "public"),
        "max_retries": int(get_env("MAX_RETRIES", "2")),
        "target_minutes": int(get_env("TARGET_MINUTES", "90")),
        "target_variance_minutes": int(get_env("TARGET_VARIANCE_MINUTES", "5")),
        "lowpass_hz": int(get_env("LOWPASS_HZ", "4000")),
        "crossfade_seconds": int(get_env("CROSSFADE_SECONDS", "12")),
        "fadeout_seconds": int(get_env("FADEOUT_SECONDS", "5")),
    }
