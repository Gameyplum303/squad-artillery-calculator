import pytest

from squad_arty_calc.grid import GridSystem


@pytest.fixture
def grid():
    return GridSystem(main_square_size_m=300.0)


def approx(point, expected):
    assert point[0] == pytest.approx(expected[0], abs=0.01)
    assert point[1] == pytest.approx(expected[1], abs=0.01)


def test_parse_main_grid_only(grid):
    approx(grid.parse("A1"), (150.0, 150.0))


def test_parse_main_grid_second_square(grid):
    # col B = index 1, row 7 = index 6
    approx(grid.parse("B7"), (450.0, 1950.0))


def test_parse_keypad_nw(grid):
    approx(grid.parse("A1-7"), (50.0, 50.0))


def test_parse_keypad_ne(grid):
    approx(grid.parse("A1-9"), (250.0, 50.0))


def test_parse_keypad_sw(grid):
    approx(grid.parse("A1-1"), (50.0, 250.0))


def test_parse_keypad_center_equals_main_center(grid):
    # keypad 5 is the center third, so it should match the plain "A1" center
    approx(grid.parse("A1-5"), grid.parse("A1"))


def test_parse_sub_keypad(grid):
    approx(grid.parse("A1-7-3"), (83.33, 83.33))


def test_parse_respects_custom_square_size():
    small = GridSystem(main_square_size_m=91.0)
    approx(small.parse("A1"), (45.5, 45.5))


def test_to_grid_round_trip_main(grid):
    assert grid.to_grid(450.0, 1950.0, precision=1) == "B7"


def test_to_grid_round_trip_keypad(grid):
    assert grid.to_grid(50.0, 50.0, precision=2) == "A1-7"
