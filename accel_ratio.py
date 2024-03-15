import argparse
import math
import os
from statistics import mean, stdev

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import utils

# from sklearn.linear_model import LinearRegression
# from scipy.optimize import curve_fit


def plot_points(x, y, z, num_points):

    alpha = math.exp(-0.012 * math.sqrt(num_points))
    plt.scatter(
        x,
        y,
        c=z,
        cmap="magma",
        alpha=alpha,
        s=20,
        linewidths=0,
    )

    mean_x = mean(x)
    mean_y = mean(y)
    stdev_x = 4 * stdev(x)
    stdev_y = 4 * stdev(y)

    plt.xlim([mean_x - stdev_x, mean_x + stdev_x])
    plt.ylim([mean_y - stdev_y, mean_y + stdev_y])


def plot_line(slope, intercept, color, label):

    plt.axline(
        xy1=(0, intercept),
        slope=slope,
        color=color,
        linewidth=2.0,
        label=label,
    )


def main(args):

    csv_files = utils.get_csv_files()

    df = utils.get_data_from_all_files(csv_files)

    # corr = utils.get_strong_corr(df, "erpm_grad", 8)

    # filter data
    df = df[df["erpm_abs"] > 500]
    df = df.reset_index(drop=True)

    # assign vars to axis
    x = df["current_motor"]
    y = df["erpm_grad"]

    # fit linear function to data
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    offset_display, ratio_display = utils.inverse_lin_func(intercept, slope)

    num_points = len(x)
    spacing = 20

    print("")
    print(f"{'Evaluated points:':<{spacing}}{num_points:,}")
    print("")
    # print("RECOMMENDED VALUES:")
    print(f"{'Accel. Ratio:':<{spacing}}{ratio_display:.1f}")
    print(f"{'Torque Offset:':<{spacing}}{offset_display:.1f} A")
    print("")
    print(f"{'Correlation:':<{spacing}}{r_value:.2f}")
    print("")

    # if args.plot:
    plt.figure(figsize=(8, 6), dpi=100)
    plot_points(x, y, df["erpm"], num_points)
    # if args.ref_ratio:
    #     ratio_ref, offset_ref = utils.inverse_lin_func(8, args.ref_ratio)
    #     plot_line(ratio_ref, offset_ref, (0.4, 0.7, 0.9), "Reference")
    # plot_line(slope, intercept, "purple", "Predicted")
    plt.xlabel("Motor Current [A]")
    plt.ylabel("Acceleration [ERPM/loop]")

    # plt.legend(loc="lower right")
    cbar = plt.colorbar()
    cbar.solids.set(alpha=1)
    cbar.ax.set_ylabel("Speed [ERPM]")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-hz",
        "--loop_hertz",
        default=800,
        metavar="LOOP_HERTZ",
        type=int,
        help="Frequency of the balance loop, should match Float Cfg > Specs > Loop Hertz. For example, ADV uses 800 Hz.",
    )
    parser.add_argument(
        "-p",
        "--plot",
        action="store_true",
        help="Plot the logged data along with the predicted line using matplotlib.",
    )
    # parser.add_argument(
    #     "-r",
    #     "--ref_ratio",
    #     # "--hertz",
    #     default=9.0,
    #     # metavar=("ACCEL", "DECEL"),
    #     metavar=("ACCEL"),
    #     type=float,
    #     nargs=1,
    #     help="Your current Accel. Ratio for comparison.",
    # )

    args = parser.parse_args()
    main(args)
