import argparse
import math
import os
from statistics import mean, stdev

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression

import utils

# from scipy.optimize import curve_fit


def main(args):

    csv_files = utils.get_csv_files()

    df = utils.get_data_from_all_files(csv_files, 800)
    print(f"All data points: {len(df)}")
    # df = df.sample(40000)

    # df = utils.get_data_from_file("logs/log_03.csv")

    # corr = utils.get_strong_corr(df, "erpm_grad", 8)

    # filter data
    df = df[df["erpm"].abs() > 250]
    df = df.reset_index()
    # df = df[df["duty_cycle_abs"] > 0.01]

    # assign vars to axis
    X = df[["current_motor", "erpm"]]
    # X = df[["current_motor"]]
    x = df["current_motor"]
    y = df["erpm_grad"]

    model = LinearRegression(
        fit_intercept=False,
    )
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
        f"(current_motor + ({model.intercept_ / model.coef_[0]:.2f} + {model.coef_[1] / model.coef_[0]:.5f} * erpm)) / {1 / model.coef_[0]:.2f}"
    )
    print(
        f"{model.intercept_:.2f} + {model.coef_[0]:.3f} * current_motor + {model.coef_[1]:.6f} * erpm"
    )

    # fit linear function to data
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    offset_display, ratio_display = utils.inverse_lin_func(intercept, slope)

    num_points = len(x)

    # if args.plot:
    plt.figure(figsize=(8, 6), dpi=100)
    # utils.plot_points(x, y, color="blue")
    utils.plot_points(df["erpm"], x, color="black", a=0.8)

    plt.xlabel("Speed [ERPM]")
    plt.ylabel("Motor Current [A]")
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
