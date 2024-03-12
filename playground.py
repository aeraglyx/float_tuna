import argparse
import os
from math import exp
from statistics import mean, stdev

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression

import utils

# from scipy.optimize import curve_fit


def plot_points(x, y, color, num_points):

    alpha = exp(-0.00015 * num_points)
    plt.scatter(
        x,
        y,
        # c=z,
        # cmap="magma",
        color=color,
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
    # print(df)

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

    # get strongly correlating values
    corr = df.corr()["erpm_grad"]
    corr = corr.dropna()
    corr = corr.sort_values(key=abs, ascending=False)
    corr = corr.iloc[1:]  # ignore correlation with itself
    corr = corr.nlargest(8)
    # print(corr)

    # filter data
    df = df[df["erpm_abs"] > 500]
    df = df.reset_index()
    # df = df[df["duty_cycle_abs"] > 0.01]

    # print(df["gnss_gVel"].nlargest(n=30))

    # assign vars to axis
    X = df[["current_motor", "erpm_abs"]]
    x = df["current_motor"]
    y = df["erpm_grad"]

    model = LinearRegression()
    model.fit(X, y)
    y_pred = pd.Series(model.predict(X))
    multivar_intercept, multivar_slope = utils.inverse_lin_func(
        model.intercept_, model.coef_[0]
    )
    print(f"y vs y_pred corr: {y_pred.corr(y)}")
    print(model.intercept_)
    print(model.coef_)
    print(multivar_slope)
    print(multivar_intercept)
    print(
        f"(current_motor - ({abs(model.intercept_ / model.coef_[0]):.2f} + {abs(model.coef_[1] / model.coef_[0]):.4f} * erpm_abs)) / {1 / model.coef_[0]:.2f}"
    )
    print(
        f"{model.intercept_:.2f} + {model.coef_[0]:.3f} * current_motor + {model.coef_[1]:.5f} * erpm_abs"
    )

    # fit linear function to data
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    offset_display, ratio_display = utils.inverse_lin_func(intercept, slope)

    num_points = len(x)

    # if args.plot:
    plt.figure(figsize=(8, 8), dpi=100)
    plot_points(x, y, "blue", num_points)
    plot_points(x, y_pred, "red", num_points)
    # plt.show()


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
    parser.add_argument(
        "-r",
        "--ref_ratio",
        # "--hertz",
        default=9.0,
        # metavar=("ACCEL", "DECEL"),
        metavar=("ACCEL"),
        type=float,
        nargs=1,
        help="Your current Accel. Ratio for comparison.",
    )

    args = parser.parse_args()
    main(args)
