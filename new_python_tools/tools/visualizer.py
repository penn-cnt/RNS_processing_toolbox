import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import times
import logging

logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)


def plot_clips(data, df, ind, annot=None):
    color_map = {
        "Seizure": "tab:red",
        "Non-Seizure": "tab:blue",
        "Unclear": "tab:gray"
    }
    spacing = 5
    dmin = -200
    dmax = 200
    dr = (dmax - dmin)  # displayed range
    n_samples, n_rows = data.shape[0], data.shape[1]
    h, w = n_rows * 1.5, 15

    start_time_string = df['Raw UTC timestamp']
    pre_trigger_length = df['ECoG pre-trigger length']
    start_time = datetime.strptime(start_time_string, "%Y-%m-%d %H:%M:%S.%f") - timedelta(seconds=pre_trigger_length)
    time_length = df['ECoG length']
    start_time_ms = start_time.strftime('.%f')
    start_time_s = start_time.strftime('%S')
    initial_offset = (float(start_time_s) + float(start_time_ms)) % spacing
    x_scale = np.linspace(initial_offset, initial_offset + time_length, n_samples)

    y_tick_offsets = (np.arange(n_rows) * dr)[::-1]
    x_tick_offset = [i * spacing for i in range(int(time_length // spacing) + 2)]

    x_label_dt = [start_time + timedelta(seconds=i * spacing - initial_offset) for i in
                  range(int(time_length // spacing) + 2)]
    x_label = [t.strftime('%M:%S') for t in x_label_dt]

    plt.figure(figsize=(w, h))
    ax = plt.axes()

    if isinstance(annot, pd.DataFrame):
        session_idx = annot["Session Index"]
        if np.isin(session_idx, ind).any():
            annot_row = annot[annot["Session Index"] == ind]
            for i, row in annot_row.iterrows():
                annot_time_start_ts, annot_time_end_ts = row["Start UTC Time"], row[
                    "End UTC Time"]
                annot_time_start, annot_time_end = times.utctimeobj_to_timestamp(
                    annot_time_start_ts), times.utctimeobj_to_timestamp(annot_time_end_ts)
                time_start, time_end = df['Start UTC Timestamp'], df['End UTC Timestamp']
                annotation_scale_start = x_scale[-1] - (time_end - annot_time_start) / (time_end - time_start) * (
                        x_scale[-1] - x_scale[0])
                annotation_scale_end = x_scale[-1] - (time_end - annot_time_end) / (time_end - time_start) * (
                        x_scale[-1] - x_scale[0])
                plt.axvspan(annotation_scale_end, annotation_scale_start, color=color_map[row["Class"]], alpha=0.5,
                            label=row["Class"])

    eeg_data = data.T + y_tick_offsets[:, np.newaxis]

    plt.plot(x_scale, eeg_data.T, 'k', linewidth=0.1)

    plt.yticks(y_tick_offsets)
    ax.set_yticklabels(["Ch1", "Ch2", "Ch3", "Ch4"])
    plt.xticks(x_tick_offset)
    ax.set_xticklabels(x_label, rotation=45)
    plt.xlabel('Time (s)')
    plt.title(
        df["Patient ID"] + ",  " + str(ind) + ",  " + df["ECoG trigger"] + ",  " + str(
            round(time_length, 3)) + "s" + ",  " + start_time_string)
    plt.grid(axis='x')
    plt.legend(loc='upper right')
    plt.show()


def plot_data(data, dr=200):
    n_samples, n_rows = data.shape[0], data.shape[1]
    h, w = n_rows * 1.5, 15

    y_tick_offsets = (np.arange(n_rows) * dr)[::-1]

    plt.figure(figsize=(w, h))
    ax = plt.axes()

    eeg_data = data.T + y_tick_offsets[:, np.newaxis]

    plt.plot(eeg_data.T, 'k', linewidth=0.1)

    plt.yticks(y_tick_offsets)
    ax.set_yticklabels(["Ch1", "Ch2", "Ch3", "Ch4"])
    plt.xlabel('Time (s)')

    plt.show()


def plot_data_list(data_list, dr=200):
    n_samples, n_rows = data_list[0].shape[0], data_list[0].shape[1]
    h, w = n_rows * 1.5, 15

    y_tick_offsets = (np.arange(n_rows) * dr)[::-1]

    plt.figure(figsize=(w, h))
    ax = plt.axes()

    for data in data_list:
        eeg_data = data.T + y_tick_offsets[:, np.newaxis]
        plt.plot(eeg_data.T, linewidth=1)

    plt.yticks(y_tick_offsets)
    ax.set_yticklabels(["Ch1", "Ch2", "Ch3", "Ch4"])
    plt.xlabel('Time (s)')

    plt.show()


def get_color_map(annot_map, annots, class_n=3):
    color_map = []
    type_map = []
    if class_n == 3:
        for ind in annot_map:
            class_type = annots.iloc[ind]['Class']
            if class_type == 'Seizure':
                color_map.append('gold')
                type_map.append(1)
            elif class_type == 'Non-Seizure':
                color_map.append('black')
                type_map.append(0)
            elif class_type == 'Unclear':
                color_map.append('tab:gray')
                type_map.append(2)
    elif class_n == 2:
        for ind in annot_map:
            class_type = annots.iloc[ind]['Class']
            if class_type == 'Seizure':
                color_map.append('gold')
                type_map.append(1)
            elif class_type == 'Non-Seizure':
                color_map.append('black')
                type_map.append(0)
            elif class_type == 'Unclear':
                color_map.append('gold')
                type_map.append(1)

    return color_map, type_map


def int_clips(data, df, ind, window_start_ind, window_end_ind, path='interactive_cache'):
    '''
    plot the picture to show in interactive plot
    :param data: data to be ploted
    :param df: dataframe of the row
    :param ind: index of event
    :param window_start_ind: ind of start of highlight
    :param window_end_ind: ind of end of highlight
    :param path: path to save the cache picture
    :return:
    '''
    color_map = {
        "Seizure": "gold",
        "Non-Seizure": "black",
        "Unclear": "gray"
    }
    spacing = 5
    dmin = -200
    dmax = 200
    dr = (dmax - dmin)  # displayed range
    n_samples, n_rows = data.shape[0], data.shape[1]
    h, w = n_rows * 1.5, 10

    start_time_string = df['Raw UTC timestamp']
    pre_trigger_length = df['ECoG pre-trigger length']
    start_time = datetime.strptime(start_time_string, "%Y-%m-%d %H:%M:%S.%f") - timedelta(seconds=pre_trigger_length)
    time_length = df['ECoG length']
    start_time_ms = start_time.strftime('.%f')
    start_time_s = start_time.strftime('%S')
    initial_offset = (float(start_time_s) + float(start_time_ms)) % spacing
    x_scale = np.linspace(initial_offset, initial_offset + time_length, n_samples)

    y_tick_offsets = (np.arange(n_rows) * dr)[::-1]
    x_tick_offset = [i * spacing for i in range(int(time_length // spacing) + 2)]

    x_label_dt = [start_time + timedelta(seconds=i * spacing - initial_offset) for i in
                  range(int(time_length // spacing) + 2)]
    x_label = [t.strftime('%M:%S') for t in x_label_dt]

    plt.figure(figsize=(w, h))
    ax = plt.axes()

    event_start_ind = df['Event Start idx']
    event_end_ind = df['Event End idx']
    window_start_ind = window_start_ind
    window_end_ind = window_end_ind

    annotation_scale_start = x_scale[-1] - (event_end_ind - window_start_ind) / (event_end_ind - event_start_ind) * (
            x_scale[-1] - x_scale[0])
    annotation_scale_end = x_scale[-1] - (event_end_ind - window_end_ind) / (event_end_ind - event_start_ind) * (
            x_scale[-1] - x_scale[0])
    plt.axvspan(annotation_scale_end, annotation_scale_start, color='gold', alpha=0.5)

    eeg_data = data.T + y_tick_offsets[:, np.newaxis]

    plt.plot(x_scale, eeg_data.T, 'k', linewidth=0.1)

    plt.yticks(y_tick_offsets)
    ax.set_yticklabels(["Ch1", "Ch2", "Ch3", "Ch4"])
    plt.xticks(x_tick_offset)
    ax.set_xticklabels(x_label, rotation=45)
    plt.xlabel('Time (s)')
    plt.title(
        df["Patient ID"] + ",  " + str(ind) + ",  " + df["ECoG trigger"] + ",  " + str(
            round(time_length, 3)) + "s" + ",  " + start_time_string)
    plt.grid(axis='x')
    plt.legend(loc='upper right')
    plt.savefig(path + ".png")
    # plt.show()


def stack_patient_match(plot_ind, id_list, ind_list):
    cs_end = np.cumsum(ind_list)
    cs_start = np.hstack(([0], cs_end[:-1]))
    id = times.find_closest_event_ind(plot_ind, cs_start)
    return id_list[id], plot_ind - cs_start[id]
