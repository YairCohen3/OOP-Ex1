"""End-to-end command-line and MP4 checks."""

import subprocess
import sys

import cv2

from IO_Utils import load_planes_from_csv


def test_cli_creates_mp4_with_one_frame_per_csv_plane(project_root, data_dir, csv_dir, tmp_path):
    csv_path = csv_dir / "synthetic_cube_planes.csv"
    output_path = tmp_path / "synthetic_cube_output.mp4"
    planes = load_planes_from_csv(str(csv_path))

    result = subprocess.run(
        [
            sys.executable,
            str(project_root / "Ex0.py"),
            str(data_dir / "synthetic_cube.nrrd"),
            str(csv_path),
            str(output_path),
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, (
        f"CLI failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert output_path.is_file()
    assert output_path.stat().st_size > 0

    capture = cv2.VideoCapture(str(output_path))
    try:
        assert capture.isOpened(), "OpenCV could not open the generated MP4"
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        assert frame_count == len(planes)
    finally:
        capture.release()
