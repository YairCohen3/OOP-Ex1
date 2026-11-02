# Dataset Definition & Testing Strategy

## 1. NRRD Datasets (`data/`)
Our test suite uses three `.nrrd` volumes to verify visual quality, mathematical accuracy, and runtime performance:

1. **`MRHead.nrrd` (Real Medical Scan):**
   * **Source:** 3D Slicer sample MRI dataset.
   * **Purpose:** End-to-end visual verification of axial, coronal, sagittal, and oblique slices on real anatomy.
2. **`synthetic_cube.nrrd` (Deterministic Unit-Test Volume):**
   * **Dimensions:** $100 \times 100 \times 100$ (`uint8`).
   * **Purpose:** Contains predictable voxel patterns so unit tests can verify exact pixel values in the projected 2D matrix $E$.
3. **`benchmark_500.nrrd` (Performance Stress-Test Volume):**
   * **Dimensions:** $500 \times 500 \times 500$ (`uint8`).
   * **Purpose:** Benchmarks projection speed against the 30 FPS minimum requirement (and 100+ FPS target).

---

## 2. CSV Test Fixtures (`tests/csv/`)
All CSV inputs used by the automated tests are located in `tests/csv/`:
* **`valid_*.csv` & `invalid_*.csv`:** Used by `test_geometry.py` to test valid triangles/trapezoids and reject unequal legs, non-coplanar points, or malformed rows.
* **`projection_*.csv` & `triangle_near_tip.csv`:** Used by `test_projection.py` to test in-bounds sampling, out-of-bounds zero-padding, and near-zero apex stability ($d_{12} \to 0$).
* **`synthetic_cube_planes.csv`:** Used by `test_cli_video.py` to test full CLI execution and MP4 frame count accuracy.
* **`benchmark_500_planes.csv`:** Contains 500 planes used by `test_performance.py` to measure throughput (FPS).
* **`MRHead_planes.csv`:** Example trajectory for generating a full video from `data/MRHead.nrrd`.

---

## 3. Automated Testing Strategy (`tests/`)

We use `pytest` across four test modules:

### 3.1 Geometry & Input Validation (`test_geometry.py`)
* Verifies that valid 3-point isosceles triangles and 4-point coplanar trapezoids pass within $\varepsilon = 0.001$.
* Confirms that unequal legs, non-coplanar vertices, wrong coordinate counts, and non-finite values (`NaN`/`Inf`) raise a `ValueError`.

### 3.2 Projection & Boundary Logic (`test_projection.py`)
* **In-Bounds Accuracy:** Projects axis-aligned slices through `synthetic_cube.nrrd` and checks that output pixels match the source 3D volume.
* **Out-of-Bounds Safety:** Projects planes extending outside $[0, s_x) \times [0, s_y) \times [0, s_z)$ and verifies that external pixels default to `0`.
* **Apex Stability:** Tests triangles near their top tip to confirm no division-by-zero occurs.

### 3.3 End-to-End CLI & Corrupted CSV Recovery (`test_cli_video.py`)
* **`test_cli_creates_mp4_with_one_frame_per_csv_plane`:** Runs `Ex0.py` via `subprocess`, verifies that the `.mp4` file is created, and checks with `cv2.VideoCapture` that the video frame count equals the number of CSV planes.
* **`test_cli_replaces_invalid_csv_rows_with_black_frames`:** Feeds a CSV containing negative indices, unequal triangle legs, and missing values into `Ex0.py`. Verifies that the CLI finishes with exit code `0`, preserves the total frame count, and outputs a pure black frame (`0`) for each invalid row.

### 3.4 Performance Benchmark (`test_performance.py`)
* Projects 500 planes on `benchmark_500.nrrd` ($500^3$) and measures pure projection FPS.
* Asserts that throughput exceeds the mandatory **30 FPS** threshold (achieving ~400 FPS in unit benchmarks and ~75–80+ FPS on full video slices).

### 3.5 Interactive GUI Test Feedback (`conftest.py`)
* Hooks into `pytest` (`pytest_exception_interact` and `pytest_sessionfinish`) to launch a Tkinter pop-up window:
  * **On Failure:** Displays an **ERROR** dialog highlighting the exact failing source line, stopping execution cleanly when closed (`os._exit(0)`).
  * **On Success:** Displays a green **ALL TESTS PASSED** summary dialog.

---

## 4. Running the Tests
From the project root directory, run:

```bash
python -m pytest -v
```