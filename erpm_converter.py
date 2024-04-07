import argparse
import math

erpm = 1000
speed = 3.5
use_miles = False

diameter = 283
motor_poles = 30


def erpm_to_speed():
    speed = float(erpm) * (math.pi * diameter / 1000) / (motor_poles * 60 / 2) * 3.6
    if use_miles:
        speed /= 1.60934
    return speed


def speed_to_erpm():
    erpm = float(speed) / (math.pi * diameter / 1000) * (motor_poles * 60 / 2) / 3.6
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
