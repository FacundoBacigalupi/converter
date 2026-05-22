from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader, PdfWriter

from uconvert.runner import ConversionError, ensure_input_file, ensure_output_parent


def merge_pdfs(input_paths: list[Path], output_path: Path) -> None:
    if not input_paths:
        raise ConversionError("No input PDFs provided.")

    ensure_output_parent(output_path)

    writer = PdfWriter()

    for path in input_paths:
        ensure_input_file(path)

        if path.suffix.lower() != ".pdf":
            raise ConversionError(f"Not a PDF file: {path}")

        reader = PdfReader(str(path))

        for page in reader.pages:
            writer.add_page(page)

    with output_path.open("wb") as f:
        writer.write(f)


def split_pdf(input_path: Path, output_dir: Path) -> None:
    ensure_input_file(input_path)

    if input_path.suffix.lower() != ".pdf":
        raise ConversionError(f"Not a PDF file: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(input_path))

    for index, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)

        output_file = output_dir / f"page_{index:03}.pdf"

        with output_file.open("wb") as f:
            writer.write(f)