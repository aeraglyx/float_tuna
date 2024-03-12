import os

import pandas as pd


def get_csv_files():
    directory = os.getcwd()
    files = os.listdir(directory)
    csv_files = [file for file in files if file.endswith(".csv")]
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
    return corr
