"""Distance, bearing, elevation angle, and travel-time calculations.

See README.md "How the math works" for an overview.

Formulas here are cross-checked against SquadCalc's source
(https://github.com/sh4rkman/SquadCalc — src/js/squadFiringSolution.js),
a widely-used community mortar calculator, and its wiki writeups:
  - distance/bearing: https://github.com/sh4rkman/SquadCalc/wiki/Deducing-distance-and-bearing
  - elevation angle:  https://github.com/sh4rkman/SquadCalc/wiki/Deducing-Elevation
  - time of flight:   https://github.com/sh4rkman/SquadCalc/wiki/Deducing-Time-Of-Flight
Those pages walk through each formula in more detail.

Altitude is NOT part of the grid coordinates in this project (real Squad
derives it from a per-map heightmap image, which we don't have). Instead,
functions that need it take a separate height_diff_m: target altitude
minus firer altitude, in meters, which you'd supply manually (e.g. by
reading elevation off the in-game map).
"""

import math

from squad_arty_calc.weapons import GRAVITY_MPS2, Weapon


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Straight-line HORIZONTAL distance in meters between two (x, y)
    points. This is ground distance only — altitude is handled
    separately by elevation_angle()/time_of_flight(), matching how
    Squad's own distance calc works (it never touches height).

    Squad maps are flat, so this is the Pythagorean theorem: sqrt(dx**2 + dy**2).
    """
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    return math.hypot(dx, dy)


def bearing(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Compass bearing in degrees [0, 360) from point a to point b,
    where 0 = North, 90 = East, 180 = South, 270 = West.

    atan2's convention (0 = East, counterclockwise) differs from the
    compass (0 = North, clockwise), and y increases south here, so the
    deltas are swapped and dy negated before calling atan2. Negative
    results are shifted into [0, 360).
    """
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    angle_rad = math.atan2(dx, -dy)  # swap dx/dy and negate dy to convert to compass convention
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360
    return angle_deg


def elevation_angle(
    weapon: Weapon,
    distance_m: float,
    height_diff_m: float = 0.0,
    low_angle: bool = True,
) -> float | None:
    """The barrel angle (degrees above horizontal) weapon needs to be
    set to land a shell at distance_m with the target height_diff_m
    higher (positive) or lower (negative) than the firer.

    Returns None if the target can't be hit at all — either no real
    trajectory exists (target too far/too extreme a height difference
    for this weapon's velocity), or the required angle falls outside
    weapon.min_elevation_deg.

    This replaces a simpler "min/max range" check: because height
    difference changes how far a shell can reach (firing downhill
    reaches farther than the flat-ground range, uphill falls short),
    whether a target is "in range" now depends on distance AND height,
    not distance alone.

    This is the standard projectile-range equation solved for launch
    angle, given initial speed v, gravity g, distance d and height
    difference h. There are generally two solutions, a flatter "low
    angle" trajectory and a lobbing "high angle" one, chosen by low_angle:

        g_eff = GRAVITY_MPS2 * weapon.gravity_scale
        v = weapon.velocity_mps
        h = height_diff_m - weapon.height_offset_m

        discriminant = v**4 - g_eff * (g_eff * distance_m**2 + 2 * h * v**2)
        # discriminant < 0 means no real trajectory: return None

        p1 = sqrt(discriminant)
        angle_term = -p1 if low_angle else p1

        angle_rad = atan((v**2 + angle_term) / (g_eff * distance_m))
        angle_deg = degrees(angle_rad)

        # an angle outside weapon.min_elevation_deg can't be fired: return None

    A distance of zero (or less) returns None: nothing can be fired at
    zero range, and the last step would divide by zero.
    """
    if distance_m <= 0:
        return None

    g_eff = GRAVITY_MPS2 * weapon.gravity_scale
    v = weapon.velocity_mps
    h = height_diff_m - weapon.height_offset_m

    discriminant = v**4 - g_eff * (g_eff * distance_m**2 + 2 * h * v**2)
    if discriminant < 0:
        return None

    p1 = math.sqrt(discriminant)
    angle_term = -p1 if low_angle else p1

    angle_rad = math.atan((v**2 + angle_term) / (g_eff * distance_m))
    angle_deg = math.degrees(angle_rad)

    lo, hi = weapon.min_elevation_deg
    if angle_deg < lo or angle_deg > hi:
        return None

    return angle_deg


def time_of_flight(
    weapon: Weapon,
    elevation_deg: float,
    height_diff_m: float = 0.0,
) -> float:
    """Seconds for the shell to reach a target height_diff_m above/below
    the firer, given it's fired at elevation_deg (from elevation_angle()).

    This solves the vertical motion equation for time:

        g_eff = GRAVITY_MPS2 * weapon.gravity_scale
        v = weapon.velocity_mps
        angle_rad = radians(elevation_deg)

        t = (v * sin(angle_rad)
             + sqrt(v**2 * sin(angle_rad)**2 - 2 * g_eff * height_diff_m)
             ) / g_eff

    The sqrt's argument can go negative for extreme low-angle shots
    with a big height difference. Like SquadCalc, this falls back to the
    flat-ground formula (dropping height_diff_m) instead of failing.
    """
    g_eff = GRAVITY_MPS2 * weapon.gravity_scale
    v = weapon.velocity_mps
    angle_rad = math.radians(elevation_deg)

    inner = v**2 * math.sin(angle_rad) ** 2 - 2 * g_eff * height_diff_m
    if inner < 0:
        inner = v**2 * math.sin(angle_rad) ** 2

    return (v * math.sin(angle_rad) + math.sqrt(inner)) / g_eff


def in_range(weapon: Weapon, distance_m: float, height_diff_m: float = 0.0) -> bool:
    """Whether the target is reachable at all: distance_m is at least
    weapon.min_distance_m, AND at least one of the low/high angle
    solutions from elevation_angle() exists.
    """
    if distance_m < weapon.min_distance_m:
        return False

    return (
        elevation_angle(weapon, distance_m, height_diff_m, low_angle=True) is not None
        or elevation_angle(weapon, distance_m, height_diff_m, low_angle=False) is not None
    )
