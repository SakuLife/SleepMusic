"""Test script to generate and process audio with new settings"""
import json
import os
import random
import shutil
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

from scripts.audio_process import process_audio
from scripts.config import load_settings
from scripts.kieai_client import KieAIClient
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

    # Build prompts
    prompt_jp = templates["suno_prompt_jp"].format(
        season_jp=season["jp"], mood_jp=mood["jp"]
    )
    prompt_en = templates["suno_prompt_en"].format(
        season_en=season["en"], mood_en=mood["en"]
    )
    suno_prompt = f"{prompt_jp}\n{prompt_en}"

    # Create output directory with timestamp
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("output", f"test_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    raw_audio = os.path.join(output_dir, "audio_raw.wav")
    processed_audio = os.path.join(output_dir, "audio_90m.wav")
    bg_path = os.path.join(output_dir, "bg.png")
    video_path = os.path.join(output_dir, "video.mp4")

    # Copy existing images from latest output
    latest_output = os.path.join("output", "20251225")
    if os.path.exists(latest_output):
        shutil.copy(os.path.join(latest_output, "bg.png"), bg_path)
        print(f"Copied existing background image to {bg_path}")
    else:
        print("Warning: No existing images found, will need to generate them")

    # Generate audio
    print(f"Generating audio with prompt: {suno_prompt}")
    print(f"Seed: {seed}")
    client = KieAIClient(
        api_key=settings["kieai_api_key"],
        api_base=settings["kieai_api_base"],
        suno_endpoint=settings["kieai_suno_endpoint"],
        nanobanana_endpoint=settings["kieai_nanobanana_endpoint"],
    )

    audio_url = retry_call(
        lambda: client.generate_suno(suno_prompt, seed),
        max_retries=settings["max_retries"],
    )
    download_file(audio_url, raw_audio)
    print(f"Downloaded raw audio to {raw_audio}")

    # Process audio with new settings
    print(f"\nProcessing audio with settings:")
    print(f"  Target: {settings['target_minutes']} minutes")
    print(f"  Lowpass: {settings['lowpass_hz']} Hz")
    print(f"  Crossfade: {settings['crossfade_seconds']} seconds")
    print(f"  Fadeout: {settings['fadeout_seconds']} seconds")

    process_audio(
        raw_audio,
        processed_audio,
        settings["target_minutes"],
        settings["target_variance_minutes"],
        settings["lowpass_hz"],
        settings["crossfade_seconds"],
        settings["fadeout_seconds"],
    )
    print(f"Processed audio saved to {processed_audio}")

    # Render video with existing background
    if os.path.exists(bg_path):
        print(f"\nRendering video...")
        render_video(bg_path, processed_audio, video_path)
        print(f"Video saved to {video_path}")
    else:
        print("Skipping video rendering (no background image)")

    print(f"\nTest complete!")
    print(f"Output directory: {output_dir}")
    print(f"Lowpass filter: {settings['lowpass_hz']} Hz (previous: 8000 Hz)")


if __name__ == "__main__":
    main()
