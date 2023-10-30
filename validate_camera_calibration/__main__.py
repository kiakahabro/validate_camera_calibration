import cProfile
import glob
import os
import sys
import textwrap
from pathlib import Path
from typing import List, Optional

import emoji
import numpy as np
import typer

from validate_camera_calibration.tools import general as gn
from validate_camera_calibration.tools import image, validation
from validate_camera_calibration.tools import yaml_utils as yu

app = typer.Typer(add_completion=False, rich_markup_mode="rich")

filename = os.path.basename(__file__)


def expected_calibration_directory_contents() -> str:
    supported_list = gn.join_string_with_commas(
        image.supported_image_extensions(), "or"
    )
    structure = ""
    structure += "camera_params.yaml            # Camera parameters"
    structure += "\ncalibration_grid_params.yaml  # Calibration grid parameters"
    structure += f"\n<first_image_filename>.(ext)  # Any file name with either {supported_list} extension"
    structure += f"\n<second_image_filename>.(ext) # Any file name with either {supported_list} extension"
    structure += "\n ..."
    structure += f"\n<last_image_filename>.(ext)   # Any file name with either {supported_list} extension"
    return structure


def expected_poses_directory_contents() -> str:
    structure = ""
    structure += "<first_image_filename>.yaml  # Same name as source file\n"
    structure += "<second_image_filename>.yaml # Same name as source file\n"
    structure += " ...\n"
    structure += "<last_image_filename>.yaml   # Same name as source file\n"
    return structure


def expected_undistorted_directory_contents() -> str:
    structure = ""
    structure += (
        f"<first_image_filename>.(ext)  # Same name and extension as source file\n"
    )
    structure += (
        f"<second_image_filename>.(ext) # Same name and extension as source file\n"
    )
    structure += " ...\n"
    structure += (
        f"<last_image_filename>.(ext)   # Same name and extension as source file\n"
    )
    return structure


def check_calibration_directory_exists(root_path: Path) -> Path:
    dir_calibration = Path(os.path.join(root_path, "calibration"))
    if not dir_calibration.is_dir():
        folder_icon = emoji.emojize(":open_file_folder:")
        structure = (
            f"Expected calibration{folder_icon} to be a directory in {root_path}! "
        )
        structure += "This folder should contain: \n"
        structure += expected_calibration_directory_contents()

        raise typer.BadParameter(structure)
    return dir_calibration


# Callbacks
# --------------------------------------------------
def root_path_callback(root_path: Path):
    if not root_path.is_dir():
        raise typer.BadParameter(f"Expected {root_path} to be a directory.")
    return root_path


def camera_params_callback(camera_params_file: Path):
    if camera_params_file is None:
        return None
    camera_params_file = Path(camera_params_file)
    if not camera_params_file.is_file():
        raise typer.BadParameter(f"Expected {camera_params_file} to be a file.")
    return camera_params_file


# --------------------------------------------------

docstring = f"""
A minimalistic camera calibration validation toolbox that makes use of the camera intrinsics provided by a yaml file, the calibration grid parameters, and a set of images containing the calibration grid.\n
\b
[bold green]Expected directory structure: [/bold green]
<root_path>/calibration
{textwrap.indent(expected_calibration_directory_contents(), "    ")}

# Only generated if --export_poses is specified
<root_path>/poses # Directory containing exported poses
{textwrap.indent(expected_poses_directory_contents(), "    ")}

# Only generated if --export_undistorted is specified
<root_path>/undistorted # Directory containing exported undistorted images
{textwrap.indent(expected_undistorted_directory_contents(), "    ")}

\b
[bold green]Examples: [/bold green]
# Validates camera calibration on image files located in <root_path>/calibration
$ validate_camera_calibration <root_path>:open_file_folder:

"""
# Split the string into lines
lines = docstring.strip().split("\n")

# Find the maximum index of the '#' character in each line
matching_str = " # "
max_index = max(line.index(matching_str) for line in lines if matching_str in line)

# Add padding to the left of the '#' characters
padded_lines = [
    line[: line.index(matching_str)].ljust(max_index) + line[line.index(matching_str) :]
    if matching_str in line
    else line
    for line in lines
]
docstring = "\n".join(padded_lines)


@app.command(help=docstring)
def run_validation(
    root_path: Path = typer.Argument(
        ...,
        help="The data directory used for running calibration.",
        show_default=False,
        callback=root_path_callback,
    ),
    export_poses: bool = typer.Option(
        False,
        "--export_poses",
        help="Export poses to <root_path>/poses.",
        show_default=False,
    ),
    export_undistorted: bool = typer.Option(
        False,
        "--export_undistorted",
        help="Export undistorted to <root_path>/undistorted.",
        show_default=False,
    ),
    camera_params_file: Optional[Path] = typer.Option(
        None,
        "--camera_params_file",
        help="Path to camera parameters yaml file.",
        show_default=False,
        callback=camera_params_callback,
    ),
):
    typer.echo(f"root_path is {root_path}")

    dir_calibration = check_calibration_directory_exists(root_path)

    validation.validate(
        root_path,
        dir_calibration,
        export_poses=export_poses,
        export_undistorted_images=export_undistorted,
        file_camera_params=camera_params_file,
    )


pr = cProfile.Profile()
pr.enable()
try:
    app()
except KeyboardInterrupt:
    pass
finally:
    pr.disable()
    pr.dump_stats("validate_camera_calibration.pstat")
