# Software Requirements Specification (SRS) & Detailed Algorithm Design

## 1. Software Requirements Specification (SRS)

### 1.1 Functional Requirements (FR)
- **FR1 - Volumetric Data Loading:** The system shall read 3D raster matrices from `.nrrd` files of dimensions **sx × sy × sz** (**1 ≤ sx, sy, sz < 2¹⁰**) containing 8-bit, 16-bit, or 32-bit unsigned integers.
- **FR2 - Plane Trajectory Parsing:** The system shall parse a `.csv` file where each row defines a sampling plane using either 3 3D points **(a, b, c)** (9 floats) or 4 3D points **(a₁, a₂, b, c)** (12 floats).
- **FR3 - Geometric Validation:**
  * For 3 points **(a, b, c)**: Validate that **|dist(a,b) - dist(a,c)| < ε** (**ε = 0.001**).
  * For 4 points **(a₁, a₂, b, c)**: Validate that **|dist(a₁,b) - dist(a₂,c)| < ε**, **dist(a₁,a₂) ≤ dist(b,c)**, and that all 4 points are coplanar within tolerance **ε**.
- **FR4 - 2D Plane Projection:** For each valid plane, the system shall compute a 2D matrix **E** representing the cross-section of the 3D volume **M**, assigning `0` to any sample point falling outside the bounds of **M**.
- **FR5 - Video Export:** The system shall compile the ordered sequence of projected 2D matrices into an `.mp4` video file via a CLI command: `python Ex0.py <file.nrrd> <file.csv> <file.mp4>`.

### 1.2 Non-Functional Requirements (NFR)
- **NFR1 - Performance (Throughput):** On a **500³** byte volume, the projection calculation shall achieve a minimum runtime performance of 30 FPS, targeting 100+ FPS using vectorized NumPy operations.
- **NFR2 - Robustness & Stability:** The system shall gracefully handle edge cases including out-of-bounds coordinates, zero-length vectors (**d₁₂ = 0**), and floating-point rounding without crashing.
- **NFR3 - Maintainability & OOD:** The codebase shall follow Object-Oriented Design principles, separating data loading, geometry validation, projection computation, and video rendering into modular components.

---

## 2. Detailed Algorithm Specification

### 2.1 Resolving Ambiguities in the Base Pseudocode
1. **Unifying Triangle and Trapezoid Representations:**
   An isosceles triangle **(a, b, c)** is treated as a degenerate isosceles trapezoid **(a₁, a₂, b, c)** where **a₁ = a** and **a₂ = a**. Thus, a single unified algorithm processes both cases.
2. **Discretization & Matrix Dimensions:**
   Since Euclidean distances **D_ab = dist(a₁, b)** and **D_bc = dist(b, c)** are floating-point numbers, the output matrix **E** dimensions are discretized as:
   * **H = max(1, int(round(D_ab)))**
   * **W = max(1, int(round(D_bc)))**
3. **Zero-Distance Guard:**
   When computing **d₁₂ = dist(a₁, a₂)** at step **y**, if **d₁₂ < ε**, we set **dp = (0, 0, 0)** and sample only a single point at the center **x = ⌊W / 2⌋** to prevent division by zero.
4. **Voxel Sampling & Boundary Handling:**
   For any continuous 3D point **p = (p_x, p_y, p_z)**, discrete voxel indices are obtained via nearest-neighbor rounding: **(i, j, k) = (round(p_x), round(p_y), round(p_z))**. If **0 ≤ i < sx**, **0 ≤ j < sy**, and **0 ≤ k < sz**, then **v = M[i, j, k]**; otherwise **v = 0**.
5. **Vectorized Execution for 100+ FPS:**
   Instead of nested Python loops over **y** and **x₁**, the 2D grid of sample coordinates **(x, y)** is generated using vectorized NumPy array broadcasting, and voxel lookup is performed in bulk.
