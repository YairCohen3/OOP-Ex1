# Test Files

This directory contains the automated tests. The CSV inputs used by the tests are kept in the `csv/` subdirectory.

- `csv/valid_*.csv` and `csv/invalid_*.csv` cover geometry validation.
- `csv/projection_*.csv` and `csv/triangle_near_tip.csv` cover projection behavior.
- `csv/synthetic_cube_planes.csv` is used by the CLI/video test.
- `csv/benchmark_500_planes.csv` contains the planes used by the performance test.
- `csv/MRHead_planes.csv` is an example input for running the application with `data/MRHead.nrrd`.

Run the tests from the project root with `python -m pytest -v`.
