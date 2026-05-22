from __future__ import annotations

from pathlib import Path

from uconvert.runner import (
    ConversionError,
    ensure_input_file,
    ensure_output_parent,
    require_tool,
    run_command,
)


def linearize_pdf(input_path: Path, output_path: Path, timeout: int = 300) -> None:
    """
    Creates a web-optimized PDF.

    A linearized PDF can start loading page 1 before the whole file is downloaded.
    """
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    if input_path.suffix.lower() != ".pdf":
        raise ConversionError("Input must be a PDF.")

    if output_path.suffix.lower() != ".pdf":
        raise ConversionError("Output must be a PDF.")

    tool = require_tool("qpdf")

    command = [
        tool,
        "--linearize",
        str(input_path),
        str(output_path),
    ]

    run_command(command, timeout=timeout)


def encrypt_pdf(
    input_path: Path,
    output_path: Path,
    password: str,
    timeout: int = 300,
) -> None:
    """
    Encrypts a PDF with a password.
    """
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    if not password:
        raise ConversionError("Password cannot be empty.")

    if input_path.suffix.lower() != ".pdf":
        raise ConversionError("Input must be a PDF.")

    if output_path.suffix.lower() != ".pdf":
        raise ConversionError("Output must be a PDF.")

    tool = require_tool("qpdf")

    command = [
        tool,
        "--encrypt",
        password,
        password,
        "256",
        "--",
        str(input_path),
        str(output_path),
    ]

    run_command(command, timeout=timeout)


def decrypt_pdf(
    input_path: Path,
    output_path: Path,
    password: str,
    timeout: int = 300,
) -> None:
    """
    Decrypts a PDF when the password is known.
    """
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    if not password:
        raise ConversionError("Password cannot be empty.")

    if input_path.suffix.lower() != ".pdf":
        raise ConversionError("Input must be a PDF.")

    if output_path.suffix.lower() != ".pdf":
        raise ConversionError("Output must be a PDF.")

    tool = require_tool("qpdf")

    command = [
        tool,
        f"--password={password}",
        "--decrypt",
        str(input_path),
        str(output_path),
    ]

    run_command(command, timeout=timeout)