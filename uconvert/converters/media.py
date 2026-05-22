from __future__ import annotations

from pathlib import Path

from uconvert.runner import (
    ConversionError,
    ensure_input_file,
    ensure_output_parent,
    require_tool,
    run_command,
)


VIDEO_FORMATS = {
    "mp4",
    "mov",
    "mkv",
    "webm",
    "avi",
    "flv",
    "wmv",
}

AUDIO_FORMATS = {
    "mp3",
    "wav",
    "flac",
    "m4a",
    "aac",
    "ogg",
}

MEDIA_INPUT_FORMATS = VIDEO_FORMATS | AUDIO_FORMATS
MEDIA_OUTPUT_FORMATS = VIDEO_FORMATS | AUDIO_FORMATS | {"gif"}


def ffmpeg_convert(input_path: Path, output_path: Path, timeout: int = 600) -> None:
    """
    Converts audio/video files using FFmpeg.
    Also supports extracting audio from video.
    """
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    in_ext = input_path.suffix.lower().lstrip(".")
    out_ext = output_path.suffix.lower().lstrip(".")

    if in_ext not in MEDIA_INPUT_FORMATS:
        raise ConversionError(f"Unsupported media input format: {in_ext}")

    if out_ext not in MEDIA_OUTPUT_FORMATS:
        raise ConversionError(f"Unsupported media output format: {out_ext}")

    tool = require_tool("ffmpeg")

    command = [
        tool,
        "-y",
        "-i",
        str(input_path),
    ]

    if out_ext == "mp3":
        command.extend(["-vn", "-codec:a", "libmp3lame", "-q:a", "2"])

    elif out_ext == "wav":
        command.extend(["-vn", "-codec:a", "pcm_s16le"])

    elif out_ext == "flac":
        command.extend(["-vn", "-codec:a", "flac"])

    elif out_ext in {"m4a", "aac"}:
        command.extend(["-vn", "-codec:a", "aac", "-b:a", "192k"])

    elif out_ext == "ogg":
        command.extend(["-vn", "-codec:a", "libvorbis", "-q:a", "5"])

    elif out_ext == "mp4":
        command.extend(["-codec:v", "libx264", "-preset", "medium", "-crf", "23", "-codec:a", "aac"])

    elif out_ext == "webm":
        command.extend(["-codec:v", "libvpx-vp9", "-crf", "32", "-b:v", "0", "-codec:a", "libopus"])

    elif out_ext == "gif":
        command.extend(["-vf", "fps=12,scale=640:-1:flags=lanczos"])

    command.append(str(output_path))

    run_command(command, timeout=timeout)