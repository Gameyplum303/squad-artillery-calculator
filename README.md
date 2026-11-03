# Squad Artillery Calculator

A tool that takes a Squad grid location (e.g. where a mortar is set up) and a
target grid location, plus a chosen weapon, and returns:

- **Distance** (meters) from firer to target
- **Bearing** (compass degrees, 0-360, 0 = North) from firer to target
- **Range check** — is the target within the weapon's min/max range?
- **Travel time** (seconds) for the shell to land

This started as a learning project (see git-free history in the docstrings
and TODO-style comments throughout `grid.py`/`ballistics.py`), and now has
a working implementation plus a local GUI (`gui.py`, Tkinter) on top of
it. Tests (`pytest`) cover the math.

**On "getting a player's exact location":** there's no automatic way to
do this, on purpose. Reading it out of a running Squad match would mean
hooking into the game's process memory, which is indistinguishable from a
cheat tool and isn't something this project does. Every legitimate Squad
tool — this one included — works the same way real players do: you read
your own grid callout off Squad's in-game map (it's shown right there on
the map screen) and type it in.

## Squad's grid system (verified facts to build against)

Squad overlays two grids on the map:

1. **Main grid** — letter (column, west→east) + number (row). Example: `B7`.
2. **Keypad** — each main grid square is divided into a 3x3 sub-grid,
   numbered like a **keyboard numpad** (not a phone pad):

   ```
   7 8 9   <- north edge of the square
   4 5 6
   1 2 3   <- south edge of the square
   ```

   1/4/7 are the west column, 3/6/9 are the east column.

3. **Sub-keypad** — the same 3x3 subdivision applied again inside a keypad
   square, for extra precision. A full coordinate looks like `B7-5-3`.

You can specify a location at any of the three precision levels:
`B7`, `B7-5`, or `B7-5-3`.

