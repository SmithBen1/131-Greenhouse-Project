"""Launcher for the Milestone 2 sandbox GUI.

Adds this directory to sys.path so `martian_greenhouse_sim.gui` resolves,
then calls its main(). Run this command from the folder that contains this
file:

    python run_sandbox.py

Optional arguments:

    python run_sandbox.py 7                                # a different seed
    python run_sandbox.py --glazing aerogel --heater 3000  # try other hardware
    python run_sandbox.py --mission m4                     # Milestone 4 sensor faults

Without --glazing/--heater, the sandbox uses your team's declaration in
student_controller/hardware.py when that file sits next to this one, and the
as-built hardware (twin_wall, 2000 W) otherwise.
"""

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from martian_greenhouse_sim.gui import main  # noqa: E402
from martian_greenhouse_sim.hardware import (  # noqa: E402
    GLAZING_OPTIONS,
    HEATER_OPTIONS_KG,
    Hardware,
)
from martian_greenhouse_sim.simulation import load_student_hardware  # noqa: E402


def resolve_hardware(glazing, heater_w, search_dirs):
    """Resolve the hardware to launch the sandbox with.

    When both glazing and heater_w are given on the command line, the
    team's declaration in student_controller/hardware.py is never loaded,
    so a broken, half filled, or off menu declaration cannot block a
    launch that does not need it. When either argument is missing, the
    declaration fills the missing value, and the as-built Hardware()
    (twin_wall, 2000 W) applies when nothing is declared.
    """
    if glazing is not None and heater_w is not None:
        return Hardware(glazing=glazing, heater_w=heater_w)

    declared = load_student_hardware(search_dirs=search_dirs) or Hardware()
    return Hardware(
        glazing=glazing or declared.glazing,
        heater_w=heater_w or declared.heater_w,
    )


def build_parser():
    """Build the command line parser for the sandbox launcher."""
    parser = argparse.ArgumentParser(description="Martian greenhouse sandbox")
    parser.add_argument("seed", nargs="?", type=int, default=42)
    parser.add_argument("--glazing", choices=list(GLAZING_OPTIONS))
    parser.add_argument("--heater", type=int, choices=list(HEATER_OPTIONS_KG))
    parser.add_argument(
        "--mission",
        choices=["m3", "m4"],
        default="m3",
        help="m4 applies the Milestone 4 sensor faults (default: m3)",
    )
    return parser

def running_total(amount, state):
    # state is a plain dict handed in from outside, so it survives between calls
    state["total"] = state.get("total", 0.0) + amount
    return state["total"]

state = {}                       # created once, outside the function
print(running_total(1, state))   # 1.0
print(running_total(1, state))   # 2.0  <- state kept the total from the first call

if __name__ == "__main__":
    args = build_parser().parse_args()

    hardware = resolve_hardware(args.glazing, args.heater, [str(_HERE)])
    main(seed=args.seed, hardware=hardware, mission=args.mission)
