"""Weapon reference data.

This file is data, not logic: the figures each weapon needs for a firing solution.

Every entry here is pulled directly from SquadCalc's source
(https://github.com/sh4rkman/SquadCalc, src/data/weapons.js and
src/app.js), a widely-used community mortar calculator, as of
2026-08-27. That file lists 19 weapons; several (M1064M121, MO120RTF1,
PZL07) fire more than one shell type with different stats, so those are
split into separate entries here (e.g. "m1064_120mm_impact" and
"m1064_120mm_nearsurface") — this project selects one weapon+shell
combination at a time, it doesn't model choosing a shell type separately.

Weapons are grouped by category:
  - vanilla infantry/emplacement ("deployables" in the source)
  - vanilla vehicle-mounted ("vehicles")
  - modded (each tagged with which mod it comes from)

GRAVITY_MPS2 is Squad's global gravity constant — notably not 9.81, the
game uses 9.78.

Fields angle_offset_deg, deceleration_mps2, deceleration_time_s, and
projectile_lifespan_s are carried over for completeness but NOT currently
used by anything in ballistics.py (deceleration matters for rockets like
the UB-32/Grad/HIMARS, which slow down after a boost phase instead of
flying a pure gravity-only arc — modeling that would mean simulating the
trajectory in small time steps rather than solving one closed-form
equation, a bigger step up in complexity than plain mortars). Explosion-
related fields (damage/radius/falloff) aren't used by anything here
either — they're for a damage calculator, out of this project's scope,
kept only because "pull all the data" means all the data.
"""

from dataclasses import dataclass


GRAVITY_MPS2 = 9.78


@dataclass
class Weapon:
    name: str
    velocity_mps: float
    min_distance_m: float
    min_elevation_deg: tuple[float, float]  # (low, high) angle bounds the tube can physically reach
    angle_type: str  # "high" or "low" -- which solution real crews actually use
    unit: str  # elevation display unit in-game: "mil", "deg", or "degMin"
    category: str  # "deployable", "vehicle", or "modded"
    mod: str | None = None  # mod name, or None for vanilla Squad
    height_offset_m: float = 0.0  # height of the tube above the ground it's set up on
    gravity_scale: float = 1.0  # multiplies GRAVITY_MPS2 for this weapon's shell
    angle_offset_deg: float = 0.0  # mount offset baked into some vehicle weapons; unused by ballistics.py so far
    elevation_precision: int = 1  # decimal places the in-game UI shows for elevation
    moa_arcmin: float | None = None  # shell spread, minutes of angle; unused by ballistics.py so far
    deceleration_mps2: float = 0.0  # unused by ballistics.py so far -- see module docstring
    deceleration_time_s: float = 0.0  # unused by ballistics.py so far
    projectile_lifespan_s: float | None = None  # shell self-destructs after this long in flight; None = no limit
    explosion_damage: float | None = None
    explosion_radius_m: tuple[float, float] | None = None  # (min, max)
    explosion_distance_from_impact_m: float | None = None
    damage_falloff: float | None = None


