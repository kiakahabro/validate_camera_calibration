from pathlib import Path

import cv2
import numpy as np
from typing_extensions import Any, List, Self, Tuple


def supported_image_extensions() -> List[str]:
    return [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]


class Image:
    def __init__(self, img: np.ndarray, file_path: Path = None) -> None:
        assert isinstance(
            img, np.ndarray
        ), f"Expected img to be a numpy array, but it is of type {type(img).__name__}!"
        self.img = img
        self._has_calibration_artifact_in_frame = False
        self.file_path = file_path
        self.chess_board_corners = None

    def __repr__(self) -> str:
        return f"Image({self.img.shape})"

    def detect_chessboard(self, pattern_size: Tuple[int]) -> None:
        assert isinstance(
            pattern_size, tuple
        ), f"Expected pattern_size to be a list, but it is of type {type(pattern_size).__name__}!"
        assert len(pattern_size) == 2, "Expected pattern_size to be of length 2!"
        corners = None
        flags = (
            cv2.CALIB_CB_FAST_CHECK
            + cv2.CALIB_CB_ADAPTIVE_THRESH
            + cv2.CALIB_CB_NORMALIZE_IMAGE
        )
        img_grey = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        retval, corners = cv2.findChessboardCorners(
            self.img, pattern_size, corners, flags=flags
        )
        if retval:
            self._has_calibration_artifact_in_frame = True
            corners = cv2.cornerSubPix(
                img_grey,
                corners,
                (11, 11),
                (-1, -1),
                (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001),
            )
        self.chess_board_corners = corners

    def has_chessboard(self) -> bool:
        return self._has_calibration_artifact_in_frame

    def to_file(self, file_path: Path) -> None:
        assert cv2.imwrite(
            file_path, self.img
        ), f"Failed to save {file_path}! Details:\n{self.__repr__()}"

    @staticmethod
    def from_file(file_path: Path) -> Self:
        file_path = Path(file_path)
        assert file_path.exists(), f"Expected {file_path} to exist."
        assert file_path.suffix.lower() in supported_image_extensions(), (
            f"Expected {file_path} to have a supported image extension. "
            f"Supported extensions are {supported_image_extensions()}"
        )
        img = cv2.imread(str(file_path))
        return Image(img, file_path)
