"""Geometry checks described in docs/Testing_and_Dataset.md."""

import pytest
from Plane import Plane
from IO_Utils import load_planes_from_csv


def test_valid_isosceles_triangle_is_accepted(csv_dir):
    planes = load_planes_from_csv(str(csv_dir / "valid_triangle.csv"))
    assert len(planes) == 1
    assert planes[0].d_ab == pytest.approx(10.0)


def test_triangle_with_unequal_legs_is_rejected(csv_dir):
    with pytest.raises(ValueError, match="Triangle legs are not equal"):
        load_planes_from_csv(str(csv_dir / "invalid_triangle.csv"))


def test_valid_isosceles_trapezoid_is_accepted(csv_dir):
    planes = load_planes_from_csv(str(csv_dir / "valid_trapezoid.csv"))
    assert len(planes) == 1
    assert planes[0].d_ab == pytest.approx(10.0)


def test_trapezoid_with_unequal_legs_is_rejected(csv_dir):
    with pytest.raises(ValueError, match="Trapezoid legs are not equal"):
        load_planes_from_csv(str(csv_dir / "invalid_trapezoid_unequal_legs.csv"))


def test_non_coplanar_trapezoid_is_rejected(csv_dir):
    with pytest.raises(ValueError, match="Points are not coplanar"):
        load_planes_from_csv(str(csv_dir / "invalid_trapezoid_non_coplanar.csv"))
def test_collinear_triangle_is_rejected():
    points = [
        (0, 0, 0),
        (10, 0, 0),
        (-10, 0, 0),
    ]

    with pytest.raises(ValueError, match="collinear"):
        Plane(points)


def test_non_finite_triangle_coordinates_are_rejected():
    points = [
        (float("nan"), 0, 0),
        (10, 0, 0),
        (0, 10, 0),
    ]

    with pytest.raises(ValueError, match="finite"):
        Plane(points)


def test_trapezoid_with_top_base_longer_than_bottom_is_rejected():
    points = [
        (-2, 0, 0),
        (2, 0, 0),
        (-1, 3, 0),
        (1, 3, 0),
    ]

    with pytest.raises(
        ValueError, match="Top base is larger than bottom base"
    ):
        Plane(points)