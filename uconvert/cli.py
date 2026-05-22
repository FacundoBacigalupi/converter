from __future__ import annotations

import argparse
import sys
from pathlib import Path

from uconvert import __version__
from uconvert.registry import convert_file, supported_formats_text
from uconvert.runner import ConversionError
from uconvert.converters.images import images_to_pdf
from uconvert.converters.pdf_tools import merge_pdfs, split_pdf
from uconvert.converters.ghostscript import compress_pdf, pdf_to_images
from uconvert.converters.gis import gis_convert, list_gis_layers
from uconvert.converters.qpdf_tools import (
    linearize_pdf,
    encrypt_pdf,
    decrypt_pdf,
)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uconvert",
        description="Simple CLI file converter."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "version",
        help="Show uconvert version."
    )

    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert one file into another format."
    )
    convert_parser.add_argument("input", type=Path)
    convert_parser.add_argument("output", type=Path)
    convert_parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds for external tools."
    )

    images_pdf_parser = subparsers.add_parser(
        "images-to-pdf",
        help="Convert multiple images into one PDF."
    )
    images_pdf_parser.add_argument("output", type=Path)
    images_pdf_parser.add_argument("inputs", type=Path, nargs="+")

    merge_parser = subparsers.add_parser(
        "merge-pdf",
        help="Merge multiple PDF files into one PDF."
    )
    merge_parser.add_argument("output", type=Path)
    merge_parser.add_argument("inputs", type=Path, nargs="+")

    split_parser = subparsers.add_parser(
        "split-pdf",
        help="Split a PDF into one PDF file per page."
    )
    split_parser.add_argument("input", type=Path)
    split_parser.add_argument("output_dir", type=Path)

    compress_parser = subparsers.add_parser(
        "compress-pdf",
        help="Compress a PDF using Ghostscript."
    )
    compress_parser.add_argument("input", type=Path)
    compress_parser.add_argument("output", type=Path)
    compress_parser.add_argument(
        "--quality",
        choices=["screen", "ebook", "printer", "prepress"],
        default="ebook",
        help="Compression quality preset."
    )
    compress_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds."
    )

    pdf_images_parser = subparsers.add_parser(
        "pdf-to-images",
        help="Convert each PDF page into an image."
    )
    pdf_images_parser.add_argument("input", type=Path)
    pdf_images_parser.add_argument("output_dir", type=Path)
    pdf_images_parser.add_argument(
        "--format",
        choices=["png", "jpg", "jpeg"],
        default="png",
        help="Output image format."
    )
    pdf_images_parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Output image resolution."
    )
    pdf_images_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds."
    )

    subparsers.add_parser(
        "formats",
        help="Show supported formats."
    )

    linearize_parser = subparsers.add_parser(
        "linearize-pdf",
        help="Create a web-optimized PDF using qpdf."
    )
    linearize_parser.add_argument("input", type=Path)
    linearize_parser.add_argument("output", type=Path)
    linearize_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds."
    )

    encrypt_parser = subparsers.add_parser(
        "encrypt-pdf",
        help="Encrypt a PDF using qpdf."
    )
    encrypt_parser.add_argument("input", type=Path)
    encrypt_parser.add_argument("output", type=Path)
    encrypt_parser.add_argument("--password", required=True)
    encrypt_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds."
    )

    decrypt_parser = subparsers.add_parser(
        "decrypt-pdf",
        help="Decrypt a PDF using qpdf."
    )
    decrypt_parser.add_argument("input", type=Path)
    decrypt_parser.add_argument("output", type=Path)
    decrypt_parser.add_argument("--password", required=True)
    decrypt_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds."
    )

    gis_layers_parser = subparsers.add_parser(
        "gis-layers",
        help="List layers in a GIS file using ogrinfo."
    )
    gis_layers_parser.add_argument("input", type=Path)
    gis_layers_parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout in seconds."
    )

    gis_convert_parser = subparsers.add_parser(
        "gis-convert",
        help="Convert GIS files with optional layer selection."
    )
    gis_convert_parser.add_argument("input", type=Path)
    gis_convert_parser.add_argument("output", type=Path)
    gis_convert_parser.add_argument(
        "--layer",
        help="Specific layer name to convert."
    )
    gis_convert_parser.add_argument(
        "--skip-failures",
        action="store_true",
        help="Skip layers/features that fail during conversion."
    )
    gis_convert_parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds."
    )

    batch_parser = subparsers.add_parser(
        "batch",
        help="Convert all files in a folder to one output format."
    )
    batch_parser.add_argument("input_dir", type=Path)
    batch_parser.add_argument("output_dir", type=Path)
    batch_parser.add_argument(
        "--to",
        required=True,
        help="Output extension, for example: pdf, jpg, webp, mp3, geojson"
    )
    batch_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search files recursively."
    )
    batch_parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds per file."
    )

    return parser


