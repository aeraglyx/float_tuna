import csv
import os


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


def prepare_data(data):
    erpm = [int(row["erpm"]) for row in data]
    data_filtered = []
    for i in range(len(data) - 1):
        # discard any stationary data points
        if erpm[i] == 0 or erpm[i + 1] == 0:
            continue
        data_filtered.append([data[i], data[i + 1]])

    return data_filtered


def get_valid_indices(data):
    erpm = [int(row["erpm"]) for row in data]
    valid_indices = []
    for i in range(len(data) - 1):
        if erpm[i] == 0 or erpm[i + 1] == 0:
            continue
        if abs(erpm[i]) < 250:
            continue
        valid_indices.append(i)
    return valid_indices


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


def get_val_diff(data, key: str, indices: list[int], loop_hertz: int) -> float:
    values = [float(row[key]) for row in data]
    ms_today = [int(row["ms_today"]) for row in data]

    values_diff = []
    for i in indices:
        time_diff = ms_today[i + 1] - ms_today[i]
        value_diff = values[i + 1] - values[i]
        # normalize to erpm change per loop duration
        value_diff *= 1000 / loop_hertz / time_diff  # TODO pre calc
        values_diff.append(value_diff)

    return values_diff


def get_val_avg(data, key: str, indices: list[int]):
    values = [float(row[key]) for row in data]
    values_avg = []
    for i in indices:
        value_avg = (values[i] + values[i + 1]) / 2
        values_avg.append(value_avg)
    return values_avg


def inverse_lin_func(slope, intercept):
    slope_new = 1 / slope
    intercept_new = -intercept / slope
    return slope_new, intercept_new
