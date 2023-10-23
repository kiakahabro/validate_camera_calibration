import os
import shutil
from pathlib import Path

import cv2
import numpy as np
import yaml
from rich.progress import track

import validate_camera_calibration.tools.general as gn
import validate_camera_calibration.tools.yaml_utils as yu
from validate_camera_calibration.tools.camera import Camera
from validate_camera_calibration.tools.image import Image, supported_image_extensions


def get_calibration_grid_parameters(file_path: Path) -> dict:
    file_path = Path(file_path)
    assert file_path.exists(), f"Expected {file_path} to exist."
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    return data


def validate(
    dir_base: Path,
    dir_calibration: Path,
    export_undistorted_images: bool = False,
    export_poses: bool = False,
) -> None:
    assert dir_base.is_dir(), f"Expected {dir_base} to be a directory!"
    assert dir_calibration.is_dir(), f"Expected {dir_calibration} to be a directory!"

    # Check that the calibration directory contains a camera_params.yaml file
    file_camera_params = Path(os.path.join(dir_calibration, "camera_params.yaml"))
    assert (
        file_camera_params.is_file()
    ), f"Expected camera_params.yaml to be a file in {dir_calibration}!"

    # Check that the calibration directory contains a calibration_grid_params.yaml file
    file_calibration_grid_params = Path(
        os.path.join(dir_calibration, "calibration_grid_params.yaml")
    )
    assert (
        file_calibration_grid_params.is_file()
    ), f"Expected calibration_grid_params.yaml to be a file in {dir_calibration}!"

    # Find images in the calibration directory
    supported_extensions = supported_image_extensions()
    image_files = [
        f
        for f in os.listdir(dir_calibration)
        if Path(f).suffix.lower() in supported_extensions
        and not Path(f).stem.startswith(".")
    ]

    image_files.sort()

    print(f"Found {len(image_files)} images in {dir_calibration}.")
    assert (
        len(image_files) > 0
    ), f"Expected to find at least one image in {dir_calibration}!"

    # Load camera parameters
    camera = Camera.from_file(file_camera_params)

    # Load calibration grid
    calibration_grid = get_calibration_grid_parameters(file_calibration_grid_params)
    pattern_size = (calibration_grid["grid_width"], calibration_grid["grid_height"])

    # Load images
    images = []
    for image_file in track(image_files, "Loading images"):
        image = Image.from_file(os.path.join(dir_calibration, image_file))

        # Detect checkerboard
        image.detect_chessboard(pattern_size)

        if image.has_chessboard():
            images.append(image)

    print(
        f"Found {len(images)} out of {len(image_files)} images with a calibration grid."
    )

    # Object points
    rPNn = np.meshgrid(np.arange(0, pattern_size[0]), np.arange(0, pattern_size[1]))
    rPNn = (
        np.hstack(
            (
                rPNn[0].reshape(-1, 1),
                rPNn[1].reshape(-1, 1),
                np.zeros((pattern_size[0] * pattern_size[1], 1)),
            )
        ).astype(float)
        * calibration_grid["grid_square_size"]
    )

    poses = []
    for image in track(
        images, "Solving camera pose from calibration grid using solvePnP"
    ):
        # Image points
        rQOi = image.chess_board_corners.reshape(-1, 2)

        # Solve PnP
        retval, rvec, tvec = cv2.solvePnP(rPNn, rQOi, camera.Kc, camera.dist)

        # Compute reprojection error
        rQOi_reprojected, _ = cv2.projectPoints(
            rPNn, rvec, tvec, camera.Kc, camera.dist
        )
        rQOi_reprojected = rQOi_reprojected.reshape(-1, 2)
        reprojection_error = np.linalg.norm(rQOi_reprojected - rQOi, axis=1)

        rNCc = tvec
        Rcn, _ = cv2.Rodrigues(rvec)

        Rnc = Rcn.T
        rCNn = -Rnc @ rNCc

        # Add pose to image
        pose = dict()
        pose["rCNn"] = rCNn
        pose["Rnc"] = Rnc
        pose["reprojection_error"] = reprojection_error
        pose["source_name"] = image.file_path
        poses.append(pose)

    reprojection_errors = np.hstack([pose["reprojection_error"] for pose in poses])
    reproj_rms = np.sqrt(np.mean(reprojection_errors**2))
    reproj_mean = np.mean(reprojection_errors)
    reproj_std = np.std(reprojection_errors)
    print(
        f"Reprojection error from {len(poses)} image frames, each with {pattern_size[0] * pattern_size[1]} points:"
    )
    print(f"  RMS: {reproj_rms:4g} [pix]")
    print(f" Mean: {reproj_mean:4g} [pix]")
    print(f"  STD: {reproj_std:4g} [pix]")

    if export_undistorted_images:
        dir_undistorted = Path(os.path.join(dir_base, "undistorted"))
        if dir_undistorted.exists():
            shutil.rmtree(dir_undistorted)
        os.mkdir(dir_undistorted)
        for image_file in track(image_files, "Saving undistorted images"):
            image = Image.from_file(os.path.join(dir_calibration, image_file))
            image_undistorted = camera.undistort_image(image)
            image_undistorted.to_file(
                os.path.join(
                    dir_undistorted,
                    image_file,
                )
            )
    if export_poses:
        dir_poses = Path(os.path.join(dir_base, "poses"))
        if dir_poses.exists():
            shutil.rmtree(dir_poses)
        dir_poses.mkdir(parents=True, exist_ok=True)
        for i, pose in enumerate(track(poses, "Saving poses")):
            image_name = Path(pose["source_name"]).stem
            file_pose = Path(os.path.join(dir_poses, f"pose_{image_name}.yaml"))
            pose_out = dict()
            #
            pose_out["rCNn"] = yu.numpy_to_yaml_dict(pose["rCNn"])
            #
            pose_out["Rnc"] = yu.numpy_to_yaml_dict(pose["Rnc"])
            #
            rms = np.sqrt(np.mean(pose["reprojection_error"] ** 2))
            pose_out["reprojection_error"] = rms.item()
            with open(file_pose, "w") as f:
                yaml.dump(pose_out, f)
