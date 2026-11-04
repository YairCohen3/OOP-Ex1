import subprocess
import sys
import pytest
from IO_Utils import save_frames_to_mp4
import cv2
import numpy as np
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


def test_cli_replaces_invalid_csv_rows_with_black_frames(project_root, data_dir, tmp_path):
    csv_path = tmp_path / "corrupted_planes.csv"
    csv_path.write_text(
        "0, 20, 20, 10, 40, 20, 10, 30, 40, 10\n"
        "-1, 20, 20, 10, 40, 20, 10, 30, 40, 10\n"  # אינדקס שלילי לא תקין -> פריים שחור
        "2, 0, 0, 0, 10, 0, 0, 0, 99, 0\n"          # שוקיים לא שוות -> פריים שחור
        "3, 10, 20, 30\n"                           # חסרים ערכים בשורה -> פריים שחור
        "4, 20, 20, 15, 40, 20, 15, 30, 40, 15\n",  # מישור תקין
        encoding="utf-8",
    )
    output_path = tmp_path / "corrupted_output.mp4"

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
        f"CLI failed on invalid rows.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert output_path.is_file()

    capture = cv2.VideoCapture(str(output_path))
    try:
        assert capture.isOpened()
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        assert frame_count == 5


        capture.read()
        ok, black_frame = capture.read()
        assert ok
        assert np.all(black_frame == 0)
    finally:
        capture.release()

def test_save_frames_mixed_sizes_and_empty_error(tmp_path):
    with pytest.raises(ValueError, match="empty"):
        save_frames_to_mp4([], str(tmp_path / "empty.mp4"))

    frames = [
        np.full((12, 16), 100.0, dtype=np.float64),
        np.full((24, 32), 200.0, dtype=np.float64),
    ]
    out_mp4 = tmp_path / "mixed_sizes.mp4"
    save_frames_to_mp4(frames, str(out_mp4))
    assert out_mp4.is_file() and out_mp4.stat().st_size > 0


def test_cli_exits_with_error_on_wrong_argument_count(project_root):
    result = subprocess.run(
        [sys.executable, str(project_root / "Ex0.py")],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1