WEAPONS: dict[str, Weapon] = {

    # --- vanilla infantry / emplacements ---

    "mortar": Weapon(
        name="Mortar (infantry, all factions)",
        velocity_mps=110.0, min_distance_m=51.0, min_elevation_deg=(45.0, 88.875),
        angle_type="high", unit="mil", category="deployable",
        height_offset_m=1.0, elevation_precision=0, moa_arcmin=50,
        explosion_damage=350, explosion_radius_m=(0, 40),
        explosion_distance_from_impact_m=1, damage_falloff=7,
    ),
    "ub32": Weapon(
        name="UB-32 rocket rack",
        velocity_mps=300.0, min_distance_m=0.0, min_elevation_deg=(-25.0, 35.0),
        angle_type="low", unit="deg", category="deployable",
        height_offset_m=1.0, gravity_scale=2.0, elevation_precision=1,
        moa_arcmin=300, deceleration_mps2=50, deceleration_time_s=2,
        projectile_lifespan_s=20,
        explosion_damage=115, explosion_radius_m=(5, 18),
        explosion_distance_from_impact_m=0.2, damage_falloff=1,
    ),
    "hellcannon": Weapon(
        name="Hell Cannon",
        velocity_mps=95.0, min_distance_m=0.0, min_elevation_deg=(10.0, 90.0),
        angle_type="high", unit="deg", category="deployable",
        height_offset_m=1.5, elevation_precision=1, moa_arcmin=100,
        explosion_damage=125, explosion_radius_m=(1, 50),
        explosion_distance_from_impact_m=2, damage_falloff=1,
    ),

    # --- vanilla vehicle-mounted ---

    "tech_mortar": Weapon(
        name="Technical-mounted Mortar",
        velocity_mps=110.0, min_distance_m=51.0, min_elevation_deg=(-45.0, 135.0),
        angle_type="high", unit="deg", category="vehicle",
        height_offset_m=2.5, angle_offset_deg=5.0, elevation_precision=1,
        moa_arcmin=50, explosion_damage=350, explosion_radius_m=(0, 40),
        explosion_distance_from_impact_m=0.5, damage_falloff=7,
    ),
    "tech_ub32": Weapon(
        name="Technical-mounted UB-32",
        velocity_mps=300.0, min_distance_m=0.0, min_elevation_deg=(-45.0, 135.0),
        angle_type="low", unit="deg", category="vehicle",
        height_offset_m=2.5, gravity_scale=2.0, elevation_precision=1,
        moa_arcmin=300, deceleration_mps2=50, deceleration_time_s=2,
        projectile_lifespan_s=20,
        explosion_damage=115, explosion_radius_m=(5, 18),
        explosion_distance_from_impact_m=0.2, damage_falloff=1,
    ),
    "bm21_grad": Weapon(
        name="BM-21 Grad",
        velocity_mps=200.0, min_distance_m=0.0, min_elevation_deg=(-45.0, 135.0),
        angle_type="low", unit="deg", category="vehicle",
        height_offset_m=3.0, gravity_scale=2.0, elevation_precision=1,
        moa_arcmin=200, explosion_damage=140, explosion_radius_m=(1, 35),
        explosion_distance_from_impact_m=2, damage_falloff=1,
    ),
    "m1064_120mm_impact": Weapon(
        name="120mm Mortar (M1064 carrier) - impact fuse",
        velocity_mps=142.0, min_distance_m=340.0, min_elevation_deg=(-45.0, 85.3),
        angle_type="high", unit="deg", category="vehicle",
        height_offset_m=3.0, elevation_precision=1, moa_arcmin=40,
        explosion_damage=400, explosion_radius_m=(0, 40),
        explosion_distance_from_impact_m=1, damage_falloff=7,
    ),
    "m1064_120mm_nearsurface": Weapon(
        name="120mm Mortar (M1064 carrier) - near-surface fuse",
        velocity_mps=142.0, min_distance_m=340.0, min_elevation_deg=(-45.0, 85.3),
        angle_type="high", unit="deg", category="vehicle",
        height_offset_m=3.0, elevation_precision=1, moa_arcmin=50,
        explosion_damage=100, explosion_radius_m=(10, 60),
        explosion_distance_from_impact_m=10, damage_falloff=1.3,
    ),
    "mk19": Weapon(
        name="Mk19 automatic grenade launcher",
        velocity_mps=230.0, min_distance_m=10.0, min_elevation_deg=(-45.0, 85.3),
        angle_type="low", unit="deg", category="vehicle",
        height_offset_m=4.0, angle_offset_deg=0.984, elevation_precision=1,
        moa_arcmin=50, projectile_lifespan_s=20,
        explosion_damage=115, explosion_radius_m=(1, 15),
        explosion_distance_from_impact_m=0.08, damage_falloff=1,
    ),
    "btr4_ags": Weapon(
        name="BTR-4 AGS-30",
        velocity_mps=190.0, min_distance_m=0.0, min_elevation_deg=(-45.0, 135.0),
        angle_type="low", unit="degMin", category="vehicle",
        height_offset_m=3.4, angle_offset_deg=0.73459689, elevation_precision=1,
        moa_arcmin=15, projectile_lifespan_s=20,
        explosion_damage=115, explosion_radius_m=(1, 15),
        explosion_distance_from_impact_m=1, damage_falloff=1,
    ),

    # --- modded: SuperMod (https://steamcommunity.com/sharedfiles/filedetails/?id=3293347373) ---

    "mo120rtf1_short": Weapon(
        name="MO-120-RT-F1 - short charge",
        velocity_mps=110.0, min_distance_m=0.0, min_elevation_deg=(45.0, 85.3),
        angle_type="high", unit="mil", category="modded", mod="SuperMod",
        height_offset_m=3.0, elevation_precision=0, moa_arcmin=30,
        explosion_damage=500, explosion_radius_m=(2, 60),
        explosion_distance_from_impact_m=1, damage_falloff=7,
    ),
    "mo120rtf1_medium": Weapon(
        name="MO-120-RT-F1 - medium charge",
        velocity_mps=143.5, min_distance_m=0.0, min_elevation_deg=(45.0, 85.3),
        angle_type="high", unit="mil", category="modded", mod="SuperMod",
        height_offset_m=3.0, elevation_precision=0, moa_arcmin=30,
        explosion_damage=500, explosion_radius_m=(2, 60),
        explosion_distance_from_impact_m=1, damage_falloff=7,
    ),
    "mo120rtf1_long": Weapon(
        name="MO-120-RT-F1 - long charge",
        velocity_mps=171.5, min_distance_m=0.0, min_elevation_deg=(45.0, 85.3),
        angle_type="high", unit="mil", category="modded", mod="SuperMod",
        height_offset_m=3.0, elevation_precision=0, moa_arcmin=30,
        explosion_damage=500, explosion_radius_m=(2, 60),
        explosion_distance_from_impact_m=1, damage_falloff=7,
    ),
    "type_63": Weapon(
        name="Type 63 multiple rocket launcher",
        velocity_mps=300.0, min_distance_m=0.5, min_elevation_deg=(-20.0, 55.0),
        angle_type="low", unit="deg", category="modded", mod="SuperMod",
        height_offset_m=3.0, gravity_scale=2.0, elevation_precision=1,
        moa_arcmin=300, explosion_damage=250, explosion_radius_m=(2, 10),
        explosion_distance_from_impact_m=2, damage_falloff=1,
    ),

    # --- modded: Infinite Warfare (https://steamcommunity.com/sharedfiles/filedetails/?id=3405835668) ---

    "pzl07_he": Weapon(
        name="PZL-07 - high-explosive",
        velocity_mps=140.0, min_distance_m=0.0, min_elevation_deg=(-90.0, 90.0),
        angle_type="low", unit="deg", category="modded", mod="InfiniteWarefare",
        height_offset_m=2.0, elevation_precision=1, moa_arcmin=40,
        explosion_damage=375, explosion_radius_m=(1.5, 10),
        explosion_distance_from_impact_m=0.5, damage_falloff=3.5,
    ),
    "pzl07_airburst": Weapon(
        name="PZL-07 - air-burst",
        velocity_mps=140.0, min_distance_m=0.0, min_elevation_deg=(-90.0, 90.0),
        angle_type="low", unit="deg", category="modded", mod="InfiniteWarefare",
        height_offset_m=2.0, elevation_precision=1, moa_arcmin=40,
        explosion_damage=100, explosion_radius_m=(10, 60),
        explosion_distance_from_impact_m=10, damage_falloff=1.3,
    ),

    # --- modded: Steel Division (https://steamcommunity.com/sharedfiles/filedetails/?l=french&id=2432926361) ---

    "m109": Weapon(
        name="M109 self-propelled howitzer",
        velocity_mps=225.0, min_distance_m=0.0, min_elevation_deg=(-45.0, 135.0),
        angle_type="low", unit="deg", category="modded", mod="SteelDivision",
        height_offset_m=2.206, gravity_scale=2.0, angle_offset_deg=-0.01,
        elevation_precision=1, moa_arcmin=1.5,
        explosion_damage=2000, explosion_radius_m=(40, 75),
        explosion_distance_from_impact_m=1, damage_falloff=3.5,
    ),
    "m777": Weapon(
        name="M777 howitzer",
        velocity_mps=200.0, min_distance_m=700.0, min_elevation_deg=(15.0, 80.0),
        angle_type="low", unit="deg", category="modded", mod="SteelDivision",
        height_offset_m=4.0, gravity_scale=2.0, elevation_precision=1,
        moa_arcmin=1.5, explosion_damage=2000, explosion_radius_m=(40, 75),
        explosion_distance_from_impact_m=1, damage_falloff=3.5,
    ),
    "t62_dumptruck": Weapon(
        name="T62 dump truck bomb",
        velocity_mps=210.0, min_distance_m=0.0, min_elevation_deg=(-45.0, 135.0),
        angle_type="low", unit="deg", category="modded", mod="SteelDivision",
        height_offset_m=3.0, gravity_scale=2.0, elevation_precision=1,
        moa_arcmin=100, explosion_damage=400, explosion_radius_m=(20, 40),
        explosion_distance_from_impact_m=1, damage_falloff=1,
    ),
    "himars": Weapon(
        name="HIMARS",
        velocity_mps=250.0, min_distance_m=0.0, min_elevation_deg=(-3.0, 84.7),
        angle_type="low", unit="deg", category="modded", mod="SteelDivision",
        height_offset_m=3.0, gravity_scale=2.0, elevation_precision=1,
        moa_arcmin=15, explosion_damage=300, explosion_radius_m=(1.5, 50),
        explosion_distance_from_impact_m=3, damage_falloff=1,
    ),
    "tos1a": Weapon(
        name="TOS-1A thermobaric MLRS",
        velocity_mps=100.0, min_distance_m=0.0, min_elevation_deg=(0.0, 80.0),
        angle_type="low", unit="deg", category="modded", mod="SteelDivision",
        height_offset_m=3.0, elevation_precision=1, moa_arcmin=200,
        explosion_damage=150, explosion_radius_m=(15, 25),
        explosion_distance_from_impact_m=0.2, damage_falloff=1,
    ),
    "ural_hellcannon": Weapon(
        name="Ural-mounted Hell Cannon",
        velocity_mps=180.0, min_distance_m=0.0, min_elevation_deg=(10.0, 85.0),
        angle_type="high", unit="deg", category="modded", mod="SteelDivision",
        height_offset_m=3.0, gravity_scale=2.0, elevation_precision=1,
        moa_arcmin=300, explosion_damage=300, explosion_radius_m=(1, 75),
        explosion_distance_from_impact_m=2, damage_falloff=1,
    ),

    # --- modded: Squad AdminTools (https://steamcommunity.com/sharedfiles/filedetails/?id=3193475024) ---

    "mtlb_fab500": Weapon(
        name="MTLB FAB-500 bomb",
        velocity_mps=95.0, min_distance_m=75.0, min_elevation_deg=(-45.0, 85.3),
        angle_type="low", unit="deg", category="modded", mod="SquadAdminTools",
        height_offset_m=3.0, elevation_precision=1, moa_arcmin=150,
        explosion_damage=4500, explosion_radius_m=(0.1, 50),
        explosion_distance_from_impact_m=2, damage_falloff=4,
    ),
}
