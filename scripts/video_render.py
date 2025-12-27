import subprocess


def render_video(bg_path, audio_path, output_path, width=1920, height=1080):
    # Subtle Ken Burns effect: very slow zoom + pan
    # For 92-minute video (138000 frames at 25fps):
    # - Zoom from 1.0 to 1.03 (3% zoom)
    # - Pan slowly from top-left to bottom-right
    video_filter = (
        f"scale={int(width*1.1)}:{int(height*1.1)}:force_original_aspect_ratio=increase,"  # Scale up 10% for panning room
        f"zoompan="
        f"z='min(1+0.0003*on/25,1.03)':"  # Zoom: 1.0 -> 1.03 over 92 minutes
        f"x='iw/2-(iw/zoom/2)+sin(on/25/100)*20':"  # Subtle horizontal movement
        f"y='ih/2-(ih/zoom/2)+on/25/100*0.5':"  # Very slow downward pan
        f"d=1:"
        f"s={width}x{height}:"
        f"fps=25"
    )

    command = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        bg_path,
        "-i",
        audio_path,
        "-vf",
        video_filter,
        "-c:v",
        "libx264",
        "-preset",
        "medium",  # Changed from stillimage tune for motion
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        output_path,
    ]
    subprocess.run(command, check=True)
    return output_path
