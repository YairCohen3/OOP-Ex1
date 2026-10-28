# Ex1: 3D Volume Plane Projection

## Problem Definition
Given a 3D raster data matrix (M) of dimensions sx * sy * sz (where 1<=sx,sy,sz<2¹⁰ and 0<=x<sx, 0<=y<sy, 0<=z<sz, and each voxel is an 8, 16, or 32-bit unsigned integer) and a 2D geometric plane (P) defined in 3D space, the goal is to compute the 2D cross-sectional projection image (E) of the plane (P) intersecting the volume (M).

Mapping a flat mathematical plane onto a 3D grid of voxels is tricky because the sampling points don't perfectly match up. This project uses an algorithm to sample the volume and create a 2D image for each input plane.

## Project Scope
1. **Input Handling:**
   - Reading 3D volumetric raster data in `.nrrd` format.
   - Reading a sequence of plane coordinates from a `.csv` file, where each row defines a plane using 3 points (isosceles triangle) or 4 points (isosceles trapezoid).
2. **Core Projection Algorithm:**
   - Validating the geometric constraints of the input points (within tolerance of **ε = 0.001**).
   - Projecting the 3D volume onto each 2D plane, with a minimum throughput requirement of 30 planes per second and a target of 100+ planes per second on a **500³** volume.
   - Handling out-of-bounds coordinates safely by assigning a default value of `0`.
3. **Output Generation:**
   - Compiling the sequence of projected 2D matrices into an `.mp4` video file.
4. **Documentation & Testing:**
   - Software requirements, algorithm design, testing strategy, and performance experiments.

## Supported CSV Input Formats
Each row in `<file.csv>` represents a single projection plane (producing one video frame in order):
* **3 Points (Isosceles Triangle - 9 coordinates per row):** `ax, ay, az, bx, by, bz, cx, cy, cz`
* **4 Points (Isosceles Trapezoid - 12 coordinates per row):** `a1x, a1y, a1z, a2x, a2y, a2z, bx, by, bz, cx, cy, cz`
* **Flexible Parsing:** The parser supports optional header rows, `#` comments, and parentheses or brackets around coordinates.

## How to Run
Install the required libraries:

```bash
python -m pip install numpy pynrrd opencv-python
```

Run the program from the project root:

```bash
python Ex0.py <file.nrrd> <file.csv> <file.mp4>
```

Replace the placeholders with the paths to your input volume, CSV file, and desired output video.

## More Information
- [Software Requirements and Algorithm Design](docs/SRS_and_Design.md)
- [Datasets and Testing Strategy](docs/Testing_and_Dataset.md)
