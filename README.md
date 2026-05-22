# uconvert

`uconvert` is a local command-line file converter built with Python.

It supports image, document, PDF, audio/video, ebook and GIS conversions by orchestrating external tools such as Pillow, LibreOffice, Pandoc, Typst, FFmpeg, GDAL, Calibre, Ghostscript, ImageMagick and qpdf.

The project can be used in two ways:

1. Locally, by installing Python dependencies and the required external tools on your system.
2. With Docker, where all external tools are already installed inside the image.

## Features

- Image conversion: PNG, JPG, JPEG, WEBP, BMP, TIFF.
- Image to PDF.
- Multiple images to one PDF.
- Office documents to PDF.
- Markdown, HTML and text conversion using Pandoc.
- Audio and video conversion using FFmpeg.
- Ebook conversion using Calibre.
- GIS conversion using GDAL/ogr2ogr.
- PDF merge and split.
- PDF compression using Ghostscript.
- PDF to images using Ghostscript.
- PDF linearization using qpdf.
- PDF encryption and decryption using qpdf.
- Batch conversion by folder.

## Project structure

~~~text
uconvert/
  cli.py
  registry.py
  runner.py
  converters/
    documents.py
    ebooks.py
    ghostscript.py
    gis.py
    images.py
    imagemagick.py
    media.py
    pdf_tools.py
    qpdf_tools.py

tests/
  audiovideo/
  book/
  documentos/
  images/
  map/
  qpdf/
~~~

## Local installation

Create a virtual environment:

~~~powershell
python -m venv .venv
~~~

Activate it on Windows PowerShell:

~~~powershell
.\.venv\Scripts\Activate.ps1
~~~

Install the project in editable mode:

~~~powershell
pip install -e .
~~~

Check that the command works:

~~~powershell
uconvert formats
~~~

## Local external tools

Some conversions require external tools installed on the system.

| Tool | Used for |
| ---- | -------- |
| LibreOffice | Office documents to PDF |
| Microsoft Word | Better DOC/DOCX to PDF on Windows, if available |
| Pandoc | Markdown, HTML and text conversions |
| Typst | Markdown to PDF through Pandoc |
| FFmpeg | Audio and video conversions |
| GDAL/ogr2ogr | GIS conversions |
| Calibre | Ebook conversions |
| Ghostscript | PDF compression and PDF to images |
| ImageMagick | Extra image formats such as AVIF, HEIC, SVG and ICO |
| qpdf | PDF encryption, decryption and linearization |

If you do not want to install all these tools locally, use Docker.

## Docker usage

Docker allows you to use `uconvert` without installing all external tools directly on Windows.

With Docker, your system only needs Docker Desktop. The Docker image contains Python, the project code and the required conversion tools.

Build the image:

~~~powershell
docker build -t uconvert .
~~~

Show supported formats:

~~~powershell
docker run --rm uconvert formats
~~~

Run conversions by mounting the current folder as `/data` inside the container:

~~~powershell
docker run --rm -v "${PWD}:/data" uconvert convert tests/images/image.webp tests/images/out/image.jpg
docker run --rm -v "${PWD}:/data" uconvert convert tests/documentos/doc.docx tests/documentos/doc.pdf
docker run --rm -v "${PWD}:/data" uconvert convert tests/audiovideo/video.mp4 tests/audiovideo/audio.mp3
docker run --rm -v "${PWD}:/data" uconvert convert tests/map/map.kml tests/map/map.geojson
~~~

The container uses `/data` as the working directory.

## Docker limitations

Inside Docker, DOCX to PDF uses LibreOffice.

Microsoft Word conversion is only available when running locally on Windows with Microsoft Word installed.

Because of this, some DOCX files may look slightly different inside Docker than when converted locally with Microsoft Word.

## Basic usage

Show supported formats:

~~~powershell
uconvert formats
~~~

Convert one file:

~~~powershell
uconvert convert input.png output.jpg
uconvert convert input.webp output.pdf
uconvert convert document.docx document.pdf
uconvert convert video.mp4 audio.mp3
uconvert convert map.kml map.geojson
~~~

## Image examples

Convert between image formats:

~~~powershell
uconvert convert image.png image.jpg
uconvert convert image.webp image.png
uconvert convert image.avif image.jpg
uconvert convert icon.svg icon.png
~~~

