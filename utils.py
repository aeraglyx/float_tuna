import os

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


def get_data_from_file(csv_file) -> pd.DataFrame:

    df = pd.read_csv(csv_file, sep=";")
    # df = df.dropna(axis=1, how="any")
    df = df[["ms_today", "current_motor", "erpm", "duty_cycle"]].copy()

    # get independent erpm
    erpm_abs = df["erpm"].abs()
    df["erpm_abs"] = erpm_abs

    # df["current_motor"] = np.where(
    #     df["erpm"] < 0, -df["current_motor"], df["current_motor"]
    # )

    # get independent duty
    # duty_cycle_abs = df["duty_cycle"].abs()
    # df["duty_cycle_abs"] = duty_cycle_abs

    # get erpm change
    erpm_grad = np.gradient(df["erpm"], df["ms_today"])
    loop_hertz = 800
    erpm_grad *= 1000 / loop_hertz  # normalize to erpm per loop
    df["erpm_grad"] = pd.Series(erpm_grad)

    return df


def get_data_from_all_files(csv_files) -> pd.DataFrame:
    dfs = []
    for csv_file in csv_files:
        df = get_data_from_file(csv_file)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    return df
