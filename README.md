# validate-camera-calibration

[TOC]

## Summary

A Python camera calibration validation project.

## Installation

```bash
pip install validate_camera_calibration
```

## Usage

The `validate_camera_calibration` package expects a path to be passed that contains the directory with the calibration data. For a calibration dataset, the following directory structure is expected:

```bash
 <root_path>/calibration
    camera_params.yaml            # Camera parameters
    calibration_grid_params.yaml  # Calibration grid parameters
    <first_image_filename>.(ext)  # Any file name with either .jpg, .jpeg, .png, .bmp or .tiff extension
    <second_image_filename>.(ext) # Any file name with either .jpg, .jpeg, .png, .bmp or .tiff extension
     ...
    <last_image_filename>.(ext)   # Any file name with either .jpg, .jpeg, .png, .bmp or .tiff extension

 # Only generated if --export_poses is specified
 <root_path>/poses                 # Directory containing exported poses
    <first_image_filename>.yaml   # Same name as source file
    <second_image_filename>.yaml  # Same name as source file
     ...
    <last_image_filename>.yaml    # Same name as source file


 # Only generated if --export_rectified is specified
 <root_path>/rectified             # Directory containing exported rectified images
    <first_image_filename>.(ext)  # Same name and extension as source file
    <second_image_filename>.(ext) # Same name and extension as source file
     ...
    <last_image_filename>.(ext)   # Same name and extension as source file

```

## Command line Options

| Argument             | Notes                                                                |
| -------------------- | -------------------------------------------------------------------- |
| `--images_dir`       | Flag for generating the time associations                            |
| `--export_rectified` | Flag for exporting rectified images                                  |
| `--export_poses`     | Flag for exporting the camera poses relative to the calibration grid |