def batch_convert(
    input_dir: Path,
    output_dir: Path,
    output_ext: str,
    recursive: bool,
    timeout: int,
) -> None:
    if not input_dir.exists():
        raise ConversionError(f"Input directory does not exist: {input_dir}")

    if not input_dir.is_dir():
        raise ConversionError(f"Input path is not a directory: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    output_ext = output_ext.lower().lstrip(".")

    pattern = "**/*" if recursive else "*"
    files = [path for path in input_dir.glob(pattern) if path.is_file()]

    if not files:
        raise ConversionError(f"No files found in: {input_dir}")

    success_count = 0
    fail_count = 0

    for input_file in files:
        output_file = output_dir / f"{input_file.stem}.{output_ext}"

        try:
            convert_file(input_file, output_file, timeout=timeout)
            print(f"OK: {input_file} -> {output_file}")
            success_count += 1

        except ConversionError as exc:
            print(f"FAILED: {input_file}")
            print(f"  {exc}")
            fail_count += 1

    print()
    print(f"Batch finished. Success: {success_count}. Failed: {fail_count}.")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "convert":
            convert_file(args.input, args.output, timeout=args.timeout)
            print(f"OK: {args.input} -> {args.output}")

        elif args.command == "images-to-pdf":
            images_to_pdf(args.inputs, args.output)
            print(f"OK: created {args.output}")

        elif args.command == "merge-pdf":
            merge_pdfs(args.inputs, args.output)
            print(f"OK: created {args.output}")

        elif args.command == "split-pdf":
            split_pdf(args.input, args.output_dir)
            print(f"OK: pages written to {args.output_dir}")

        elif args.command == "compress-pdf":
            compress_pdf(
                args.input,
                args.output,
                quality=args.quality,
                timeout=args.timeout,
            )
            print(f"OK: compressed {args.input} -> {args.output}")

        elif args.command == "pdf-to-images":
            pdf_to_images(
                args.input,
                args.output_dir,
                image_format=args.format,
                dpi=args.dpi,
                timeout=args.timeout,
            )
            print(f"OK: images written to {args.output_dir}")

        elif args.command == "linearize-pdf":
            linearize_pdf(args.input, args.output, timeout=args.timeout)
            print(f"OK: linearized {args.input} -> {args.output}")

        elif args.command == "encrypt-pdf":
            encrypt_pdf(
                args.input,
                args.output,
                password=args.password,
                timeout=args.timeout,
            )
            print(f"OK: encrypted {args.input} -> {args.output}")

        elif args.command == "decrypt-pdf":
            decrypt_pdf(
                args.input,
                args.output,
                password=args.password,
                timeout=args.timeout,
            )
            print(f"OK: decrypted {args.input} -> {args.output}")

        elif args.command == "gis-layers":
            output = list_gis_layers(args.input, timeout=args.timeout)
            print(output)

        elif args.command == "gis-convert":
            gis_convert(
                args.input,
                args.output,
                timeout=args.timeout,
                layer=args.layer,
                skip_failures=args.skip_failures,
            )
            print(f"OK: {args.input} -> {args.output}")

        elif args.command == "batch":
            batch_convert(
                args.input_dir,
                args.output_dir,
                output_ext=args.to,
                recursive=args.recursive,
                timeout=args.timeout,
            )

        elif args.command == "version":
            print(f"uconvert {__version__}")

        elif args.command == "formats":
            print(supported_formats_text())

    except ConversionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        print("Cancelled.", file=sys.stderr)
        sys.exit(130)