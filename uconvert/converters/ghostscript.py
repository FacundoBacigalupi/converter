from __future__ import annotations

from pathlib import Path

from uconvert.runner import (
    ConversionError,
    ensure_input_file,
    ensure_output_parent,
    require_tool,
    run_command,
)


def _ghostscript_tool() -> str:
    return require_tool("gswin64c", "gswin32c", "gs")


def compress_pdf(input_path: Path, output_path: Path, quality: str = "ebook", timeout: int = 300) -> None:
    """
    Compresses a PDF using Ghostscript.

    quality options:
      screen   = lowest quality, smallest size
      ebook    = medium quality
      printer  = high quality
      prepress = very high quality
    """
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    if input_path.suffix.lower() != ".pdf":
        raise ConversionError("Input must be a PDF.")

    if output_path.suffix.lower() != ".pdf":
        raise ConversionError("Output must be a PDF.")

    allowed = {"screen", "ebook", "printer", "prepress"}
    if quality not in allowed:
        raise ConversionError(f"Invalid quality '{quality}'. Use one of: {', '.join(sorted(allowed))}")

    tool = _ghostscript_tool()

    command = [
        tool,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{quality}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        str(input_path),
    ]

    run_command(command, timeout=timeout)


def pdf_to_images(
    input_path: Path,
    output_dir: Path,
    image_format: str = "png",
    dpi: int = 200,
    timeout: int = 300,
) -> None:
    """
    Converts each PDF page into an image using Ghostscript.
    """
    ensure_input_file(input_path)

    if input_path.suffix.lower() != ".pdf":
        raise ConversionError("Input must be a PDF.")

    image_format = image_format.lower()

    if image_format not in {"png", "jpg", "jpeg"}:
        raise ConversionError("Image format must be png, jpg or jpeg.")

    output_dir.mkdir(parents=True, exist_ok=True)

    tool = _ghostscript_tool()

    if image_format == "png":
        device = "png16m"
        pattern = output_dir / "page_%03d.png"
    else:
        device = "jpeg"
        pattern = output_dir / "page_%03d.jpg"

    command = [
        tool,
        f"-sDEVICE={device}",
        f"-r{dpi}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={pattern}",
        str(input_path),
    ]

    run_command(command, timeout=timeout)