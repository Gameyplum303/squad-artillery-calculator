[![Tests](https://github.com/Gameyplum303/squad-artillery-calculator/actions/workflows/tests.yml/badge.svg)](https://github.com/Gameyplum303/squad-artillery-calculator/actions/workflows/tests.yml)

# Squad Artillery Calculator

A firing-solution calculator for the game Squad. Give it where your mortar is, where the target is and which weapon
you're using, and it returns:

- **Distance** in meters from firer to target
- **Bearing** in compass degrees (0 = North)
- **Elevation** to set on the tube, accounting for the height difference between firer and target
- **Time of flight** for the shell to land
- **Range check**: whether the weapon can reach the target at all

It runs as a desktop app (Tkinter) or from the command line, and covers 23 weapon and shell entries, including several
community mods.

You read your own grid callout off Squad's in-game map and type it in, the same way every legitimate Squad tool works.
Nothing reads the running game.

## Run it

Python 3.10 or newer. From the project folder:

```bash
python -m pip install -e .
```

```bash
squad-arty-gui
```

Or from the command line:

```bash
squad-arty B7-5 C5-7-5 mortar
squad-arty B7-5 C5-7-5 mortar --firer-alt 120 --target-alt 60
```

## Squad's grid system

1. **Main grid**: a column letter (west to east) and a row number (north to south), such as `B7`. Each square is
   300 m on every map; bigger maps just have more squares.
2. **Keypad**: each square splits into a 3x3 grid numbered like a keyboard numpad, so 7-8-9 is the north row and
   1-2-3 the south row. Each keypad square is 100 m.
3. **Sub-keypad**: the same split again, about 33 m. A full reference looks like `B7-5-3`.

Locations can be given at any of the three levels: `B7`, `B7-5` or `B7-5-3`. Internally, `x` increases east and `y`
increases south from the north-west corner of `A1`. Row numbering (row 1 at the north edge, increasing southward)
matches SquadCalc's grid code.

## How the math works

- **Distance** is straight-line ground distance. Squad maps are flat, so this is the Pythagorean theorem.
- **Bearing** is `atan2` of the offsets, converted from math convention (0 = East, counterclockwise) to compass
  convention (0 = North, clockwise) and normalized to 0-360.
- **Elevation** solves the projectile-range equation for launch angle from the weapon's muzzle velocity, gravity,
  distance and height difference. There are usually two answers, a flat low-angle shot and a lobbing high-angle one,
  and each weapon's firing mode decides which is used. Shooting downhill reaches farther than on flat ground and uphill
  falls short, so reachability depends on both distance and height.
- **Time of flight** solves the vertical motion equation for the chosen angle.

Squad reads target height from per-map heightmaps that aren't part of this project, so the height difference is an
input (`--firer-alt` and `--target-alt`, or the fields in the app).

## Project layout

```
src/squad_arty_calc/
  grid.py        grid reference <-> (x, y) meters
  ballistics.py  distance, bearing, elevation angle, time of flight, range check
  weapons.py     weapon and shell figures (23 entries, vanilla and modded)
  cli.py         command-line tool
  gui.py         Tkinter desktop app
tests/           pytest suite for the grid and ballistics math
```

## Tests

```bash
python -m pip install -e ".[test]"
python -m pytest
```

## Credit

Grid layout, formulas and weapon figures were checked against [SquadCalc](https://github.com/sh4rkman/SquadCalc), an
open-source community mortar calculator for Squad. This project is independent and not affiliated with it. The weapon
figures in `weapons.py` come from SquadCalc's data and stay under its license terms; see [LICENSE](LICENSE).
