# uconvert

`uconvert` is a local command-line file converter built with Python.

It supports image, document, PDF, audio/video, ebook and GIS conversions by orchestrating external tools such as Pillow, LibreOffice, Pandoc, Typst, FFmpeg, GDAL, Calibre, Ghostscript and qpdf.

## Features

- Image conversion: PNG, JPG, JPEG, WEBP, BMP, TIFF.
- Image to PDF.
- Multiple images to one PDF.
- Office documents to PDF using LibreOffice or Microsoft Word on Windows.
- Markdown, HTML and text conversion using Pandoc.
- Audio and video conversion using FFmpeg.
- Ebook conversion using Calibre.
- GIS conversion using GDAL/ogr2ogr.
- PDF merge and split.
- PDF compression using Ghostscript.
- PDF linearization, encryption and decryption using qpdf.

## Installation

Create and activate a virtual environment:

~~~powershell
python -m venv .venv
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

## Basic usage

Convert one file:

~~~powershell
uconvert convert input.png output.jpg
uconvert convert input.webp output.pdf
uconvert convert document.docx document.pdf
uconvert convert video.mp4 audio.mp3
uconvert convert map.kml map.geojson
~~~

Show supported formats:

~~~powershell
uconvert formats
~~~

## Image examples

~~~powershell
uconvert convert image.png image.jpg
uconvert convert image.webp image.png
uconvert convert image.png image.pdf
uconvert images-to-pdf output.pdf page1.jpg page2.png page3.webp
~~~

## Document examples

~~~powershell
uconvert convert document.docx document.pdf
uconvert convert README.md README.pdf
uconvert convert README.md README.html
~~~

Office document conversion requires LibreOffice or Microsoft Word on Windows.

Markdown to PDF requires Pandoc and a PDF engine such as Typst.

## Audio and video examples

~~~powershell
uconvert convert video.mov video.mp4
uconvert convert video.mp4 audio.mp3
uconvert convert song.wav song.mp3
uconvert convert video.mp4 clip.gif
~~~

These conversions require FFmpeg.

## Ebook examples

~~~powershell
uconvert convert book.epub book.pdf
uconvert convert book.mobi book.epub
uconvert convert book.azw3 book.pdf
~~~

These conversions require Calibre.

## GIS examples

~~~powershell
uconvert convert map.kml map.geojson
uconvert convert map.geojson map.gpkg
uconvert convert map.gml map.geojson
uconvert gis-layers map.kml
uconvert gis-convert map.kml placemarks.geojson --layer "Placemarks"
~~~

These conversions require GDAL/ogr2ogr.

For files with multiple GIS layers, GeoPackage is usually safer than GeoJSON:

~~~powershell
uconvert convert map.kml map.gpkg
~~~

## PDF tools

Merge PDFs:

~~~powershell
uconvert merge-pdf combined.pdf file1.pdf file2.pdf file3.pdf
~~~

Split PDF into pages:

~~~powershell
uconvert split-pdf combined.pdf pages
~~~

Compress PDF:

~~~powershell
uconvert compress-pdf big.pdf small.pdf
uconvert compress-pdf big.pdf small_screen.pdf --quality screen
~~~

Convert PDF pages to images:

~~~powershell
uconvert pdf-to-images input.pdf pages --format png --dpi 200
~~~

Linearize PDF for web usage:

~~~powershell
uconvert linearize-pdf input.pdf output_linear.pdf
~~~

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

## External tools

Some conversions require external tools installed on the system:

| Tool | Used for |
| ---- | -------- |
| LibreOffice | Office documents to PDF |
| Microsoft Word | Better DOC/DOCX to PDF on Windows |
| Pandoc | Markdown, HTML and text conversions |
| Typst | Markdown to PDF through Pandoc |
| FFmpeg | Audio and video conversions |
| GDAL/ogr2ogr | GIS conversions |
| Calibre | Ebook conversions |
| Ghostscript | PDF compression and PDF to images |
| qpdf | PDF encryption, decryption and linearization |

