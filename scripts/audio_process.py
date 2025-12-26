import random

from pydub import AudioSegment


def process_audio(
    input_path,
    output_path,
    target_minutes,
    variance_minutes,
    lowpass_hz,
    crossfade_seconds,
    fadeout_seconds,
):
    audio = AudioSegment.from_file(input_path)
    filtered = audio.low_pass_filter(lowpass_hz)

    target_ms = (
        target_minutes * 60 * 1000
        + random.randint(-variance_minutes, variance_minutes) * 60 * 1000
    )
    crossfade_ms = crossfade_seconds * 1000

    combined = filtered
    while len(combined) < target_ms:
        combined = combined.append(filtered, crossfade=crossfade_ms)

    combined = combined[:target_ms]
    combined = combined.fade_out(fadeout_seconds * 1000)
    combined.export(output_path, format="wav")

    return output_path, target_ms
