from __future__ import annotations

import shutil
from pathlib import Path

from uconvert.runner import ConversionError, ensure_input_file, ensure_output_parent
from uconvert.converters.images import IMAGE_FORMATS, convert_image
from uconvert.converters.documents import (
    OFFICE_FORMATS,
    PANDOC_INPUT_FORMATS,
    PANDOC_OUTPUT_FORMATS,
    office_to_pdf,
    pandoc_convert,
)
from uconvert.converters.imagemagick import (
    IMAGEMAGICK_INPUT_FORMATS,
    IMAGEMAGICK_OUTPUT_FORMATS,
    imagemagick_convert,
)
from uconvert.converters.media import (
    MEDIA_INPUT_FORMATS,
    MEDIA_OUTPUT_FORMATS,
    ffmpeg_convert,
)
from uconvert.converters.ebooks import (
    EBOOK_INPUT_FORMATS,
    EBOOK_OUTPUT_FORMATS,
    ebook_convert,
)

from uconvert.converters.gis import (
    GIS_INPUT_FORMATS,
    GIS_OUTPUT_FORMATS,
    gis_convert,
)


def convert_file(input_path: Path, output_path: Path, timeout: int = 120) -> None:
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    in_ext = input_path.suffix.lower().lstrip(".")
    out_ext = output_path.suffix.lower().lstrip(".")

    if not in_ext:
        raise ConversionError("Input file has no extension.")

    if not out_ext:
        raise ConversionError("Output file has no extension.")

    if in_ext == out_ext:
        shutil.copyfile(input_path, output_path)
        return

    if in_ext in IMAGE_FORMATS and (out_ext in IMAGE_FORMATS or out_ext == "pdf"):
        convert_image(input_path, output_path)
        return

    if in_ext in OFFICE_FORMATS and out_ext == "pdf":
        office_to_pdf(input_path, output_path, timeout=timeout)
        return

    if in_ext in PANDOC_INPUT_FORMATS and out_ext in PANDOC_OUTPUT_FORMATS:
        pandoc_convert(input_path, output_path, timeout=timeout)
        return
    
    if in_ext in IMAGEMAGICK_INPUT_FORMATS and out_ext in IMAGEMAGICK_OUTPUT_FORMATS:
        imagemagick_convert(input_path, output_path, timeout=timeout)
        return

    if in_ext in MEDIA_INPUT_FORMATS and out_ext in MEDIA_OUTPUT_FORMATS:
        ffmpeg_convert(input_path, output_path, timeout=timeout)
        return

    if in_ext in EBOOK_INPUT_FORMATS and out_ext in EBOOK_OUTPUT_FORMATS:
        ebook_convert(input_path, output_path, timeout=timeout)
        return

    if in_ext in GIS_INPUT_FORMATS and out_ext in GIS_OUTPUT_FORMATS:
        gis_convert(input_path, output_path, timeout=timeout)
        return

    raise ConversionError(
        f"Unsupported conversion: .{in_ext} → .{out_ext}"
    )


def supported_formats_text() -> str:
    return """
Supported initial conversions:

Images:
  png, jpg, jpeg, webp, bmp, tif, tiff
  → png, jpg, jpeg, webp, bmp, tif, tiff, pdf

Office documents, requires LibreOffice:
  doc, docx, odt, rtf, ppt, pptx, odp, xls, xlsx, ods
  → pdf

Pandoc documents, requires Pandoc:
  md, markdown, html, htm, txt, rst, tex
  → pdf, docx, html, md, markdown, txt

PDF tools:
  merge PDFs
  split PDF into pages

ImageMagick, requires ImageMagick:
  heic, heif, avif, svg, ico, psd, eps, pdf
  → png, jpg, jpeg, webp, bmp, tif, tiff, pdf, ico

Media, requires FFmpeg:
  mp4, mov, mkv, webm, avi, flv, wmv
  mp3, wav, flac, m4a, aac, ogg
  → mp4, webm, mp3, wav, flac, m4a, aac, ogg, gif

Ghostscript PDF tools, requires Ghostscript:
  compress PDF
  PDF → images

Ebooks, requires Calibre:
  epub, mobi, azw3, fb2, txt, html, htm, pdf
  → epub, mobi, azw3, pdf, txt

GIS, requires GDAL/ogr2ogr:
  shp, geojson, json, gpkg, kml, gml
  → shp, geojson, json, gpkg, kml, gml

qpdf PDF tools, requires qpdf:
  linearize PDF
  encrypt PDF
  decrypt PDF
"""