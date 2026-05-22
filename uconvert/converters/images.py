from __future__ import annotations

from pathlib import Path
from PIL import Image

from uconvert.runner import ConversionError, ensure_input_file, ensure_output_parent


IMAGE_FORMATS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
    "bmp",
    "tif",
    "tiff",
}


def _normalize_for_pdf_or_jpeg(
    image: Image.Image,
    background: tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    """
    JPEG and PDF do not support transparency properly.

    Instead of simply removing alpha, we place the image over
    a solid background to avoid weird transparent-pixel artifacts.
    Default background: white.
    """
    if image.mode in ("RGBA", "LA"):
        rgba = image.convert("RGBA")

        canvas = Image.new(
            "RGBA",
            rgba.size,
            background + (255,),
        )

        canvas.alpha_composite(rgba)
        return canvas.convert("RGB")

    if image.mode == "P":
        if "transparency" in image.info:
            rgba = image.convert("RGBA")

            canvas = Image.new(
                "RGBA",
                rgba.size,
                background + (255,),
            )

            canvas.alpha_composite(rgba)
            return canvas.convert("RGB")

        return image.convert("RGB")

    if image.mode != "RGB":
        return image.convert("RGB")

    return image


def convert_image(input_path: Path, output_path: Path) -> None:
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    in_ext = input_path.suffix.lower().lstrip(".")
    out_ext = output_path.suffix.lower().lstrip(".")

    if in_ext not in IMAGE_FORMATS:
        raise ConversionError(f"Unsupported input image format: {in_ext}")

    if out_ext not in IMAGE_FORMATS and out_ext != "pdf":
        raise ConversionError(f"Unsupported output image format: {out_ext}")

    with Image.open(input_path) as img:
        if out_ext == "pdf":
            final_img = _normalize_for_pdf_or_jpeg(img)
            final_img.save(output_path, "PDF")
            return

        if out_ext in ("jpg", "jpeg"):
            img = _normalize_for_pdf_or_jpeg(img)
            img.save(output_path, "JPEG", quality=95, optimize=True)
            return

        img.save(output_path)


def images_to_pdf(input_paths: list[Path], output_path: Path) -> None:
    if not input_paths:
        raise ConversionError("No input images provided.")

    ensure_output_parent(output_path)

    images: list[Image.Image] = []

    try:
        for path in input_paths:
            ensure_input_file(path)

            ext = path.suffix.lower().lstrip(".")
            if ext not in IMAGE_FORMATS:
                raise ConversionError(f"Unsupported image format: {path}")

            img = Image.open(path)
            img = _normalize_for_pdf_or_jpeg(img)
            images.append(img)

        first = images[0]
        rest = images[1:]

        first.save(
            output_path,
            "PDF",
            save_all=True,
            append_images=rest,
        )

    finally:
        for img in images:
            img.close()