# Software Requirements Specification (SRS) & Detailed Algorithm Design

## 1. Software Requirements Specification (SRS)

### 1.1 Functional Requirements (FR)
- **FR1 - Volumetric Data Loading:** The system shall read 3D raster matrices from `.nrrd` files of dimensions **sx × sy × sz** (**1 ≤ sx, sy, sz < 2¹⁰**) containing 8-bit, 16-bit, or 32-bit unsigned integers.
- **FR2 - Plane Trajectory Parsing:** The system shall parse a `.csv` file where each row defines a sampling plane using either 3 3D points **(a, b, c)** (9 floats)
- **FR3 - Geometric Validation:**
  * For 3 points **(a, b, c)**: Validate that **|dist(a,b) - dist(a,c)| < ε** (**ε = 0.001**).
  * For 4 points (a₁, a₂, b, c): Validate that |dist(a₁,b) - dist(a₂,c)| < ε, dist(a₁,a₂) ≤ dist(b,c), and that all 4 points are coplanar within tolerance ε.
- **FR4 - 2D Plane Projection:** For each valid plane, the system shall compute a 2D matrix **E** representing the cross-section of the 3D volume **M**, assigning `0` to any sample point falling outside the bounds of **M**.
- **FR5 - Video Export:** The system shall compile the ordered sequence of projected 2D matrices into an `.mp4` video file via a CLI command: `python Ex0.py <file.nrrd> <file.csv> <file.mp4>`.

### 1.2 Non-Functional Requirements (NFR)
- **NFR1 - Performance (Throughput):** On a **500³** byte volume, the projection calculation shall achieve a minimum runtime performance of 30 FPS, targeting 100+ FPS using vectorized NumPy operations.
- **NFR2 - Robustness & Stability:** The system shall gracefully handle edge cases including out-of-bounds coordinates, zero-length vectors (**d₁₂ = 0**), and floating-point rounding without crashing.
- **NFR3 - Maintainability & OOD:** The codebase shall follow Object-Oriented Design principles, separating data loading, geometry validation, projection computation, and video rendering into modular components.

---

## 2. Detailed Algorithm Specification

### 2.1 Resolving Ambiguities in the Base Pseudocode

> **Overview**
> The following constraints and optimizations resolve edge cases found in the initial mathematical model, ensuring robust boundary handling and real-time execution.

**Unified Shape Representation**  
The system utilizes a single algorithm to process both triangles and trapezoids. An isosceles triangle is seamlessly treated as a degenerate isosceles trapezoid where the two top vertices converge to the exact same point.

**Matrix Dimension Discretization**  
To ensure valid integer pixel coordinates for the 2D output matrix, floating-point `3D` Euclidean distances are rounded to the nearest integer. This guarantees accurate, discrete `Height` and `Width` boundaries.

**Zero-Distance Guard**  
At the triangle's apex, the distance between the scanning points evaluates to `0`. To proactively prevent division-by-zero exceptions, the horizontal scan is skipped, and a single point is sampled precisely at the center of the row.

**Voxel Sampling & Boundary Handling**  
Continuous 3D coordinates are mapped to discrete matrix indices utilizing nearest-neighbor rounding. If a mapped coordinate falls outside the boundaries of the `3D` volume, it safely defaults to a background value of `0`.

**Vectorized Execution**  
To achieve sustained real-time performance (**100+ FPS**), standard nested iterative loops are replaced with vectorized array operations (e.g., `NumPy` broadcasting). This architectural shift allows the entire 2D sampling grid to be computed and queried simultaneously in bulk.
