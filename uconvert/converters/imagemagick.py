from __future__ import annotations

from pathlib import Path

from uconvert.runner import (
    ConversionError,
    ensure_input_file,
    ensure_output_parent,
    require_tool,
    run_command,
)


IMAGEMAGICK_INPUT_FORMATS = {
    "heic",
    "heif",
    "avif",
    "svg",
    "ico",
    "psd",
    "eps",
    "pdf",
}

IMAGEMAGICK_OUTPUT_FORMATS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
    "bmp",
    "tif",
    "tiff",
    "pdf",
    "ico",
}


def imagemagick_convert(input_path: Path, output_path: Path, timeout: int = 120) -> None:
    """
    Converts formats that Pillow may not handle well using ImageMagick.
    """
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    in_ext = input_path.suffix.lower().lstrip(".")
    out_ext = output_path.suffix.lower().lstrip(".")

    if in_ext not in IMAGEMAGICK_INPUT_FORMATS:
        raise ConversionError(f"Unsupported ImageMagick input format: {in_ext}")

    if out_ext not in IMAGEMAGICK_OUTPUT_FORMATS:
        raise ConversionError(f"Unsupported ImageMagick output format: {out_ext}")

    tool = require_tool("magick")

    command = [
        tool,
        str(input_path),
        str(output_path),
    ]

    run_command(command, timeout=timeout)