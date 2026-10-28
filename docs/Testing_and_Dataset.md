# Dataset Definition & Testing Strategy

## 1. NRRD Dataset Definition

To thoroughly test that the output looks right, the math is correct, and the code runs fast, our dataset uses three `.nrrd` files:

1. **Real-World Medical Data (`MRHead.nrrd`):**
   - **Source:** 3D Slicer Open-Source Sample Data.
   - **Purpose:** Visually checking different cross-sections (oblique, axial, sagittal, coronal) on a real MRI head scan.

2. **Simple Test Volume (`synthetic_cube.nrrd`):**
   - **Dimensions:** 100 x 100 x 100 (8-bit unsigned integers, `uint8`).
   - **Content:** Simple, known patterns (like a solid inner block of value 200 surrounded by 50, or basic coordinate values like M[x, y, z] = x).
   - **Purpose:** Checking the exact numbers in our unit tests, since we already know exactly what the 2D output matrix E should look like.

3. **Speed Test Volume (`benchmark_500.nrrd`):**
   - **Dimensions:** 500 x 500 x 500 (`uint8` byte values).
   - **Purpose:** Stress-testing the code's speed to make sure it meets the required 30 FPS minimum (while aiming for 100+ FPS).

---

## 2. Testing Strategy

We use Python's `pytest` framework to run automatic tests in four main areas:

### 2.1 Unit Testing (Geometry & Rules)
- **Isosceles Triangle (3 Points):**
  - Check valid points (a, b, c) where the leg distances are virtually identical (difference is less than 0.001).
  - Check invalid points where the distances are too different, and make sure the code handles the error properly.
- **Isosceles Trapezoid (4 Points):**
  - Check valid points (a1, a2, b, c) where the legs are equal in length, the top is shorter than or equal to the base, and all four points sit flat on the same plane.
  - Test uneven legs or points that don't sit on the same plane to make sure the program rejects them.

### 2.2 Algorithm & Boundary Tests (Projection Logic)
- **Inside the Grid:** Cut a straight, axis-aligned slice through `synthetic_cube.nrrd` and make sure the values in E perfectly match the original 3D matrix M.
- **Outside the Grid:** Place a plane partly or completely outside the 3D limits ([0, sx) x [0, sy) x [0, sz)) and make sure all outside pixels in E are set to 0.
- **Edge Cases:** Test what happens when distances are close to zero (like at the top tip of the triangle) to make sure the code doesn't crash by dividing by zero.

### 2.3 Full Run & Command Line Tests
- **Running the Code:** Run `python Ex0.py <file.nrrd> <file.csv> <file.mp4>` using subprocess.
- **Checking the Output:**
  - Make sure the `<file.mp4>` video is actually created and isn't empty.
  - Open the video with OpenCV (`cv2.VideoCapture`) and count the frames. Make sure the total frame count exactly matches the number of rows in the `<file.csv>`.

### 2.4 Speed & FPS Tests
- Time how long it takes to process 100 planes on the large 500^3 file (`benchmark_500.nrrd`).
- Make sure the average speed is clearly over the required 30 FPS mark (with a goal of passing 100 FPS).