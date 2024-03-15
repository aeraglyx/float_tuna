import argparse
import math
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

    alpha = exp(-0.015 * math.sqrt(num_points))
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


def get_data(csv_files) -> pd.DataFrame:
    dfs = []
    for csv_file in csv_files:

        df = pd.read_csv(csv_file, sep=";")
        # df = df.dropna(axis=1, how="any")
        df = df[["ms_today", "current_motor", "erpm", "duty_cycle"]].copy()

        # get independent erpm
        erpm_abs = df["erpm"].abs()
        df["erpm_abs"] = erpm_abs

        # get independent duty
        duty_cycle_abs = df["duty_cycle"].abs()
        df["duty_cycle_abs"] = duty_cycle_abs

        # get erpm change
        erpm_grad = np.gradient(df["erpm_abs"], df["ms_today"])
        erpm_grad *= 1000 / args.loop_hertz  # normalize to erpm per loop
        df["erpm_grad"] = pd.Series(erpm_grad)
        # csv_file = csv_files[1]
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    return df


def main(args):

    csv_files = utils.get_csv_files()
    df = get_data(csv_files)
    df = df.sample(20000)

    # print(df)
    # print(csv_file)

    # df = df.loc[:, (df != 0).any(axis=0)]
    # df[
    #     [
    #         "ms_today",
    #         "input_voltage",
    #         "temp_mos_max",
    #         # "temp_mos_1",
    #         # "temp_mos_2",
    #         # "temp_mos_3",
    #         "temp_motor",
    #         "current_motor",
    #         "current_in",
    #         "d_axis_current",
    #         "q_axis_current",
    #         "erpm",
    #         "duty_cycle",
    #         "amp_hours_used",
    #         "amp_hours_charged",
    #         "watt_hours_used",
    #         "watt_hours_charged",
    #         "tachometer",
    #         "tachometer_abs",
    #         "encoder_position",
    #         # "fault_code",
    #         # "vesc_id",
    #         "d_axis_voltage",
    #         "q_axis_voltage",
    #         "ms_today_setup",
    #         "amp_hours_setup",
    #         "amp_hours_charged_setup",
    #         "watt_hours_setup",
    #         "watt_hours_charged_setup",
    #         "battery_level",
    #         "battery_wh_tot",
    #         "current_in_setup",
    #         "current_motor_setup",
    #         "speed_meters_per_sec",
    #         "tacho_meters",
    #         "tacho_abs_meters",
    #         # "num_vescs",
    #         "ms_today_imu",
    #         "roll",
    #         "pitch",
    #         "yaw",
    #         "accX",
    #         "accY",
    #         "accZ",
    #         "gyroX",
    #         "gyroY",
    #         "gyroZ",
    #         "gnss_posTime",
    #         "gnss_lat",
    #         "gnss_lon",
    #         "gnss_alt",
    #         "gnss_gVel",
    #         # "gnss_vVel",
    #         "gnss_hAcc",
    #         "gnss_vAcc",
    #     ]
    # ]

    # corr = utils.get_strong_corr(df, "erpm_grad", 8)
    # print(corr)

    # filter data
    df = df[df["erpm"] > 250]
    df = df.reset_index()
    # df = df[df["duty_cycle_abs"] > 0.01]

    # print(df["gnss_gVel"].nlargest(n=30))

    # assign vars to axis
    X = df[["current_motor", "erpm_abs"]]
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
        f"(current_motor + ({model.intercept_ / model.coef_[0]:.2f} + {model.coef_[1] / model.coef_[0]:.5f} * erpm_abs)) / {1 / model.coef_[0]:.2f}"
    )
    print(
        f"{model.intercept_:.2f} + {model.coef_[0]:.3f} * current_motor + {model.coef_[1]:.6f} * erpm_abs"
    )

    # fit linear function to data
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    offset_display, ratio_display = utils.inverse_lin_func(intercept, slope)

    num_points = len(x)

    # if args.plot:
    plt.figure(figsize=(8, 8), dpi=100)
    # plot_points(x, y, "blue", num_points)
    plot_points(df["erpm"], x, "black", num_points)
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
