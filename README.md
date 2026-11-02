# Ex1: 3D Volume Plane Projection

A Python tool that loads a 3D volumetric scan (`.nrrd`), computes 2D cross-sectional slices defined by geometric planes in a `.csv` file, and compiles the resulting projections into an `.mp4` video.

---

## Problem Overview
Given a 3D voxel matrix $M$ of dimensions $s_x \times s_y \times s_z$ ($1 \le s_x, s_y, s_z < 2^{10}$, using 8, 16, or 32-bit unsigned integers) and a list of 2D planes in 3D space, the program samples the volume along each plane and outputs a 2D projection matrix $E$.

Because continuous 3D plane coordinates do not align perfectly with discrete voxel indices, the algorithm uses vectorized NumPy grid sampling and nearest-neighbor rounding to achieve over **100+ FPS** on a $500^3$ volume (well above the 30 FPS requirement).

---

## Project Structure
```text
OOP-Ex1/
├── data/                       # Input 3D volume files (.nrrd)
├── docs/
│   ├── SRS_and_Design.md       # System requirements & vectorized algorithm design
│   └── Testing_and_Dataset.md  # Dataset details, CSV fixtures & test suite guide
├── results/                    # Generated output videos (.mp4)
├── tests/
│   ├── csv/                    # CSV test fixtures (valid, invalid, benchmark)
│   ├── conftest.py             # Pytest fixtures & Tkinter GUI test pop-ups
│   ├── test_geometry.py        # Triangle & trapezoid validation tests
│   ├── test_projection.py      # 2D sampling & boundary tests
│   ├── test_cli_video.py       # End-to-end CLI & corrupted CSV recovery tests
│   └── test_performance.py     # 500x500x500 volume FPS benchmark
├── Plane.py                    # Geometric validation & plane vectors
├── Volume.py                   # NRRD volume loader & dimensions handler
├── Projector.py                # Fully vectorized 3D-to-2D projection engine
├── IO_Utils.py                 # CSV parser & OpenCV MP4 video writer
└── Ex0.py                      # Main CLI entry point
```

---

## Installation & Setup

Install the required dependencies before running the project or tests:

```bash
python -m pip install numpy pynrrd opencv-python pytest
```

---

## How to Run (User Guide)

### 1. Generate an MP4 Video from a Volume and CSV
Run `Ex0.py` from the project root directory with three arguments: `<input.nrrd>`, `<planes.csv>`, and `<output.mp4>`:

```bash
python Ex0.py <data/File.nrrd> <tests/csv/File.csv> <results/File.mp4>
```

Example with the synthetic test cube:

```bash
python Ex0.py data/synthetic_cube.nrrd tests/csv/synthetic_cube_planes.csv results/cube_output.mp4
```

### 2. Run the Automated Test Suite
Run all tests from the project root:

```bash
python -m pytest -v
```

Run a specific test file (for example, the performance benchmark or CLI video tests):

```bash
python -m pytest tests/test_performance.py -v
python -m pytest tests/test_cli_video.py -v
```

> **Interactive Test Pop-ups:** When running `pytest`, `conftest.py` displays a clean Tkinter window. If a test fails, an **ERROR** pop-up highlights the exact failing code line; if all tests pass, a green **ALL TESTS PASSED** window appears. Press `Enter` or `Esc` to close the window immediately.

---

## Supported CSV Input Format & Fault Tolerance
Each row in the input `.csv` file represents one projection plane (one frame in the output video):
* **3 Points (Isosceles Triangle - 9 floats):** `ax, ay, az, bx, by, bz, cx, cy, cz` (or 10 numbers if a leading row index is included).
* **4 Points (Isosceles Trapezoid - 12 floats):** `a1x, a1y, a1z, a2x, a2y, a2z, bx, by, bz, cx, cy, cz` (or 13 numbers with a leading row index).
* **Formatting:** Header rows, `#` comments, and parentheses/brackets around coordinates are supported automatically.
* **Corrupted Row Recovery (Black Frame Fallback):** When running `Ex0.py`, if a row in the CSV is corrupted (invalid geometry, missing numbers, or a negative row index), the program does not crash. Instead, it prints a warning to the console and inserts a **black frame** at that position so the video continues smoothly.

---

## Documentation Links
* [Software Requirements & Algorithm Design](docs/SRS_and_Design.md)
* [Testing Strategy & Datasets](docs/Testing_and_Dataset.md)