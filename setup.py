# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

from setuptools import find_packages, setup

DESCRIPTION = "validate camera calibration"
LONG_DESCRIPTION = "A Python camera calibration validation project."
version = "{{VERSION_PLACEHOLDER}}"
if version.startswith("{{"):
    version = "0.0.0"

# Setting up
setup(
    # the name must match the folder name 'validate_camera_calibration'
    name="validate_camera_calibration",
    version=version,
    author="Timothy Farnworth",
    author_email="tkfarnworth@gmail.com",
    description=DESCRIPTION,
    url="https://github.com/kiakahabro/validate_camera_calibration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "validate_camera_calibration = validate_camera_calibration.__main__:main"
        ]
    },
    # https://peps.python.org/pep-0440/#version-specifiers
    python_requires=">=3.8, <=3.10",
    install_requires=[
        "emoji",
        "numba",
        "numpy",
        "opencv-python",
        "pathlib2",
        "pytest-cov",
        "pytest",
        "pyyaml",
        "typer[all]",
    ],
    keywords=["python", "calibration", "validation", "camera"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],
)
