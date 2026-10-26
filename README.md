# Ex1: 3D Volume Plane Projection

## Problem Definition
Given a 3D raster data matrix (M) of dimensions sx * sy * sz (where 1<=sx,sy,sz<2¹⁰ and 0<=x<sx, 0<=y<sy, 0<=z<sz, and each voxel is an 8, 16, or 32-bit unsigned integer) and a 2D geometric plane (P) defined in 3D space, the goal is to compute the 2D cross-sectional projection image (E) of the plane (P) intersecting the volume (M).

Mapping a flat mathematical plane onto a 3D grid of voxels is tricky because the sampling points don't perfectly match up. This project solves this by using a fast, reliable, and well-designed algorithm to extract the 3D data and create clean 2D images
## Project Scope
1. **Input Handling:**
   - Reading 3D volumetric raster data in `.nrrd` format.
   - Reading a sequence of plane coordinates from a `.csv` file, where each row defines a plane using 3 points (isosceles triangle) or 4 points (isosceles trapezoid).
2. **Core Projection Algorithm:**
   - Validating the geometric constraints of the input points (within tolerance of **ε = 0.001**).
   - Projecting the 3D volume onto each 2D plane at high speed (targeting 30 FPS, aiming for 100+ FPS on a **500³** volume).
   - Handling out-of-bounds coordinates safely by assigning a default value of `0`.
3. **Output Generation:**
   - Compiling the sequence of projected 2D matrices into an `.mp4` video file.
4. **Documentation & Testing:**
   - Full Software Requirements Specification (SRS), detailed algorithm specification, unit testing strategy, and experimental benchmarking.

## CLI Usage
```bash
python Ex1.py <file.nrrd> <file.csv> <file.mp4>
```
