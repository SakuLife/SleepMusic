# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated daily pipeline that generates 90-minute sleep music videos and uploads them to YouTube. The pipeline:

1. Generates ~4-minute ambient music using Suno AI (KieAI API)
2. Processes audio: applies 4000Hz lowpass filter, loops to 90 minutes with crossfades
3. Generates starry night background images using Nano Banana AI (KieAI API)
4. Renders static video with ffmpeg
5. Uploads to YouTube with auto-generated bilingual (JP/EN) titles and descriptions
6. Backs up to Google Drive and logs to Google Sheets
7. Sends Discord notifications

Runs daily at 20:00 JST via GitHub Actions (`.github/workflows/daily.yml`).

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env with your API keys

# Get YouTube refresh token (one-time setup)
python scripts/get_youtube_token.py
```

### Running

```bash
# Full pipeline (generates music, images, video, uploads everything)
PYTHONPATH=. python scripts/run_pipeline.py

# Test audio generation only (skips image generation and uploads)
PYTHONPATH=. python scripts/test_audio.py
```

Note: `PYTHONPATH=.` is required for the `scripts` module imports to work correctly.

### System Requirements
- **Python 3.11+**
- **ffmpeg** must be on PATH for video rendering
- pydub uses ffmpeg for audio processing

## Architecture

### Pipeline Flow (scripts/run_pipeline.py)

The main pipeline orchestrates these steps in sequence:

1. **Content Generation** (lines 97-104)
   - Selects random mood from templates
   - Chooses season based on current month (3-5: spring, 6-8: summer, etc.)
   - Builds bilingual prompts and titles from `config/templates.json`

2. **Audio Generation** (lines 122-126)
   - Calls KieAI Suno API via `kieai_client.generate_suno()`
   - Suno generates ONE ~4-minute ambient track (not configurable)
   - Downloads raw WAV file

3. **Audio Processing** (lines 128-136)
   - `audio_process.process_audio()` loops the track to 90 minutes
   - Applies 4000Hz lowpass filter for softer sleep-appropriate sound
   - Uses 12-second crossfades between loops
   - Adds 5-second fadeout at end
   - Actual duration: 90 ± 5 minutes (variance for YouTube algorithm)

4. **Image Generation** (lines 138-143)
   - `image_generate.generate_images()` calls Nano Banana API
   - Generates background (16:9, no text) and thumbnail (with text)
   - Prompts use starry night theme + seasonal elements

5. **Video Rendering** (line 145)
   - `video_render.render_video()` uses ffmpeg
   - Creates static video: background image + 90-minute audio
   - Output: 1920x1080 MP4

6. **Upload & Notification** (lines 147-200)
   - Uploads video to Google Drive
   - Uploads to YouTube with metadata
   - Sets custom thumbnail
   - Logs to Google Sheets (timestamp, seed, prompts, URLs)
   - Sends Discord notification

### Key Components

#### KieAI API Client (scripts/kieai_client.py)

**IMPORTANT**: The KieAI Nano Banana API has a specific payload format. Do NOT include `seed`, `with_text`, or `callBackUrl` parameters - these cause 422 errors.

Correct payload (lines 99-106):
```python
payload = {
    "model": "google/nano-banana",
    "input": {
        "prompt": prompt,
        "output_format": "png",
        "image_size": "16:9",
    },
}
```

Both APIs use async task polling:
- Submit task → get taskId
- Poll `/recordInfo` endpoint until status is SUCCESS/success
- Extract URL from response (audio_url for Suno, resultUrls[0] for Nano Banana)

#### Audio Processing (scripts/audio_process.py)

Uses pydub (which wraps ffmpeg) to:
- Apply lowpass filter at configurable Hz (default 4000Hz for sleep music)
- Loop audio with crossfades until reaching target duration
- Trim to exact target duration
- Apply fadeout

**Why 4000Hz lowpass?** High frequencies (above 4kHz) are stimulating; filtering them creates a softer, more sleep-inducing sound. Previous setting of 8000Hz was too "noisy" for sleep.

#### Template System (config/templates.json)

Bilingual (JP/EN) templates with variables:
- `{season_jp}` / `{season_en}`: 春/spring, 夏/summer, 秋/autumn, 冬/winter
- `{mood_jp}` / `{mood_en}`: 穏やか/calm, やさしい/gentle, etc.

Seasons auto-select based on current month (scripts/run_pipeline.py:31-40).

Image prompts (lines 36-39) use starry night base + season variations:
- Winter → snow + stars
- Summer → beach/ocean + stars
- Spring → cherry blossoms + stars
- Autumn → autumn leaves + stars

#### YouTube Upload (scripts/upload_youtube.py)

Uses OAuth2 refresh token (not service account). The refresh token never expires but must be obtained once via `get_youtube_token.py`.

Privacy status defaults to "public" but configurable via `YOUTUBE_PRIVACY` env var.

#### Google Services (scripts/upload_drive.py, scripts/update_sheet.py)

Use GCP service account (NOT OAuth2). The `GCP_SERVICE_ACCOUNT_JSON` env var should contain the entire JSON key file as a string.

Service account needs:
- Drive API enabled with write access to target folder
- Sheets API enabled with edit access to target spreadsheet

## Configuration

### Environment Variables

See `.env.example` for all variables.

**Required Secrets** (must configure in GitHub Secrets or local .env):
- `KIEAI_API_KEY`: KieAI API key for Suno and Nano Banana
- `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`: YouTube OAuth2
- `GCP_SERVICE_ACCOUNT_JSON`: Full GCP service account JSON as string (for Drive/Sheets)

**Optional Secrets** (for backup and logging):
- `DRIVE_FOLDER_ID`: Google Drive **shared drive** folder ID (service accounts cannot upload to personal Drive)
- `SHEETS_ID`: Google Sheets for execution logging
- `DISCORD_WEBHOOK_URL`: Discord notifications

**Configuration Defaults** (defined in `scripts/config.py`, rarely need to override):
- `LOWPASS_HZ=4000`: Lowpass filter cutoff. Lower = softer/darker sound
- `TARGET_MINUTES=90`: Target video length
- `TARGET_VARIANCE_MINUTES=5`: Random variance in duration (for YouTube algorithm)
- `CROSSFADE_SECONDS=12`: Crossfade duration when looping audio
- `FADEOUT_SECONDS=5`: Final fadeout duration
- `YOUTUBE_PRIVACY=public`: Video privacy setting
- `MAX_RETRIES=2`: API retry attempts
- `KIEAI_API_BASE=https://api.kie.ai`: KieAI base URL
- `KIEAI_SUNO_ENDPOINT=/api/v1/generate`: Suno endpoint
- `KIEAI_NANOBANANA_ENDPOINT=/api/v1/jobs/createTask`: Nano Banana endpoint
- `SHEETS_RANGE=Sheet1!A2`: Sheets append range

