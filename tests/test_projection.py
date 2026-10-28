"""Projection values and volume-boundary checks using synthetic_cube.nrrd."""

import numpy as np

from IO_Utils import load_planes_from_csv
from Projector import Projector
from Volume import Volume


def test_axis_aligned_projection_matches_known_synthetic_values(data_dir, csv_dir):
    volume = Volume(str(data_dir / "synthetic_cube.nrrd"))
    plane = load_planes_from_csv(str(csv_dir / "projection_inside.csv"))[0]

    frame = Projector.projection(volume, plane)

    assert frame.shape == (10, 14)
    # This triangle lies in the known background region of the synthetic volume,
    # where every sampled voxel has value 50. Unfilled pixels remain zero.
    assert frame[0, 6] == 50
    assert frame[0, 7] == 50
    assert np.any(frame == 50)
    assert np.all((frame == 0) | (frame == 50))


def test_plane_fully_outside_volume_produces_zeros(data_dir, csv_dir):
    volume = Volume(str(data_dir / "synthetic_cube.nrrd"))
    plane = load_planes_from_csv(str(csv_dir / "projection_outside.csv"))[0]

    frame = Projector.projection(volume, plane)

    assert frame.size > 0
    assert np.all(frame == 0)


def test_plane_partly_outside_volume_keeps_valid_samples(data_dir, csv_dir):
    volume = Volume(str(data_dir / "synthetic_cube.nrrd"))
    plane = load_planes_from_csv(str(csv_dir / "projection_partial.csv"))[0]

    frame = Projector.projection(volume, plane)

    assert np.any(frame == 50)
    assert np.any(frame == 0)
    assert np.all(np.isfinite(frame))


def test_small_triangle_near_tip_does_not_crash(data_dir, csv_dir):
    volume = Volume(str(data_dir / "synthetic_cube.nrrd"))
    plane = load_planes_from_csv(str(csv_dir / "triangle_near_tip.csv"))[0]

    frame = Projector.projection(volume, plane)

    assert frame.shape == (1, 1)
    assert np.all(np.isfinite(frame))
