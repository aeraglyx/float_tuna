import argparse
import math

erpm = 10000
speed = 5.0
use_miles = False

diameter = 290
motor_poles = 30

radius_m = 0.5 * diameter * 0.001
pole_pairs = motor_poles / 2
mps_to_erpm_ratio = (math.tau * radius_m) / (pole_pairs * 60)


def erpm_to_speed():
    speed = float(erpm) * mps_to_erpm_ratio * 3.6
    if use_miles:
        speed /= 1.60934
    return speed


def speed_to_erpm():
    erpm = float(speed) / mps_to_erpm_ratio / 3.6
    if use_miles:
        erpm *= 1.60934
    return erpm


def main():
    unit_str = "mi/h" if use_miles else "km/h"

    print("")
    print(f"{erpm} ERPM = {erpm_to_speed():.2f} {unit_str}")
    print(f"{speed:.2f} {unit_str} = {speed_to_erpm():,.0f} ERPM")
    print("")


if __name__ == "__main__":
    main()
