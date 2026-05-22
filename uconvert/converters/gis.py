from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from uconvert.runner import (
    ConversionError,
    ensure_input_file,
    ensure_output_parent,
    require_tool,
    run_command,
    run_command_capture,
)


GIS_INPUT_FORMATS = {
    "shp",
    "geojson",
    "json",
    "gpkg",
    "kml",
    "gml",
}

GIS_OUTPUT_FORMATS = {
    "shp",
    "geojson",
    "json",
    "gpkg",
    "kml",
    "gml",
}


OGR_FORMATS = {
    "shp": "ESRI Shapefile",
    "geojson": "GeoJSON",
    "json": "GeoJSON",
    "gpkg": "GPKG",
    "kml": "KML",
    "gml": "GML",
}


def gis_convert(
    input_path: Path,
    output_path: Path,
    timeout: int = 600,
    layer: str | None = None,
    skip_failures: bool = False,
) -> None:
    """
    Converts vector GIS files using GDAL/ogr2ogr.
    """
    ensure_input_file(input_path)
    ensure_output_parent(output_path)

    in_ext = input_path.suffix.lower().lstrip(".")
    out_ext = output_path.suffix.lower().lstrip(".")

    if in_ext not in GIS_INPUT_FORMATS:
        raise ConversionError(f"Unsupported GIS input format: {in_ext}")

    if out_ext not in GIS_OUTPUT_FORMATS:
        raise ConversionError(f"Unsupported GIS output format: {out_ext}")

    tool = require_tool("ogr2ogr")
    output_format = OGR_FORMATS[out_ext]

    if out_ext == "shp":
        _convert_to_shapefile(tool, input_path, output_path, output_format, timeout)
        return

    _remove_existing_gis_output(output_path, out_ext)

    command = [
        tool,
        "-f",
        output_format,
        str(output_path),
        str(input_path),
    ]

    if skip_failures:
        command.insert(1, "-skipfailures")

    if layer:
        command.append(layer)

    run_command(
        command,
        timeout=timeout,
        env_extra=_gdal_env(tool),
    )


def _convert_to_shapefile(
    tool: str,
    input_path: Path,
    output_path: Path,
    output_format: str,
    timeout: int,
) -> None:
    """
    Shapefile output creates several files:
      .shp, .shx, .dbf, .prj, etc.

    Because of that, we create it in a temp folder and copy all generated files.
    """
    output_dir = output_path.parent
    output_stem = output_path.stem

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        tmp_shp = tmp_dir / f"{output_stem}.shp"

        command = [
            tool,
            "-f",
            output_format,
            str(tmp_shp),
            str(input_path),
        ]

        run_command(
            command,
            timeout=timeout,
            env_extra=_gdal_env(tool),
        )

        generated_files = list(tmp_dir.glob(f"{output_stem}.*"))

        if not generated_files:
            raise ConversionError("GDAL did not produce shapefile output.")

        for file in generated_files:
            shutil.move(str(file), str(output_dir / file.name))


def list_gis_layers(input_path: Path, timeout: int = 120) -> str:
    """
    Returns the layers contained in a GIS file.
    Useful for KML/GML/GPKG files with multiple layers.
    """
    ensure_input_file(input_path)

    tool = require_tool("ogrinfo")

    command = [
        tool,
        "-ro",
        "-so",
        str(input_path),
    ]

    return run_command_capture(command, timeout=timeout)


def _gdal_env(tool: str) -> dict[str, str]:
    """
    Forces ogr2ogr/ogrinfo to use the GDAL and PROJ data from the same QGIS install.
    This avoids conflicts with PostgreSQL/PostGIS proj.db on Windows.
    """
    env: dict[str, str] = {}

    tool_path = Path(tool)
    bin_dir = tool_path.parent
    root_dir = bin_dir.parent

    proj_candidates = [
        root_dir / "share" / "proj",
        root_dir / "apps" / "proj" / "share" / "proj",
    ]

    gdal_candidates = [
        root_dir / "share" / "gdal",
        root_dir / "apps" / "gdal" / "share" / "gdal",
    ]

    for proj_dir in proj_candidates:
        if proj_dir.exists():
            env["PROJ_LIB"] = str(proj_dir)
            env["PROJ_DATA"] = str(proj_dir)
            break

    for gdal_dir in gdal_candidates:
        if gdal_dir.exists():
            env["GDAL_DATA"] = str(gdal_dir)
            break

    env["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")

    return env


def _remove_existing_gis_output(output_path: Path, out_ext: str) -> None:
    """
    Removes previous GIS output before calling ogr2ogr.

    This avoids GeoJSON overwrite errors like:
      DeleteLayer() not supported by this dataset.
    """
    if out_ext == "shp":
        for suffix in [".shp", ".shx", ".dbf", ".prj", ".cpg", ".qix"]:
            candidate = output_path.with_suffix(suffix)
            if candidate.exists():
                candidate.unlink()
        return

    if output_path.exists():
        output_path.unlink()