from datetime import datetime, timezone, timedelta
import numpy as np


def timestamp_to_utctime(ts):
    """
    :param ts: int - datetime timestamp
    :return: string - utc time
    """
    return datetime.utcfromtimestamp(ts * 1e-6)


def utctimeobj_to_timestamp(ts):
    """
    :param ts: datetime object - utc time
    :return: int - datetime time stamp
    """
    return int(ts.replace(tzinfo=timezone.utc).timestamp() * 1e6)


def timestring_to_timestamp(timestring, time_delta=0.0):
    """
    :param timestring: string - time string
    :param time_delta: float - time offset in second
    :return: int - datetime timestamp
    """
    time = datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S.%f") + timedelta(seconds=time_delta)
    return int(time.replace(tzinfo=timezone.utc).timestamp() * 1e6)


def timestring_to_timeobj(timestring, time_delta=0.0):
    """
    parse time string to time object
    :param timestring: string - time in string
    :param time_delta: float - time offset in second
    :return: datetime object - time object
    """
    time = datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S.%f") + timedelta(seconds=time_delta)
    return time


def find_ind_in_data(catalog, start_ind, end_ind, annot):
    """
    helper function to find index in catalog
    :param catalog:
    :param start_ind:
    :param end_ind:
    :param annot:
    :return:
    """
    start_time, end_time = catalog['Start UTC Timestamp'], catalog['End UTC Timestamp']
    annot_time = annot
    annot_ind = round(end_ind - (end_time - annot_time) / (end_time - start_time) * (end_ind - start_ind))
    return int(annot_ind)


def find_closest_event_ind(value, array, threshold = 0):
    '''
    find the index of event
    :param value: the time stamp
    :param array: the array of starting time
    :return: event index
    '''
    array = np.asarray(array)
    diff = array - value
    valid_idx = np.where(diff <= threshold)[0]
    out = valid_idx[diff[valid_idx].argmax()]
    return out


def timestamp_to_ind(timestamp, catalog):
    """
    :param timestamp: int - timestamp in a dataset
    :param catalog: dataframe - catalog
    :return: event_ind: index of the event this timestamp is at, data_ind: the corresponding index of the data of timestamp
    """
    start_timestamps = catalog['Start UTC Timestamp']
    event_ind = find_closest_event_ind(timestamp, start_timestamps, threshold=0.5e6)
    df_row = catalog.iloc[event_ind]
    ind_start = df_row['Event Start idx']
    ind_end = df_row['Event End idx']
    data_ind = find_ind_in_data(df_row, ind_start, ind_end, timestamp)
    return event_ind, data_ind

def ind_to_timestamp(ind, catalog):
    catalog_ind = find_closest_event_ind(ind,catalog['Event Start idx'])
    start_time = catalog['Start UTC Timestamp'][catalog_ind]
    end_time = catalog['End UTC Timestamp'][catalog_ind]
    start_ind = catalog['Event Start idx'][catalog_ind]
    end_ind = catalog['Event End idx'][catalog_ind]
    time = end_time-(end_ind-ind)/(end_ind-start_ind)*(end_time-start_time)
    return time