import argparse
import csv
import os
from math import exp
from statistics import mean

import matplotlib.pyplot as plt
from scipy import stats

# from scipy.optimize import curve_fit


def get_csv_files():
    directory = os.getcwd()
    files = os.listdir(directory)
    csv_files = [file for file in files if file.endswith(".csv")]
    return csv_files


def get_data(csv_file):
    data = []
    with open(csv_file, mode="r") as file:
        csv_reader_dict = csv.DictReader(file, delimiter=";")
        for row in csv_reader_dict:
            data.append(row)
    return data


def calculate_accel(data, loop_hertz):
    erpm = [int(row["erpm"]) for row in data]
    current_motor = [float(row["current_motor"]) for row in data]
    ms_today = [int(row["ms_today"]) for row in data]

    accel_measured = []
    current_measured = []
    # ratio_list = []
    for i in range(len(data) - 1):
        # discard any stationary data points
        if erpm[i] == 0 or erpm[i + 1] == 0:
            continue

        time_diff = ms_today[i + 1] - ms_today[i]
        erpm_diff = erpm[i + 1] - erpm[i]
        # normalize to erpm change per loop duration
        erpm_diff *= 1000 / loop_hertz / time_diff
        current_avg = (current_motor[i + 1] + current_motor[i]) / 2

        accel_measured.append(erpm_diff)
        current_measured.append(current_avg)
        # ratio_list.append((current_avg - 8) * time_diff / erpm_diff)

    return accel_measured, current_measured


def plot(x, y, ratio_predicted, offset_predicted, num_points):

    alpha = exp(-0.0001 * num_points)
    plt.scatter(x, y, s=20, linewidths=0, color="IndianRed", alpha=alpha)
    plt.axline(
        xy1=(0, offset_predicted),
        slope=ratio_predicted,
        # color="purple",
        label=f"Accel. Ratio = {ratio_predicted:.2f}\nTorque Offset = {offset_predicted:.2f} A",
    )

    plt.xlabel("Acceleration [ERPM/loop]")
    plt.ylabel("Motor Current [A]")

    plt.xlim([-8, 8])
    plt.ylim([-30, 50])

    plt.legend()
    plt.show()


def process_csv_file(csv_file, args):

    data = get_data(csv_file)

    accel_measured, current_measured = calculate_accel(data, args.loop_hertz)

    x = accel_measured
    y = current_measured
    num_points = len(x)

    # fit linear function to data
    slope, intercept, r_value, p_value, std_err = stats.linregress(y, x)

    # inverse the linear function
    ratio_predicted = 1 / slope
    offset_predicted = -intercept / slope

    print("")
    print(f"{csv_file}")
    print(f"Evaluated {num_points:,} data points")
    print("")
    print("RECOMMENDED VALUES:")
    print(f"Accel. Ratio:  {ratio_predicted:.1f}")
    print(f"Torque Offset: {offset_predicted:.1f} A")
    print("")
    print(f"R Value: {r_value:.2f} (more = better)")
    # print(f"Std Err: {std_err:.4f}")
    print("")

    if args.plot:
        plot(x, y, ratio_predicted, offset_predicted, num_points)


def main(args):

    csv_files = get_csv_files()

    for csv_file in csv_files:
        process_csv_file(csv_file, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-hz",
        "--loop_hertz",
        default=800,
        type=int,
        help="Frequency of the balance loop, should match Float Cfg > Specs > Loop Hertz. For example, ADV uses 800 Hz.",
    )
    parser.add_argument(
        "-p",
        "--plot",
        action="store_true",
        help="Plot the logged data along with the predicted line.",
    )

    args = parser.parse_args()
    main(args)