**Correction (2026-08-27):** an earlier version of this README claimed the
main square's size varies by map (91m/182m/etc). That was wrong — verified
against SquadCalc's actual source
(https://github.com/sh4rkman/SquadCalc/blob/master/src/js/squadGrid.js),
which draws grid lines at fixed intervals of 300 / 3^n meters on every
map, no per-map override. **The main square is always 300m, the keypad
square always 100m, the sub-keypad always ~33.3m.** What varies between
maps is the total *playable area* (anywhere from ~1.4km to ~8km), so
smaller maps just have fewer grid squares across them, not smaller ones.
`GridSystem.main_square_size_m` is still a constructor parameter in this
project (doesn't hurt to keep it configurable), but 300.0 is the correct
value for real Squad and you shouldn't need to change it.

**Open question you should verify in-game before trusting bearings:** does
the row number increase heading south (like reading down a page) or north?
This scaffold assumes row number increases **south** (row 1 near the north
edge), matching how the keypad's 7-8-9 sit at the "top"/north of a square.
Pull up the in-game map on a real match, compare two known grids, and
confirm — if it's backwards, every bearing this tool produces will be
mirrored north-south.

## Coordinate convention

Internally, use a flat Cartesian plane in meters:

- `x` increases **east**
- `y` increases **south** (see open question above — flip this if you
  verify it's actually north-up)

Grid parsing (`grid.py`) turns a grid string into `(x, y)` meters relative
to the map's top-left corner (grid `A1`'s northwest corner = origin).

## The math you'll implement

**Distance** — straight-line distance between two `(x, y)` points. Squad
maps are flat, so this is just the Pythagorean theorem, not haversine.

**Bearing** — compass bearing from firer to target, 0-360° where 0=North,
90=East. This is an `atan2` of the delta x/y, then converted from
mathematical angle convention to compass convention, then normalized into
`[0, 360)`.

**Altitude / height difference.** Mortars fire on an arc, so firing at a
target that's higher or lower than you changes both the angle you need
and how long the shell takes to arrive — a shot fired downhill at a fixed
angle travels farther than the same shot on flat ground, and vice versa.
This project doesn't have access to Squad's actual per-map heightmap data
(real Squad reads target elevation off a heightmap image bundled with
each map), so altitude is a manual input here: you supply
`height_diff_m` (target altitude minus firer altitude) yourself rather
than it being derived from the grid string.

**Elevation angle & travel time** — rather than a flat-ground lookup
table, this project uses real projectile-motion physics (the same
approach SquadCalc uses — see
https://github.com/sh4rkman/SquadCalc/wiki/Deducing-Elevation and
.../Deducing-Time-Of-Flight): given the weapon's muzzle velocity and
gravity, there are generally two firing angles that reach a given
distance — a lobbing "high angle" and a flatter "low angle" — and each
implies its own time of flight. Squad's mortars are high-angle-only tubes
(`min_elevation_deg` in `weapons.py` reflects that), so the CLI always
asks for the high-angle solution. Whether a target is even reachable now
genuinely depends on both distance *and* height difference, not distance
alone — see `elevation_angle()`'s docstring in `ballistics.py`.

Weapon constants (`weapons.py`) — muzzle velocity, minimum range, and the
elevation limits the tube can physically reach — are pulled from
SquadCalc's own data file (`src/data/weapons.js`), not guessed. All 19
weapons it lists are included (23 entries once a couple of multi-shell
weapons are split out), spanning vanilla infantry/vehicle weapons and
several community mods (SuperMod, Infinite Warfare, Steel Division, Squad
AdminTools) — each entry's `mod` field says which. `elevation_angle()`/
`time_of_flight()` should work unmodified for all of them once
implemented; `cli.py` already picks each weapon's real firing mode
(`angle_type`) rather than assuming every weapon is a high-angle mortar.

## Project layout

```
src/squad_arty_calc/
  grid.py        # grid string <-> (x, y) meters
  ballistics.py  # distance, bearing, elevation_angle, time_of_flight, in_range
  weapons.py     # reference data: 23 weapon/shell entries, vanilla + modded
  cli.py         # command-line tool
  gui.py         # local Tkinter desktop GUI
tests/
  test_grid.py
  test_ballistics.py
```

## Running it

GUI (recommended):
```
pip install -r requirements.txt
python -m squad_arty_calc.gui
```

CLI:
```
python -m squad_arty_calc.cli B7-5 D3-2-6 mortar
python -m squad_arty_calc.cli B7-5 D3-2-6 mortar --firer-alt 120 --target-alt 60
```
(Run either from the project root, or `pip install -e .` first — both need `src` importable; `pytest` already handles this via `pyproject.toml`.)

## Milestones

- [x] `grid.py`: parse a grid string into `(x, y)` meters, and the inverse (`to_grid`)
- [x] `ballistics.py`: `distance`, `bearing`, `elevation_angle`, `time_of_flight`, `in_range`
- [x] `cli.py` and `gui.py`: both wired up end to end
- [x] Weapon roster expanded to all 19 weapons (23 entries) from SquadCalc's data, including mods
- [ ] Verify grid row-direction assumption (north vs. south) against a real match — the math is implemented and internally consistent, but this specific assumption is still unverified against actual gameplay
- [ ] Stretch: MOA/spread — how precise a shot actually is, not just where it aims
- [ ] Stretch: real per-map heightmaps instead of manual `height_diff_m` — decided 2026-08-27 to stay manual for now (see "Altitude / height difference" above). If revisited: elevation data would come from
      [Squad-Wiki Pipeline Map Data](https://github.com/Squad-Wiki/squad-wiki-pipeline-map-data),
      an open-source SDK extractor (not something to scrape off SquadCalc's
      live server) — decode is `height = (255 + r - b) * scale` on an
      8-bit R/B PNG, looked up via a pixel-per-meter scale factor.
- [ ] Stretch: a clickable map image (like SquadCalc's) instead of typing grid strings — would need Squad map imagery, a separate asset question from the code itself

## Credit

Domain facts, formulas, and weapon constants here were cross-checked
against [SquadCalc](https://github.com/sh4rkman/SquadCalc), an open-source
community mortar calculator for Squad, as of 2026-08-27. This project is
an independent learning exercise, not a fork of or affiliated with it —
worth a look at their source/wiki if you get stuck or want to see a
complete reference implementation after building your own.

## Running tests

```
pip install -r requirements.txt
pytest
```
