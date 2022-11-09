from tqdm import tqdm


def normalize(data, dmin, dmax, verbose=False):
    '''
    z-score the data
    :param data: list - windowed data
    :param dmin: float - min of data
    :param dmax: float - max of data
    :param verbose: show progress bar
    :return: list - windowed data
    '''
    for i, d in tqdm(enumerate(data), total=len(data), disable=not verbose):
        data[i] = (d - dmin) / (dmax - dmin)
    return data


def normalization_recover(dg_data_norm, mm):
    """
    :param dg_data_norm: [nd.array(n,5),nd.array(n,5),nd.array(n,5)], normalized digital glove datas for all subjects
    :param mm: list of tuples, mins and maxs for the dg_data
    :return: [nd.array(n,5),nd.array(n,5),nd.array(n,5)], digital glove data in original scale
    """
    # TODO: implement function
    pass
