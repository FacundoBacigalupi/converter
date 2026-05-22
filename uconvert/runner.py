from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class ConversionError(Exception):
    pass


class ToolNotFoundError(ConversionError):
    pass


def require_tool(*names: str) -> str:
    """
    Finds the first available executable from a list of possible names.
    Also checks common Windows installation paths.
    """
    for name in names:
        path = shutil.which(name)
        if path:
            return path

    common_windows_paths = {
        "soffice": [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ],
        "libreoffice": [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ],
        "pandoc": [
            str(Path.home() / r"AppData\Local\Pandoc\pandoc.exe"),
        ],
        "magick": [
            r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe",
        ],
        "ffmpeg": [
            str(Path.home() / r"scoop\apps\ffmpeg\current\bin\ffmpeg.exe"),
            r"C:\ffmpeg\bin\ffmpeg.exe",
        ],
        "gswin64c": [
            r"C:\Program Files\gs\gs10.07.1\bin\gswin64c.exe",
        ],
        "ebook-convert": [
            r"C:\Program Files\Calibre2\ebook-convert.exe",
            r"C:\Program Files (x86)\Calibre2\ebook-convert.exe",
        ],
        "ogr2ogr": [
            r"C:\OSGeo4W\bin\ogr2ogr.exe",
            r"C:\Program Files\QGIS 3.44.8\bin\ogr2ogr.exe",
        ],
        "ogrinfo": [
            r"C:\OSGeo4W\bin\ogrinfo.exe",
            r"C:\Program Files\QGIS 3.44.8\bin\ogrinfo.exe",
        ],
        "qpdf": [
            r"C:\Program Files\qpdf 12.3.2\bin\qpdf.exe",
        ],
    }

    for name in names:
        for candidate in common_windows_paths.get(name.lower(), []):
            candidate_path = Path(candidate)
            if candidate_path.exists():
                return str(candidate_path)

    raise ToolNotFoundError(
        f"Required tool not found. Tried: {', '.join(names)}"
    )


def run_command(
    args: list[str],
    timeout: int = 120,
    env_extra: dict[str, str] | None = None,
) -> None:
    """
    Runs an external command safely without shell=True.
    Allows extra environment variables for tools like GDAL/OGR.
    """
    env = os.environ.copy()

    if env_extra:
        env.update(env_extra)

    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise ConversionError(f"Command timed out after {timeout} seconds.") from exc

    if result.returncode != 0:
        raise ConversionError(
            "Command failed:\n"
            f"Command: {' '.join(args)}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )


def ensure_input_file(path: Path) -> None:
    if not path.exists():
        raise ConversionError(f"Input file does not exist: {path}")

    if not path.is_file():
        raise ConversionError(f"Input path is not a file: {path}")


def ensure_output_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def run_command_capture(
    args: list[str],
    timeout: int = 120,
    env_extra: dict[str, str] | None = None,
) -> str:
    """
    Runs an external command and returns stdout.
    """
    env = os.environ.copy()

    if env_extra:
        env.update(env_extra)

    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise ConversionError(f"Command timed out after {timeout} seconds.") from exc

    if result.returncode != 0:
        raise ConversionError(
            "Command failed:\n"
            f"Command: {' '.join(args)}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    return result.stdout