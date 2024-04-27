import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression, LogisticRegression

import utils


def main(args):

    csv_files = utils.get_csv_files()

    df = utils.get_data_from_all_files(csv_files, 800)
    # df = utils.get_data_from_file("logs/log_08_clean.csv", 800)
    # df = df.sample(50000)
    # df = utils.get_data_from_file("logs/log_03.csv")
    print("")
    print(f"Data points considered: {len(df)}")
    # utils.get_strong_corr(df, "erpm_grad", 8)

    df = utils.filter_data(df)

    # assign vars to axis
    X = df[["q_axis_current", "erpm"]]
    x = df["q_axis_current"]
    y = df["erpm_grad"]

    model_lin = LinearRegression(fit_intercept=False)
    model_lin.fit(X, y)
    y_pred = pd.Series(model_lin.predict(X))

    model_log = LogisticRegression(fit_intercept=False)
    model_log.fit(X, y > 0)

    bias = 0.95
    amp_offset_per_erpm = model_log.coef_[0][1] / model_log.coef_[0][0]

    print("")
    print(f"Lin. Reg. Slope Current:   {1 / model_lin.coef_[0]:.2f}")
    print(f"Lin. Reg. Slope ERPM:     {model_lin.coef_[1]:.5f}")
    print(f"Lin. Reg. Slope Combined: {model_lin.coef_[1] / model_lin.coef_[0]:.5f}")
    print("")
    print(f"Log. Reg. Slope Current:   {1 / model_log.coef_[0][0]:.2f}")
    print(f"Log. Reg. Slope ERPM:     {model_log.coef_[0][1]:.5f}")
    print(
        f"Log. Reg. Slope Combined: {model_log.coef_[0][1] / model_log.coef_[0][0]:.5f}"
    )
    print("")
    print(f"Amp Offset per ERPM: {-amp_offset_per_erpm:.5f}")
    print("")
    print(f"y vs y_pred corr: {y_pred.corr(y):.2f}")
    print("")

    # fit linear function to data
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    offset_display, ratio_display = utils.inverse_lin_func(intercept, slope)

    # if args.plot:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    # fig.suptitle("Horizontally stacked subplots")

    im1 = utils.plot_points(
        x - 0.00025 * 5.66 * df["erpm"],
        # x,
        y,
        z=df["erpm"],
        ax=ax1,
        cmap="magma",
        s=15,
        vmin=0,
        vmax=10000,
    )
    utils.plot_line(
        # model_log.coef_[0][0],
        1 / 8,
        0,
        ax1,
        "purple",
        "Predicted",
    )

    ax1.set_xlabel("Motor Current [A]")
    ax1.set_ylabel("Acceleration [ERPM/loop]")

    cbar = fig.colorbar(im1)
    cbar.solids.set(alpha=1)
    cbar.ax.set_ylabel("Speed [ERPM]")

    norm = 2
    im2 = utils.plot_points(
        df["erpm"],
        x,
        ax=ax2,
        z=df["erpm_grad"],
        s=15,
        a=1.2,
        cmap="coolwarm",
        vmin=-norm,
        vmax=norm,
    )
    utils.plot_line(
        -model_log.coef_[0][1] / model_log.coef_[0][0],
        0,
        ax2,
        "purple",
        f"{model_log.coef_[0][1] / model_log.coef_[0][0]:.5f}",
    )
    ax2.legend(loc="lower right")

    ax2.set_xlabel("Speed [ERPM]")
    ax2.set_ylabel("Motor Current [A]")

    cbar = fig.colorbar(im2)
    cbar.solids.set(alpha=1)
    cbar.ax.set_ylabel("Acceleration [ERPM/loop]")

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
