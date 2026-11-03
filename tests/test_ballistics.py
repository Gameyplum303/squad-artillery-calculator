import pytest

from squad_arty_calc import ballistics
from squad_arty_calc.weapons import WEAPONS

MORTAR = WEAPONS["mortar"]


def test_distance_pythagorean_triple():
    assert ballistics.distance((0, 0), (3, 4)) == pytest.approx(5.0)


def test_distance_zero():
    assert ballistics.distance((100, 100), (100, 100)) == pytest.approx(0.0)


def test_bearing_north():
    # y increases south in this project's convention, so "north" is -y
    assert ballistics.bearing((0, 0), (0, -10)) == pytest.approx(0.0)


def test_bearing_east():
    assert ballistics.bearing((0, 0), (10, 0)) == pytest.approx(90.0)


def test_bearing_south():
    assert ballistics.bearing((0, 0), (0, 10)) == pytest.approx(180.0)


def test_bearing_west():
    assert ballistics.bearing((0, 0), (-10, 0)) == pytest.approx(270.0)


def test_bearing_northeast():
    assert ballistics.bearing((0, 0), (10, -10)) == pytest.approx(45.0)


def test_elevation_angle_flat_ground_high_angle():
    # cross-checked against SquadCalc's own formula, see ballistics.py docstring
    angle = ballistics.elevation_angle(MORTAR, 500.0, height_diff_m=0.0, low_angle=False)
    assert angle == pytest.approx(78.08696, abs=0.001)


def test_elevation_angle_low_angle_rejected_for_high_angle_only_tube():
    # the low-angle solution at 500m is ~11.8 degrees, but this mortar's
    # min_elevation_deg is (45, 88.875) -- it physically can't point that
    # low, so this must come back None rather than an out-of-bounds angle
    angle = ballistics.elevation_angle(MORTAR, 500.0, height_diff_m=0.0, low_angle=True)
    assert angle is None


def test_elevation_angle_beyond_max_range_returns_none():
    # flat-ground max range is ~1237m (45 degrees, the tube's own minimum
    # elevation) -- 1400m has no valid trajectory at all
    angle = ballistics.elevation_angle(MORTAR, 1400.0, height_diff_m=0.0, low_angle=False)
    assert angle is None


def test_elevation_angle_uphill_needs_less_angle_than_downhill():
    # firing at a target 50m higher vs. 50m lower than the mortar, same
    # horizontal distance -- uphill needs a flatter angle, downhill a
    # steeper one, to land at the same 500m
    uphill = ballistics.elevation_angle(MORTAR, 500.0, height_diff_m=50.0, low_angle=False)
    downhill = ballistics.elevation_angle(MORTAR, 500.0, height_diff_m=-50.0, low_angle=False)
    assert uphill == pytest.approx(77.80722, abs=0.001)
    assert downhill == pytest.approx(78.34198, abs=0.001)


def test_time_of_flight_flat_ground():
    t = ballistics.time_of_flight(MORTAR, elevation_deg=78.08696, height_diff_m=0.0)
    assert t == pytest.approx(22.01039, abs=0.001)


def test_time_of_flight_uphill():
    t = ballistics.time_of_flight(MORTAR, elevation_deg=77.80722, height_diff_m=50.0)
    assert t == pytest.approx(21.51215, abs=0.001)


def test_in_range_within_bounds():
    assert ballistics.in_range(MORTAR, 500.0) is True


def test_in_range_beyond_max_range():
    assert ballistics.in_range(MORTAR, 1400.0) is False


def test_in_range_below_min_distance():
    # 30m is closer than min_distance_m (51), even though a steep enough
    # angle might physically reach it -- the tube's minimum range rules
    # it out regardless
    assert ballistics.in_range(MORTAR, 30.0) is False
