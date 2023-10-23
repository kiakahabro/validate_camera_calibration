from pathlib import Path

import cv2
import numpy as np
import yaml
from typing_extensions import Any, List, Self

import validate_camera_calibration.tools.general as gn
import validate_camera_calibration.tools.yaml_utils as yu
from validate_camera_calibration.tools.image import Image


class Camera:
    def __init__(
        self,
        Kc: np.ndarray,
        dist: np.ndarray,
        image_width: int,
        image_height: int,
        from_file: Path = None,
    ) -> None:
        assert len(Kc.shape) == 2, "Expected Kc to be 2d!"
        assert Kc.shape[0] == Kc.shape[1], "Expected Kc to be square!"
        assert Kc.shape[0] == 3, "Expected Kc to be a 3x3 Matrix!"
        assert np.allclose(Kc, np.triu(Kc)), "Expected Kc to be upper triangular!"

        self.Kc = Kc
        self.dist = dist
        self.image_width = image_width
        self.image_height = image_height
        self.from_file = from_file

    @staticmethod
    def from_file(file_path: Path) -> Self:
        file_path = Path(file_path)
        assert file_path.exists(), f"Expected {file_path} to exist."
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        Kc = yu.yaml_dict_to_numpy(data["camera_matrix"])
        dist = yu.yaml_dict_to_numpy(data["distortion_coefficients"])
        image_width = data["image_width"]
        image_height = data["image_height"]
        return Camera(Kc, dist, image_width, image_height, file_path)

    def to_file(self, file_path: Path) -> None:
        file_path = gn.add_extension(file_path, "yaml")
        data = dict()
        data["camera_matrix"] = yu.numpy_to_yaml_dict(self.Kc)
        data["distortion_coefficients"] = yu.numpy_to_yaml_dict(self.dist)
        with open(file_path, "w") as f:
            yaml.dump(data, f)

    def __repr__(self) -> str:
        return f"Camera(Kc={self.Kc.shape}, dist={self.dist.shape})"

    def undistort(self, img: np.ndarray) -> np.ndarray:
        assert isinstance(img, np.ndarray), "Expected img to be a numpy array!"
        assert (
            len(img.shape) == 2 or len(img.shape) == 3
        ), "Expected img to be 2d if grayscale or 3d if colour!"
        assert img.shape[0] == self.image_height, "Expected img to have correct height!"
        assert img.shape[1] == self.image_width, "Expected img to have correct width!"
        return cv2.undistort(img, self.Kc, self.dist)

    def undistort_image(self, img: Image) -> Image:
        assert isinstance(img, Image), "Expected img to be an Image object!"
        return Image(self.undistort(img.img), img.from_file)
