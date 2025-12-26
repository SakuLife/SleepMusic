import subprocess


def render_video(bg_path, audio_path, output_path, width=1920, height=1080):
    scale_filter = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
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
        scale_filter,
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
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
