from __future__ import annotations

from pathlib import Path

from uconvert.runner import (
    ConversionError,
    ensure_input_file,
    ensure_output_parent,
    require_tool,
    run_command,
)


EBOOK_INPUT_FORMATS = {
    "epub",
    "mobi",
    "azw3",
    "fb2",
    "txt",
    "html",
    "htm",
    "pdf",
}

EBOOK_OUTPUT_FORMATS = {
    "epub",
    "mobi",
    "azw3",
    "pdf",
    "txt",
}


def ebook_convert(input_path: Path, output_path: Path, timeout: int = 600) -> None:
    """
    Converts ebooks using Calibre's ebook-convert.
    """
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    in_ext = input_path.suffix.lower().lstrip(".")
    out_ext = output_path.suffix.lower().lstrip(".")

    if in_ext not in EBOOK_INPUT_FORMATS:
        raise ConversionError(f"Unsupported ebook input format: {in_ext}")

    if out_ext not in EBOOK_OUTPUT_FORMATS:
        raise ConversionError(f"Unsupported ebook output format: {out_ext}")

    tool = require_tool("ebook-convert")

    command = [
        tool,
        str(input_path),
        str(output_path),
    ]

    run_command(command, timeout=timeout)