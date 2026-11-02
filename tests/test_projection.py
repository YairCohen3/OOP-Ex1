"""Projection values and volume-boundary checks using synthetic_cube.nrrd."""

import numpy as np
import pytest
import nrrd
from Plane import Plane

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
def test_trapezoid_projection_and_none_plane_fallback(data_dir):
    volume = Volume(str(data_dir / "synthetic_cube.nrrd"))
    trapezoid = Plane([
        (25.0, 20.0, 10.0),
        (35.0, 20.0, 10.0),
        (20.0, 30.0, 10.0),
        (40.0, 30.0, 10.0),
    ])
    frame = Projector.projection(volume, trapezoid)
    assert frame.shape == (round(trapezoid.d_ab), round(trapezoid.d_bc))
    assert np.any(frame == 50)

    black = Projector.projection(volume, None)
    assert black.shape == (1, 1) and black[0, 0] == 0.0


def test_volume_validation_and_get_voxel(data_dir, tmp_path):
    volume = Volume(str(data_dir / "synthetic_cube.nrrd"))
    assert volume.get_voxel(np.array([10.0, 10.0, 10.0])) == 50.0
    assert volume.get_voxel(np.array([-5.0, 10.0, 10.0])) == 0.0

    bad_2d_path = tmp_path / "bad_2d.nrrd"
    nrrd.write(str(bad_2d_path), np.zeros((10, 10), dtype=np.uint8))
    with pytest.raises(ValueError, match="Expected 3D volumetric data"):
        Volume(str(bad_2d_path))
