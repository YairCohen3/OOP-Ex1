# Software Requirements Specification (SRS) & Algorithm Design

## 1. Software Requirements Specification (SRS)

### 1.1 Functional Requirements (FR)
- **FR1 - Load 3D Data:** The system will read 3D matrices from `.nrrd` files with dimensions **sx × sy × sz** (where **1 ≤ sx, sy, sz ≤  2¹⁰**). It must support 8-bit, 16-bit, and 32-bit unsigned integers.
- **FR2 - Read Plane Coordinates:** The system will read a `.csv` file where each row defines a 2D slice (plane) using either 3 3D points **(a, b, c)** (9 floats) or 4 3D points **(a₁, a₂, b, c)** (12 floats).
- **FR3 - Check Geometry:**
  - **For 3 points (a, b, c):** Check that the sides are equal in length: **|dist(a,b) - dist(a,c)| < ε** (where **ε = 0.001**).
  - **For 4 points (a₁, a₂, b, c):** Check that **|dist(a₁,b) - dist(a₂,c)| < ε**, that **dist(a₁,a₂) ≤ dist(b,c)**, and that all 4 points sit on the same flat plane (within **ε**).
- **FR4 - Create 2D Slices:** For each valid plane, the system will calculate a 2D image matrix **E** that shows the cross-section of the 3D volume **M**. Any point outside the 3D volume will be set to `0` (black).
- **FR5 - Export Video:** The system will combine all the 2D slices in order and save them as an `.mp4` video using the command line: `python Ex0.py <file.nrrd> <file.csv> <file.mp4>`.

### 1.2 Non-Functional Requirements (NFR)
- **NFR1 - Speed:** For a **500³** byte volume, the system must process at least 30 frames per second (FPS), aiming for 100+ FPS by using fast NumPy array operations.
- **NFR2 - Stability:** The system must handle edge cases safely without crashing. This includes points outside the volume, zero-length distances (**d₁₂ = 0**), and decimal rounding issues.
- **NFR3 - Clean Code Structure:** The code will use Object-Oriented Design (OOD), keeping data loading, geometry checks, 2D slicing, and video creation in separate, organized parts.

---

## 2. Detailed Algorithm Design

### 2.1 Fixing Edge Cases in the Base Algorithm

> **Overview**  
> The rules below fix potential math and boundary issues in the basic algorithm so the program runs smoothly and quickly.

**One Logic for Triangles and Trapezoids**  
The system uses a single method to handle both shapes. It treats an isosceles triangle simply as a trapezoid where the two top points **(a₁, a₂)** are at the exact same spot.

**Rounding Image Sizes**  
Because image dimensions must be whole numbers (pixels), 3D distances are rounded to the nearest integer to set the `Height` and `Width` of the 2D slice.

**Preventing Division by Zero**  
At the very top point of a triangle, the distance between the left and right edges is `0`. To avoid a "division by zero" crash, the system skips scanning across that row and just samples a single point right in the center.

**Sampling Pixels & Out-of-Bounds Points**  
Decimal 3D coordinates are rounded to the nearest whole number to find the matching pixel in the 3D matrix. If a coordinate falls outside the 3D box, its value is safely set to `0`.

**Fast Array Processing (Vectorization)**  
To reach **100+ FPS**, the code avoids slow `for` loops. Instead, it uses `NumPy` array operations to calculate and fetch all pixels of a 2D slice at the exact same time.

### 2.2 Creating the MP4 Video

After all planes have been projected, the video writer:

1. Finds the maximum pixel value across all frames and scales pixel values to the range `0–255`.
2. Centers each frame on the common-size canvas.
3. Converts each grayscale frame to a three-channel image for video encoding.
4. Writes the frames in their original order to an MP4 file at 30 frames per second.

The throughput printed by the command-line program measures the projection loop only. It does not include volume loading, CSV parsing, or MP4 encoding time.
