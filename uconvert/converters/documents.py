from __future__ import annotations

import platform
import shutil
import tempfile
from pathlib import Path

from uconvert.runner import (
    ConversionError,
    ensure_input_file,
    ensure_output_parent,
    require_tool,
    run_command,
)


OFFICE_FORMATS = {
    "doc",
    "docx",
    "odt",
    "rtf",
    "ppt",
    "pptx",
    "odp",
    "xls",
    "xlsx",
    "ods",
}

PANDOC_INPUT_FORMATS = {
    "md",
    "markdown",
    "html",
    "htm",
    "txt",
    "rst",
    "tex",
}

PANDOC_OUTPUT_FORMATS = {
    "pdf",
    "docx",
    "html",
    "md",
    "markdown",
    "txt",
}


def word_to_pdf(input_path: Path, output_path: Path) -> None:
    """
    Converts DOC/DOCX to PDF using Microsoft Word on Windows.
    This usually gives better results than LibreOffice for Word documents.
    """
    if platform.system() != "Windows":
        raise ConversionError("Microsoft Word conversion is only available on Windows.")

    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        raise ConversionError(
            "pywin32 is required for Microsoft Word conversion. Run: pip install pywin32"
        ) from exc

    input_abs = str(input_path.resolve())
    output_abs = str(output_path.resolve())

    pythoncom.CoInitialize()

    word = None
    doc = None

    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0

        doc = word.Documents.Open(
            input_abs,
            ReadOnly=True,
            AddToRecentFiles=False,
        )

        doc.SaveAs(
            output_abs,
            FileFormat=17,  # wdFormatPDF
        )

    except Exception as exc:
        raise ConversionError(f"Microsoft Word failed to convert the file: {exc}") from exc

    finally:
        if doc is not None:
            doc.Close(False)

        if word is not None:
            word.Quit()

        pythoncom.CoUninitialize()


def office_to_pdf(input_path: Path, output_path: Path, timeout: int = 120) -> None:
    """
    Converts Office documents to PDF.

    On Windows, DOC/DOCX uses Microsoft Word if available.
    Other Office files use LibreOffice.
    """
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    if output_path.suffix.lower() != ".pdf":
        raise ConversionError("Office documents are currently only supported as input → PDF.")

    in_ext = input_path.suffix.lower().lstrip(".")

    if in_ext in {"doc", "docx"} and platform.system() == "Windows":
        try:
            word_to_pdf(input_path, output_path)
            return
        except ConversionError:
            pass

    tool = require_tool("soffice", "libreoffice")

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)

        run_command(
            [
                tool,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(tmp_dir),
                str(input_path),
            ],
            timeout=timeout,
        )

        expected_pdf = tmp_dir / f"{input_path.stem}.pdf"

        if not expected_pdf.exists():
            found = list(tmp_dir.glob("*.pdf"))
            if not found:
                raise ConversionError("LibreOffice did not produce a PDF file.")
            expected_pdf = found[0]

        shutil.move(str(expected_pdf), str(output_path))


def pandoc_convert(input_path: Path, output_path: Path, timeout: int = 120) -> None:
    """
    Converts Markdown/HTML/Text/LaTeX-like files using Pandoc.
    Requires Pandoc installed.
    """
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    in_ext = input_path.suffix.lower().lstrip(".")
    out_ext = output_path.suffix.lower().lstrip(".")

    if in_ext not in PANDOC_INPUT_FORMATS:
        raise ConversionError(f"Unsupported Pandoc input format: {in_ext}")

    if out_ext not in PANDOC_OUTPUT_FORMATS:
        raise ConversionError(f"Unsupported Pandoc output format: {out_ext}")

    tool = require_tool("pandoc")

    command = [
        tool,
        str(input_path),
        "-o",
        str(output_path),
    ]

    if out_ext == "pdf":
        typst_path = shutil.which("typst")

        if not typst_path:
            raise ConversionError(
                "PDF conversion requires Typst or LaTeX. "
                "Typst seems installed, but this terminal cannot find it. "
                "Close PowerShell, open it again, activate the venv, and try: typst --version"
            )

        command.extend(["--pdf-engine", typst_path])

    run_command(
        command,
        timeout=timeout,
    )