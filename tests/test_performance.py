"""Measure projection throughput on 500 planes from benchmark_500.nrrd."""

import time

from IO_Utils import load_planes_from_csv
from Projector import Projector
from Volume import Volume


def test_500_planes_on_500_cube_meets_minimum_throughput(project_root, data_dir, csv_dir):
    volume = Volume(str(data_dir / "benchmark_500.nrrd"))
    assert (volume.sx, volume.sy, volume.sz) == (500, 500, 500)

    planes = load_planes_from_csv(str(csv_dir / "benchmark_500_planes.csv"))
    assert len(planes) == 500, f"Expected 500 planes, found {len(planes)}"

    start = time.perf_counter()
    for plane in planes:
        frame = Projector.projection(volume, plane)
        assert frame.size > 0
    elapsed = time.perf_counter() - start
    fps = len(planes) / elapsed if elapsed > 0 else float("inf")

    print(
        f"({fps:.1f} FPS)"
    )
    assert fps >= 30, f"Required minimum is 30 planes/s; measured ({fps:.1f} FPS)"
