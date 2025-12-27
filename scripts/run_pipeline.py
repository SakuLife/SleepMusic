import json
import os
import random
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from scripts.audio_process import process_audio
from scripts.config import load_settings
from scripts.image_generate import generate_images
from scripts.kieai_client import KieAIClient
from scripts.notify_discord import notify
from scripts.update_sheet import append_row
from scripts.upload_drive import upload_to_drive
from scripts.upload_youtube import set_thumbnail, upload_video
from scripts.utils import retry_call
from scripts.video_render import render_video

JST = timezone(timedelta(hours=9))


def load_templates(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def choose_season(month, seasons):
    if month in (3, 4, 5):
        index = 0
    elif month in (6, 7, 8):
        index = 1
    elif month in (9, 10, 11):
        index = 2
    else:
        index = 3
    return seasons[index]


def build_texts(templates, mood, season, bg_variation, thumb_variation):
    title_jp = random.choice(templates["title_templates"]).format(
        season_jp=season["jp"], mood_jp=mood["jp"]
    )
    title_en = random.choice(templates["title_templates_en"]).format(
        season_en=season["en"], mood_en=mood["en"]
    )
    description_jp = templates["description_template_jp"].format(
        season_jp=season["jp"], mood_jp=mood["jp"]
    )
    description_en = templates["description_template_en"].format(
        season_en=season["en"], mood_en=mood["en"]
    )
    prompt_jp = templates["suno_prompt_jp"].format(
        season_jp=season["jp"], mood_jp=mood["jp"]
    )
    prompt_en = templates["suno_prompt_en"].format(
        season_en=season["en"], mood_en=mood["en"]
    )
    bg_prompt_jp = templates["image_bg_prompt_jp"].format(
        season_jp=season["jp"], mood_jp=mood["jp"], variation=bg_variation
    )
    bg_prompt_en = templates["image_bg_prompt_en"].format(
        season_en=season["en"], mood_en=mood["en"], variation=bg_variation
    )
    thumb_prompt_jp = templates["image_thumb_prompt_jp"].format(
        season_jp=season["jp"], mood_jp=mood["jp"], variation=thumb_variation
    )
    thumb_prompt_en = templates["image_thumb_prompt_en"].format(
        season_en=season["en"], mood_en=mood["en"], variation=thumb_variation
    )

    title = f"{title_jp} / {title_en}"
    description = f"{description_jp}\n\n{description_en}"

    suno_prompt = f"{prompt_jp}\n{prompt_en}"
    bg_prompt = f"{bg_prompt_jp}\n{bg_prompt_en}"
    thumb_prompt = f"{thumb_prompt_jp}\n{thumb_prompt_en}"

    return title, description, suno_prompt, bg_prompt, thumb_prompt


def download_file(url, output_path):
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


def main():
    settings = load_settings()
    templates = load_templates(os.path.join("config", "templates.json"))

    now = datetime.now(JST)
    seed = random.randint(1, 2_147_483_647)
    mood = random.choice(templates["moods"])
    season = choose_season(now.month, templates["seasons"])
    bg_variation = random.choice(templates["image_variations"])
    thumb_variation = random.choice(templates["image_variations"])

    title, description, suno_prompt, bg_prompt, thumb_prompt = build_texts(
        templates, mood, season, bg_variation, thumb_variation
    )

    output_dir = os.path.join("output", now.strftime("%Y%m%d"))
    os.makedirs(output_dir, exist_ok=True)

    raw_audio = os.path.join(output_dir, "audio_raw.wav")
    processed_audio = os.path.join(output_dir, "audio_90m.wav")
    bg_path = os.path.join(output_dir, "bg.png")
    thumb_path = os.path.join(output_dir, "thumb.png")
    video_path = os.path.join(output_dir, "video.mp4")

    client = KieAIClient(
        api_key=settings["kieai_api_key"],
        api_base=settings["kieai_api_base"],
        suno_endpoint=settings["kieai_suno_endpoint"],
        nanobanana_endpoint=settings["kieai_nanobanana_endpoint"],
    )

    audio_url = retry_call(
        lambda: client.generate_suno(suno_prompt, seed, instrumental=True),
        max_retries=settings["max_retries"],
    )
    download_file(audio_url, raw_audio)

    process_audio(
        raw_audio,
        processed_audio,
        settings["target_minutes"],
        settings["target_variance_minutes"],
        settings["lowpass_hz"],
        settings["crossfade_seconds"],
        settings["fadeout_seconds"],
    )

    retry_call(
        lambda: generate_images(
            client, bg_prompt, thumb_prompt, seed, bg_path, thumb_path,
            model=settings["kieai_nanobanana_model"]
        ),
        max_retries=settings["max_retries"],
    )

    render_video(bg_path, processed_audio, video_path)

    # Upload to Drive (optional, requires GCP service account and shared drive)
    drive_url = None
    if settings["gcp_service_account"] and settings["drive_folder_id"]:
        try:
            drive_url = upload_to_drive(
                settings["gcp_service_account"],
                video_path,
                os.path.basename(video_path),
                settings["drive_folder_id"],
            )
            print(f"Uploaded to Drive: {drive_url}")
        except Exception as e:
            print(f"Warning: Drive upload failed (continuing anyway): {e}")
            # Continue pipeline even if Drive upload fails

    # Calculate publish time: today at 20:00 JST
    publish_time = now.replace(hour=20, minute=0, second=0, microsecond=0)
    # If current time is past 20:00, schedule for tomorrow
    if now >= publish_time:
        publish_time += timedelta(days=1)
    # Convert to ISO 8601 format for YouTube API
    publish_at = publish_time.isoformat()
    print(f"Scheduled publish time: {publish_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    video_id = retry_call(
        lambda: upload_video(
            settings["youtube_client_id"],
            settings["youtube_client_secret"],
            settings["youtube_refresh_token"],
            video_path,
            title,
            f"{description}\n\n#sleepmusic #relax #ambient #bedtime",
            templates["tags"],
            privacy_status=settings["youtube_privacy"],
            publish_at=publish_at,
        ),
        max_retries=settings["max_retries"],
    )
    print(f"Video uploaded successfully: https://youtu.be/{video_id}")

    # Set thumbnail (optional, requires verified YouTube account)
    try:
        retry_call(
            lambda: set_thumbnail(
                settings["youtube_client_id"],
                settings["youtube_client_secret"],
                settings["youtube_refresh_token"],
                video_id,
                thumb_path,
            ),
            max_retries=settings["max_retries"],
        )
        print("Thumbnail set successfully")
    except Exception as e:
        print(f"Warning: Thumbnail upload failed (continuing anyway): {e}")
        print("Note: Custom thumbnails require a verified YouTube account")

    youtube_url = f"https://youtu.be/{video_id}"

    # Log to Sheets (optional, requires GCP service account)
    if settings["gcp_service_account"] and settings["sheets_id"]:
        try:
            append_row(
                settings["gcp_service_account"],
                settings["sheets_id"],
                settings["sheets_range"],
                [
                    now.strftime("%Y-%m-%d %H:%M:%S"),
                    seed,
                    suno_prompt,
                    bg_prompt,
                    thumb_prompt,
                    drive_url or "N/A",
                    youtube_url,
                    "success",
                ],
            )
            print(f"Logged to Sheets: {settings['sheets_id']}")
        except Exception as e:
            print(f"Warning: Sheets logging failed (continuing anyway): {e}")

    # Discord notification (optional)
    if settings["discord_webhook_url"]:
        try:
            notify(
                settings["discord_webhook_url"],
                f"Upload complete: {youtube_url}",
            )
        except Exception as e:
            print(f"Warning: Discord notification failed: {e}")


if __name__ == "__main__":
    try:
        main()
        print("\nPipeline completed successfully!")
    except Exception as exc:
        print(f"\nPipeline failed: {exc}")
        webhook = os.getenv("DISCORD_WEBHOOK_URL")
        if webhook:
            try:
                notify(webhook, f"Pipeline failed: {exc}")
            except Exception:
                pass  # Don't fail on notification error
        raise
