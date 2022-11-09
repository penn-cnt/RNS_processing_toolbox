import math
import numpy as np
from tqdm import tqdm
import times


def NumWins(winLen, winDisp, xLen, fs):
    '''
    Find the number of the windows for segmentation
    :param winLen: float - length of window in second
    :param winDisp: float - displacement of the window padding in second
    :param xLen: int - the number of samples in the dataset
    :param fs: float - sample rate in Hz
    :return:
    '''
    try:
        if winDisp != winLen:
            numwins = math.floor((xLen / fs - winLen + winDisp) / winDisp)
        else:
            numwins = math.floor((xLen / fs) / winDisp)
    except:
        print("Invalid Inputs")
    return numwins


def indexHelper(x, fs, winLen, winDisp):
    '''
    find the start & stop index of each window
    :param x: data
    :param fs: float- sample rate
    :param winLen: float - length of window in second
    :param winDisp: float - displacement of the window padding in second
    :return:
    '''
    # helper function to return the indices of list slices based on right-align rule for the original signal
    numWins = NumWins(winLen, winDisp, x.shape[0], fs)
    indexes = []

    for ind in range(numWins):
        start = x.shape[0] - int(ind * winDisp * fs + winLen * fs)
        end = start + int(winLen * fs) - 1
        indexes.append([start, end])
    indexes_rev = indexes[::-1]
    return np.array(indexes_rev)


def get_windowed_ind(start_data_ind, end_data_ind, fs, window_length, window_disp, verbose=False):
    """
    return a list of index of the segmented data
    :param start_data_ind: list of int - index of start of data
    :param end_data_ind: list of int - index of end of data
    :param fs: float - sample rate
    :param window_length: float - length of window in second
    :param window_disp: float - displacement of the window padding in second
    :param verbose: show progress bar
    :return: a list of index of the segmented data
    """
    windowed_ind_list = []
    for start_ind, end_ind in tqdm(zip(start_data_ind, end_data_ind), disable=not verbose):
        dummy_sequence = np.arange(start=start_ind, stop=end_ind)
        start_stop_ind = indexHelper(dummy_sequence, fs, window_length, window_disp)
        windowed_data_ind = dummy_sequence[start_stop_ind]
        windowed_ind_list.append(windowed_data_ind)

    return windowed_ind_list


def get_windowed_data(data, windowed_ind_list, stack=True, verbose=False):
    """
    use windowed index list of data to return the list of windowed data
    :param data: data
    :param windowed_ind_list: list
    :param verbose: show progress bar
    :return: list - list of windowed data
    """
    windowed_data_list = []
    for inds in tqdm(windowed_ind_list, disable=not verbose):
        length = len(inds)
        windowed_data = np.empty((length, inds[0, 1] - inds[0, 0], 4))
        for i, ind in enumerate(inds):
            windowed_data[i] = data[ind[0]:ind[1]]
        windowed_data_list.append(windowed_data)
    if stack:
        return np.vstack(windowed_data_list)
    return windowed_data_list


def get_annot_map(windowed_ind, reference_indices):
    '''
    get the map of annotations to the windowed data
    :param windowed_ind: indices of windowed data
    :param reference_indices: the start indices of respective data
    :return:
    '''
    windowed_ind_stack = np.vstack(windowed_ind)
    annot_map = np.empty(len(windowed_ind_stack)).astype(int)
    for i, itb in enumerate(windowed_ind_stack):
        annot_map[i] = times.find_closest_event_ind(itb[0], reference_indices)
    return annot_map


def get_concatenation_ind(windowed_ind, concat_n):
    clip_len = np.empty(len(windowed_ind))
    clip_start_stop_table = np.empty((len(windowed_ind), 2)).astype(int)
    for i, ind in enumerate(windowed_ind):
        clip_len[i] = ind.shape[0]
    clip_len_cumsum = np.cumsum(clip_len).astype(int)
    clip_start_stop_table[:, 1] = clip_len_cumsum - 1
    clip_start_stop_table[:, 0] = np.hstack(([0], clip_len_cumsum[:-1]))
    concatenate_ind_table = np.empty((clip_len_cumsum[-1], concat_n * 2 + 1)).astype(int)
    j = 0
    for i, start_stop_ind in enumerate(clip_start_stop_table):
        start_ind = start_stop_ind[0]
        stop_ind = start_stop_ind[1]
        for window_ind in np.arange(start_ind, stop_ind + 1):
            concatenate_ind = np.arange(window_ind - concat_n, window_ind + concat_n + 1)
            concatenate_ind = np.where(concatenate_ind < start_ind, start_ind, concatenate_ind)
            concatenate_ind = np.where(concatenate_ind > stop_ind, stop_ind, concatenate_ind)
            concatenate_ind_table[j] = concatenate_ind
            j += 1
    return concatenate_ind_table


def get_concatenation_data(data, concatenate_ind_table, arrange='time_stack'):
    if arrange == "time_stack":
        concatenate_data = data[concatenate_ind_table]
        concatenate_data = concatenate_data.transpose([0, 2, 1, 3])
        d1, d2, d3, d4 = concatenate_data.shape
        concatenate_data = concatenate_data.reshape((d1, d2, d3 * d4))
    elif arrange == 'channel_stack':
        concatenate_data = data[concatenate_ind_table]
        concatenate_data = concatenate_data.transpose([0, 2, 3, 1])
        d1, d2, d3, d4 = concatenate_data.shape
        concatenate_data = concatenate_data.reshape((d1, d2, d3 * d4))
    elif arrange == 'time_concat':
        concatenate_data = data[concatenate_ind_table]
        concatenate_data = concatenate_data.transpose([0, 1, 2, 3])
        d1, d2, d3, d4 = concatenate_data.shape
        concatenate_data = concatenate_data.reshape((d1, d2*d3, d4))

    return concatenate_data
