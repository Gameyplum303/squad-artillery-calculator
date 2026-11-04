"""Local desktop GUI for the Squad artillery calculator.

Run with:
    python -m squad_arty_calc.gui

Uses Tkinter (bundled with Python, no extra install needed). There is
deliberately no way to auto-detect where a player is standing -- that
would mean reading the game's process memory, which is indistinguishable
from a cheat tool and out of scope. Instead this mirrors how every
legitimate Squad tool works: you read your own grid callout off Squad's
in-game map and type it in here.
"""

import tkinter as tk
from tkinter import ttk

from squad_arty_calc import ballistics
from squad_arty_calc.grid import GridSystem
from squad_arty_calc.weapons import WEAPONS

MIL_PER_DEG = 6400 / 360

CATEGORY_LABELS = {
    "deployable": "Vanilla - Infantry / Emplacement",
    "vehicle": "Vanilla - Vehicle-mounted",
    "modded": "Modded",
}


def weapon_display_name(key: str) -> str:
    weapon = WEAPONS[key]
    if weapon.mod:
        return f"{weapon.name} [{weapon.mod}]"
    return weapon.name


def grouped_weapon_choices() -> list[str]:
    """Weapon dropdown entries, grouped by category then sorted by name,
    with a non-selectable header row per group."""
    choices: list[str] = []
    for category in ("deployable", "vehicle", "modded"):
        keys = sorted(
            (k for k, w in WEAPONS.items() if w.category == category),
            key=lambda k: WEAPONS[k].name,
        )
        if not keys:
            continue
        choices.append(f"-- {CATEGORY_LABELS[category]} --")
        choices.extend(weapon_display_name(k) for k in keys)
    return choices


DISPLAY_TO_KEY = {weapon_display_name(k): k for k in WEAPONS}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Squad Artillery Calculator")
        self.resizable(False, False)
        self.grid_system = GridSystem()
        self._build_widgets()

    def _build_widgets(self):
        pad = {"padx": 8, "pady": 4}
        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        row = 0
        ttk.Label(frm, text="Weapon").grid(row=row, column=0, sticky="w", **pad)
        self.weapon_var = tk.StringVar()
        weapon_choices = grouped_weapon_choices()
        self.weapon_box = ttk.Combobox(
            frm, textvariable=self.weapon_var, values=weapon_choices,
            state="readonly", width=42,
        )
        self.weapon_box.grid(row=row, column=1, columnspan=2, sticky="w", **pad)
        self.weapon_box.set(weapon_display_name("mortar"))
        row += 1

        ttk.Separator(frm, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=6
        )
        row += 1

        ttk.Label(frm, text="Firer grid").grid(row=row, column=0, sticky="w", **pad)
        self.firer_grid_var = tk.StringVar(value="B7-5")
        ttk.Entry(frm, textvariable=self.firer_grid_var, width=16).grid(
            row=row, column=1, sticky="w", **pad
        )
        ttk.Label(frm, text="Altitude (m)").grid(row=row, column=2, sticky="w", **pad)
        self.firer_alt_var = tk.StringVar(value="0")
        ttk.Entry(frm, textvariable=self.firer_alt_var, width=8).grid(
            row=row, column=3, sticky="w", **pad
        )
        row += 1

        ttk.Label(frm, text="Target grid").grid(row=row, column=0, sticky="w", **pad)
        self.target_grid_var = tk.StringVar(value="D3-2-6")
        ttk.Entry(frm, textvariable=self.target_grid_var, width=16).grid(
            row=row, column=1, sticky="w", **pad
        )
        ttk.Label(frm, text="Altitude (m)").grid(row=row, column=2, sticky="w", **pad)
        self.target_alt_var = tk.StringVar(value="0")
        ttk.Entry(frm, textvariable=self.target_alt_var, width=8).grid(
            row=row, column=3, sticky="w", **pad
        )
        row += 1

        ttk.Button(frm, text="Calculate", command=self.calculate).grid(
            row=row, column=0, columnspan=4, sticky="ew", **pad
        )
        row += 1

        ttk.Separator(frm, orient="horizontal").grid(
            row=row, column=0, columnspan=4, sticky="ew", pady=6
        )
        row += 1

        self.result_var = tk.StringVar(value="Enter grids and press Calculate.")
        ttk.Label(
            frm, textvariable=self.result_var, justify="left",
            font=("Consolas", 10),
        ).grid(row=row, column=0, columnspan=4, sticky="w", **pad)

    def calculate(self):
        weapon_key = DISPLAY_TO_KEY.get(self.weapon_var.get())
        if weapon_key is None:
            self.result_var.set("Pick a weapon (not a category header).")
            return
        weapon = WEAPONS[weapon_key]

        try:
            firer_xy = self.grid_system.parse(self.firer_grid_var.get())
            target_xy = self.grid_system.parse(self.target_grid_var.get())
            firer_alt = float(self.firer_alt_var.get() or 0)
            target_alt = float(self.target_alt_var.get() or 0)
        except (ValueError, KeyError, IndexError) as exc:
            self.result_var.set(f"Input error: {exc}")
            return

        height_diff = target_alt - firer_alt
        dist = ballistics.distance(firer_xy, target_xy)
        brg = ballistics.bearing(firer_xy, target_xy)

        lines = [
            f"Distance:  {dist:8.1f} m",
            f"Bearing:   {brg:8.1f} deg",
        ]

        if not ballistics.in_range(weapon, dist, height_diff):
            lines.append("")
            lines.append(
                f"OUT OF RANGE for {weapon.name}\n"
                f"(min {weapon.min_distance_m:.0f} m, height diff {height_diff:+.1f} m)"
            )
            self.result_var.set("\n".join(lines))
            return

        low_angle = weapon.angle_type == "low"
        angle = ballistics.elevation_angle(weapon, dist, height_diff, low_angle=low_angle)
        ttof = ballistics.time_of_flight(weapon, angle, height_diff)

        lines.append(f"Elevation: {angle:8.2f} deg  ({angle * MIL_PER_DEG:.0f} mil)")
        lines.append(f"Travel time: {ttof:6.1f} s")
        self.result_var.set("\n".join(lines))


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