Convert one image to PDF:

~~~powershell
uconvert convert image.png image.pdf
~~~

Convert multiple images to one PDF:

~~~powershell
uconvert images-to-pdf output.pdf page1.jpg page2.png page3.webp
~~~

## Document examples

Convert Office documents to PDF:

~~~powershell
uconvert convert document.docx document.pdf
uconvert convert presentation.pptx presentation.pdf
uconvert convert spreadsheet.xlsx spreadsheet.pdf
~~~

Convert Markdown or HTML:

~~~powershell
uconvert convert README.md README.pdf
uconvert convert README.md README.html
uconvert convert page.html page.pdf
~~~

Office document conversion uses Microsoft Word on Windows when available for DOC/DOCX files. Otherwise, it uses LibreOffice.

Markdown to PDF uses Pandoc with Typst when available.

## Audio and video examples

Convert video formats:

~~~powershell
uconvert convert video.mov video.mp4
uconvert convert video.mkv video.mp4
uconvert convert video.mp4 video.webm
~~~

Extract audio from video:

~~~powershell
uconvert convert video.mp4 audio.mp3
~~~

Convert audio formats:

~~~powershell
uconvert convert song.wav song.mp3
uconvert convert song.mp3 song.flac
uconvert convert song.wav song.ogg
~~~

Create a GIF from a video:

~~~powershell
uconvert convert video.mp4 clip.gif
~~~

These conversions require FFmpeg.

## Ebook examples

Convert ebooks:

~~~powershell
uconvert convert book.epub book.pdf
uconvert convert book.mobi book.epub
uconvert convert book.azw3 book.pdf
~~~

These conversions require Calibre.

## GIS examples

Convert GIS files:

~~~powershell
uconvert convert map.kml map.geojson
uconvert convert map.geojson map.gpkg
uconvert convert map.gml map.geojson
uconvert convert map.shp map.geojson
~~~

List layers in a GIS file:

~~~powershell
uconvert gis-layers map.kml
~~~

Convert a specific layer:

~~~powershell
uconvert gis-convert map.kml placemarks.geojson --layer "Placemarks"
~~~

For files with multiple GIS layers, GeoPackage is usually safer than GeoJSON:

~~~powershell
uconvert convert map.kml map.gpkg
uconvert convert map.gml map.gpkg
~~~

These conversions require GDAL/ogr2ogr.

## PDF tools

Merge PDFs:

~~~powershell
uconvert merge-pdf combined.pdf file1.pdf file2.pdf file3.pdf
~~~

Split a PDF into one file per page:

~~~powershell
uconvert split-pdf combined.pdf pages
~~~

Compress PDF:

~~~powershell
uconvert compress-pdf big.pdf small.pdf
uconvert compress-pdf big.pdf small_screen.pdf --quality screen
~~~

Compression quality options:

~~~text
screen   = smallest file, lowest quality
ebook    = balanced/default
printer  = better quality, larger file
prepress = high quality, usually larger
~~~

Convert PDF pages to images:

~~~powershell
uconvert pdf-to-images input.pdf pages --format png --dpi 200
uconvert pdf-to-images input.pdf pages --format jpg --dpi 150
~~~

Linearize PDF for web usage:

~~~powershell
uconvert linearize-pdf input.pdf output_linear.pdf
~~~

A linearized PDF is optimized so browsers and PDF viewers can start displaying the first pages before the whole file is downloaded.

Encrypt PDF:

~~~powershell
uconvert encrypt-pdf input.pdf encrypted.pdf --password 1234
~~~

Decrypt PDF:

~~~powershell
uconvert decrypt-pdf encrypted.pdf decrypted.pdf --password 1234
~~~

## Batch conversion

Convert all files in a folder to one output format:

~~~powershell
uconvert batch .\tests\images .\tests\images\out --to jpg
uconvert batch .\tests\documentos .\tests\documentos\out --to pdf
uconvert batch .\tests\audiovideo .\tests\audiovideo\out --to mp3
uconvert batch .\tests\map .\tests\map\out --to geojson
~~~

Recursive batch conversion:

~~~powershell
uconvert batch .\tests .\tests\out --to pdf --recursive
~~~

## Notes

This project does not implement all conversion logic from scratch. Instead, it acts as a clean command-line interface that detects the requested conversion and delegates the work to the best available tool.