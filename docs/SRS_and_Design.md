# Software Requirements Specification (SRS) & Algorithm Design

## 1. Software Requirements Specification (SRS)

### 1.1 Functional Requirements (FR)
* **FR1 - Load 3D Volumes (`Volume.py`):** Load 3D raster matrices from `.nrrd` files with dimensions $s_x \times s_y \times s_z$ ($1 \le s_x, s_y, s_z < 2^{10}$), supporting 8-bit, 16-bit, and 32-bit unsigned integer voxels.
* **FR2 - Parse Plane Definitions (`IO_Utils.py`):** Read `.csv` files where each row defines a slicing plane using either 3 points $(a, b, c)$ (9 floats) or 4 points $(a_1, a_2, b, c)$ (12 floats), with optional leading row indices.
* **FR3 - Validate Geometry (`Plane.py`):** Validate geometric constraints within a tolerance of $\varepsilon = 0.001$:
  * **Isosceles Triangle (3 points):** $|dist(a,b) - dist(a,c)| < \varepsilon$.
  * **Isosceles Trapezoid (4 points):** $|dist(a_1,b) - dist(a_2,c)| < \varepsilon$, $dist(a_1,a_2) \le dist(b,c)$, and all 4 points must be coplanar within $\varepsilon$.
* **FR4 - Compute 2D Projections (`Projector.py`):** Sample the 3D volume $M$ along each valid plane to produce a 2D cross-section matrix $E$. Coordinates falling outside the volume bounds $[0, s_x) \times [0, s_y) \times [0, s_z)$ are assigned `0`.
* **FR5 - Export MP4 Video (`IO_Utils.py`, `Ex0.py`):** Normalize projected frames to `0–255` (`uint8`), center them on a uniform canvas, and encode an `.mp4` video at 30 FPS at least. 

### 1.2 Non-Functional Requirements (NFR)
* **NFR1 - Throughput (Performance):** Achieve a minimum projection speed of 30 FPS on a $500^3$ volume, targeting **100+ FPS** using vectorized NumPy operations.
* **NFR2 - Fault Tolerance & Stability:** Safely handle edge cases including out-of-bounds coordinates, near-zero triangle tips ($d_{12} < \varepsilon$), and malformed CSV rows during video generation.
* **NFR3 - Modularity (OOP Design):** Separate data management (`Volume`), geometric validation (`Plane`), projection math (`Projector`), and I/O operations (`IO_Utils`) into clean, independent modules.

---

## 2. Algorithm Design & Optimizations

### 2.1 Unified Geometry & Edge-Case Handling
1. **Unified Triangle/Trapezoid Model:** `Plane.py` treats an isosceles triangle as a degenerate trapezoid where $a_1 = a_2 = a$. This allows `Projector.py` to run a single projection algorithm for both shapes.
2. **Integer Matrix Dimensions:** Output dimensions $d_{ab}$ (height) and $d_{bc}$ (width) are rounded to the nearest integer so they map cleanly to a 2D pixel grid.
3. **Division-by-Zero Protection:** Near the apex of a triangle, the row length $d_{12}$ approaches `0`. When $d_{12} < \varepsilon^3$, `Projector.py` substitutes a safe divisor (`1.0`) and samples the single midpoint pixel without crashing.
4. **Boundary Masking:** Sampled 3D points are rounded via `np.rint`. A boolean mask filters out any voxel outside $[0, s_x) \times [0, s_y) \times [0, s_z)$, leaving out-of-bounds pixels at their default `0` value.

### 2.2 Full NumPy Vectorization
* **2D Grid Broadcasting (`Projector.py`):** Instead of iterating row-by-row and pixel-by-pixel with Python `for` loops, `Projector.projection` builds a 2D grid of scanline steps (`y_indices` $\times$ `step_values`). All 3D voxel coordinates, boundary checks, and centering offsets for the entire plane are computed in C via NumPy broadcasting in a single pass.
* **Fast CSV & Video Processing (`IO_Utils.py`):**
  * Regex patterns are pre-compiled at the module level, and numbers are streamed directly into NumPy arrays using `np.fromiter`.
  * During MP4 creation, frame normalization (`0–255`), canvas centering, and 3-channel BGR conversion (`np.repeat`) are vectorized across the entire 3D frame stack before writing to `cv2.VideoWriter`.

### 2.3 Dual-Mode Error Handling (Strict vs. CLI Fault Tolerance)
* **Strict Mode (Unit Tests):** Calling `load_planes_from_csv(csv_path, ignore_errors=False)` raises a `ValueError` immediately if a row has invalid geometry, non-numeric text, wrong coordinate counts, or negative row indices.
* **Graceful CLI Mode (`Ex0.py`):** The CLI runs `load_planes_from_csv(csv_path, ignore_errors=True)`. If a row in the CSV is invalid, a warning is printed and `None` is stored in the plane list. `Projector.projection` converts `None` into a zero matrix, which renders as a **pure black frame** in the output `.mp4` video without interrupting execution.