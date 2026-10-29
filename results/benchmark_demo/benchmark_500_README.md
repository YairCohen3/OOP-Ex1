# Benchmark Sweep Demo

## Purpose

This demo shows how the project projects a sequence of planes through a synthetic 3D volume. It complements the MRI demo: the benchmark volume is designed to make changes in the projected shape easy to see, while the automated benchmark measures projection throughput.

## Input Data

- `data/benchmark_500.nrrd` — a `500 × 500 × 500` volume stored as unsigned 8-bit voxels (`uint8`). The background value is `0`, and the non-zero spherical region has value `255`.
- `benchmark_500_planes.csv` — 500 isosceles-triangle planes. The triangle stays in the same X/Y position while its Z coordinate moves from `155` toward `345` and then back toward `155`.

As the planes pass through the volume, the intersection with the non-zero region changes size. Near the outside of the sphere, only a small region contains non-zero voxels; nearer the center, the intersection grows. The sampled region is still limited by the triangular plane, which is why the silhouette can change from a rounded shape to a triangle.

## Output Video

- `benchmark_500.mp4` — the MP4 generated from the CSV above.
- The CSV contains 500 planes, so the generated video should contain 500 frames in the same order.
- The video is encoded at 30 frames per second. This is the playback frame rate, not the measured projection throughput.

## Reproduce the Video

Run this command from the project root directory:

```powershell
py .\Ex0.py .\data\benchmark_500.nrrd .\tests\csv\benchmark_500_planes.csv .\results\benchmark_demo\benchmark_500.mp4```

Make sure the output directory exists before running the command.

## Performance Measurement

The automated performance test is separate from video playback. It projects 500 planes from `benchmark_500.nrrd` and calculates throughput as:

`number of projected planes / projection elapsed time`

One recorded run on the development computer processed 500 planes in `3.574` seconds, which is approximately `139.9` planes per second. This exceeds the assignment's required minimum of 30 planes per second and its target of 100 or more planes per second. Results can vary between computers and runs. The measurement covers projection only; it excludes volume loading and MP4 encoding.
