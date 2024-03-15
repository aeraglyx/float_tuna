import argparse
import math

erpm = 500
speed = 5

diameter = 283
motor_poles = 30


def erpm_to_kmh():
    speed = float(erpm) * (math.pi * diameter / 1000) / (motor_poles * 60 / 2) * 3.6
    return speed


def kmh_to_erpm():
    erpm = float(speed) / (math.pi * diameter / 1000) * (motor_poles * 60 / 2) / 3.6
    return erpm


def main():

    print(f"{erpm} ERPM = {erpm_to_kmh():.2f} km/h")
    print(f"{speed} km/h = {kmh_to_erpm():,.0f} ERPM")


if __name__ == "__main__":
    main()
