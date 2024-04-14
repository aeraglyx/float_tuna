import math
import os

# from scipy import stats
from statistics import mean, stdev

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_csv_files():
    # directory = os.getcwd()
    directory = "logs"
    files = os.listdir(directory)
    csv_files = ["logs/" + file for file in files if file.endswith(".csv")]
    return csv_files


def inverse_lin_func(intercept, slope):
    slope_new = 1 / slope
    intercept_new = -intercept / slope
    return intercept_new, slope_new


def get_strong_corr(df: pd.DataFrame, column: str, n: int = 5):
    corr = df.corr()[column]
    corr = corr.dropna()
    corr = corr.sort_values(key=abs, ascending=False)
    corr = corr.iloc[1:]  # ignore correlation with itself
    corr = corr.nlargest(n)
    print(corr)
    return corr


def get_data_from_file(csv_file, loop_hertz: int) -> pd.DataFrame:

    df = pd.read_csv(csv_file, sep=";")
    # df = df.dropna(axis=1, how="any")
    # df = df[["ms_today", "current_motor", "erpm", "duty_cycle"]].copy()
    # df["erpm"] = df["erpm"].abs()

    # get independent erpm
    # erpm_abs = df["erpm"].abs()
    # df["erpm_abs"] = erpm_abs

    # df["current_motor"] = np.where(
    #     df["erpm"] < 0, -df["current_motor"], df["current_motor"]
    # )

    # get independent duty
    # duty_cycle_abs = df["duty_cycle"].abs()
    # df["duty_cycle_abs"] = duty_cycle_abs

    # get erpm gradient
    erpm_grad = np.gradient(df["erpm"], df["ms_today"])
    # loop_hertz = 800
    erpm_grad *= 1000 / loop_hertz  # normalize to erpm per loop
    df["erpm_grad"] = pd.Series(erpm_grad)

    return df


def get_data_from_all_files(csv_files, loop_hertz: int) -> pd.DataFrame:
    dfs = []
    for csv_file in csv_files:
        df = get_data_from_file(csv_file, loop_hertz)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    return df


def filter_data(df):
    # df = df[df["erpm"].abs() > 200]
    df = df[df["erpm"] > 200]
    df = df[df["erpm"].abs() < 10000]
    df = df[df["erpm_grad"].abs() < 5]
    return df.reset_index()


def plot_points(
    x,
    y,
    ax=plt,
    z=None,
    s=10,
    a=1.0,
    color=None,
    cmap="magma",
    vmin=None,
    vmax=None,
):
    alpha = math.exp(-0.01 * math.sqrt(len(x)) / a)
    im = ax.scatter(
        x,
        y,
        s=s,
        c=z,
        cmap=(None if z is None else cmap),
        color=color,
        alpha=alpha,
        linewidths=0,
        vmin=vmin,
        vmax=vmax,
    )

    mean_x = mean(x)
    mean_y = mean(y)
    stdev_x = 4 * stdev(x)
    stdev_y = 4 * stdev(y)

    ax.set_xlim([mean_x - stdev_x, mean_x + stdev_x])
    ax.set_ylim([mean_y - stdev_y, mean_y + stdev_y])

    return im


def plot_line(slope, intercept, ax=plt, color=None, label=None):

    ax.axline(
        xy1=(0, intercept),
        slope=slope,
        color=color,
        linewidth=2.0,
        label=label,
    )
