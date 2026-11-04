"""Command-line entry point.

Once grid.py and ballistics.py are implemented, this will run end to end:

    python -m squad_arty_calc.cli B7-5 D3-2-6 mortar
    python -m squad_arty_calc.cli B7-5 D3-2-6 mortar --firer-alt 120 --target-alt 80

Nothing to implement here yet unless you want to improve on it (better
argument parsing, interactive prompts, etc.) — it's a thin wrapper around
the pieces you're building elsewhere.
"""

import argparse
import sys

from squad_arty_calc import ballistics
from squad_arty_calc.grid import GridSystem
from squad_arty_calc.weapons import WEAPONS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firer_grid", help='e.g. "B7-5"')
    parser.add_argument("target_grid", help='e.g. "D3-2-6"')
    parser.add_argument("weapon", choices=sorted(WEAPONS), help="weapon key")
    parser.add_argument(
        "--square-size",
        type=float,
        default=300.0,
        help="main grid square size in meters (Squad always uses 300)",
    )
    parser.add_argument(
        "--firer-alt", type=float, default=0.0, help="firer altitude in meters"
    )
    parser.add_argument(
        "--target-alt", type=float, default=0.0, help="target altitude in meters"
    )
    args = parser.parse_args(argv)

    grid = GridSystem(main_square_size_m=args.square_size)
    weapon = WEAPONS[args.weapon]

    firer_xy = grid.parse(args.firer_grid)
    target_xy = grid.parse(args.target_grid)
    height_diff = args.target_alt - args.firer_alt

    dist = ballistics.distance(firer_xy, target_xy)
    brg = ballistics.bearing(firer_xy, target_xy)

    print(f"Distance: {dist:.1f} m")
    print(f"Bearing:  {brg:.1f} deg")

    if not ballistics.in_range(weapon, dist, height_diff):
        print(f"WARNING: {weapon.name} cannot reach a target {dist:.1f} m away "
              f"with a height difference of {height_diff:+.1f} m.")
        return 0

    # Use whichever trajectory this weapon is actually crewed for (mortars
    # are high-angle-only; direct-fire weapons like Mk19 use low angle) --
    # see weapon.angle_type in weapons.py.
    angle = ballistics.elevation_angle(
        weapon, dist, height_diff, low_angle=(weapon.angle_type == "low")
    )
    ttof = ballistics.time_of_flight(weapon, angle, height_diff)
    print(f"Elevation:    {angle:.2f} deg")
    print(f"Travel time:  {ttof:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
