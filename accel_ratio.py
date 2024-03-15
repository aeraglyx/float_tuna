import argparse
import os
from math import exp
from statistics import mean, stdev

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import utils

# from sklearn.linear_model import LinearRegression
# from scipy.optimize import curve_fit


def plot_points(x, y, z, num_points):

    alpha = exp(-0.0001 * num_points)
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

    # for csv_file in csv_files:
    #     data = utils.get_data(csv_file)
    #     process_data(data, args)

    csv_file = csv_files[0]
    df = pd.read_csv(csv_file, sep=";")
    df = df.dropna(axis=1, how="all")
    # print(df["ms_today"].diff().describe())
    # print(df)

    df = df[["ms_today", "current_motor", "erpm", "duty_cycle"]].copy()

    # get independent erpm
    erpm_abs = df["erpm"].abs()
    df["erpm_abs"] = erpm_abs

    # get independent duty
    duty_cycle_abs = df["duty_cycle"].abs()
    df["duty_cycle_abs"] = duty_cycle_abs

    # get erpm change
    ms_today = df["ms_today"]
    erpm_grad_np = np.gradient(df["erpm_abs"], ms_today)
    erpm_grad_np *= 1000 / args.loop_hertz  # normalize to erpm per loop
    erpm_grad = pd.Series(erpm_grad_np)
    df["erpm_grad"] = erpm_grad

    corr = utils.get_strong_corr(df, "erpm_grad", 8)
    # print(corr)

    # filter data
    df = df[df["erpm_abs"] > 500]
    # df = df[df["duty_cycle_abs"] > 0.01]
    df = df.reset_index(drop=True)
    # print(df)

    # assign vars to axis
    # X = df[["current_motor", "erpm_abs"]]
    x = df["current_motor"]
    y = df["erpm_grad"]

    # model = LinearRegression()
    # model.fit(X, y)
    # y_pred = model.predict(X)

    # fit linear function to data
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    offset_display, ratio_display = utils.inverse_lin_func(intercept, slope)

    num_points = len(x)
    spacing = 20

    print("")
    print(f"{'Log File:':<{spacing}}{os.path.splitext(csv_file)[0]}")
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
    plot_points(x, y, df["erpm_abs"], num_points)
    # if args.ref_ratio:
    #     ratio_ref, offset_ref = utils.inverse_lin_func(8, args.ref_ratio)
    #     plot_line(ratio_ref, offset_ref, (0.4, 0.7, 0.9), "Reference")
    plot_line(slope, intercept, "purple", "Predicted")
    plt.xlabel("Motor Current [A]")
    plt.ylabel("Acceleration [ERPM/loop]")

    plt.legend(loc="lower right")
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