### Output Structure

```
output/
  YYYYMMDD/              # One folder per day
    audio_raw.wav        # ~4min from Suno
    audio_90m.wav        # Processed 90min loop
    bg.png               # Background image (16:9)
    thumb.png            # Thumbnail image (with text)
    video.mp4            # Final rendered video
  test_YYYYMMDD_HHMMSS/  # Test runs create timestamped folders
    ...
```

Output folder is gitignored.

## Common Issues

### Unicode/Emoji Errors on Windows
Windows console (cp932 encoding) cannot handle emojis in print statements. Use plain text instead.

### ffmpeg Not Found
Video rendering requires ffmpeg on PATH. Install via:
- Windows: `choco install ffmpeg` or download from ffmpeg.org
- macOS: `brew install ffmpeg`
- Linux: `apt-get install ffmpeg`

### KieAI API 422 Errors
Usually means incorrect payload format. For Nano Banana, only send `model` and `input` fields - no `seed`, `with_text`, or `callBackUrl`.

### Google Drive Upload: "Service Accounts do not have storage quota"
Service accounts cannot upload to personal Google Drive. You must:
1. Create a **Shared Drive** in Google Drive (left sidebar → Shared drives → New)
2. Create a folder inside the shared drive (e.g., "output")
3. Add the service account email as a member:
   - Right-click the shared drive → Manage members
   - Add the service account email (found in `GCP_SERVICE_ACCOUNT_JSON` as `client_email`)
   - Grant "Content Manager" or "Manager" role
4. Use the folder ID in `DRIVE_FOLDER_ID` secret
   - Open the folder in Drive, copy the ID from URL: `folders/[FOLDER_ID]`

Alternatively, disable Drive backup by not setting `DRIVE_FOLDER_ID` secret. The pipeline will skip Drive upload and continue normally.

### YouTube Custom Thumbnail Permission Denied
Custom thumbnails require a **verified YouTube account**. If you see "doesn't have permissions to upload and set custom video thumbnails":
1. Verify your YouTube account (requires phone verification)
2. Or disable thumbnail upload by commenting out the `set_thumbnail` call

The pipeline will now continue even if thumbnail upload fails.

### YouTube Account Not Verified for 15+ Minute Videos
**IMPORTANT**: YouTube requires phone verification to upload videos longer than 15 minutes.

To verify your account:
1. Go to https://www.youtube.com/verify
2. Enter your phone number
3. Enter the verification code sent via SMS

This is a **one-time setup** required for all 15+ minute videos. Without verification, uploads will fail with an error.

### YouTube Upload Timeout or "Processing too long" Error
For large videos (90+ minutes), uploads may timeout. The code now uses:
- **Resumable uploads** with 10MB chunks
- **Progress tracking** during upload
- **Automatic retry** for temporary errors (500, 502, 503, 504)
- Up to 10 retries with exponential backoff

If uploads still fail, the video is likely uploaded to YouTube but processing. Check your YouTube Studio dashboard.

### YouTube Upload Quota Exceeded
YouTube API has daily upload quotas. Free tier: 6 uploads/day. Pipeline runs once daily (20:00 JST) to stay within limits.

## Modifying Content

### Changing Music Style
Edit `suno_prompt_jp` and `suno_prompt_en` in `config/templates.json`. Current prompts emphasize:
- Low frequency focus (低音寄り)
- Minimal rhythm (リズム弱め)
- Soothing ambient (柔らかいアンビエント)

### Changing Image Style
Edit `image_bg_prompt_jp/en` and `image_thumb_prompt_jp/en` in `config/templates.json`. Current prompts use starry night theme with seasonal variations.

### Adding Moods or Seasons
Add entries to `moods` or `seasons` arrays in `config/templates.json`. Both require `jp` and `en` fields.

## GitHub Actions

Workflow runs daily at 11:00 UTC (20:00 JST). All env vars must be set as GitHub Secrets.

Manual trigger: Go to Actions tab → daily-sleepmusic → Run workflow

## Testing

No automated tests yet. For manual testing:
- Use `scripts/test_audio.py` to test audio generation without uploads
- Set `YOUTUBE_PRIVACY=unlisted` when testing to avoid public uploads
- Check `pipeline.log` (gitignored) for detailed execution logs
