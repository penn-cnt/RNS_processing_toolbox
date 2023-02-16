# -*- coding: utf-8 -*-
"""
Utilities
(RNS Processing Toolbox)

Functions in this file: 
    str2dt_usec(s)
    posix2dt_UTC(psx)
    ptIdxLookup(config, ID_field, ID)

"""
import datetime as DT
import os.path as pth
import pandas as pd
import numpy as np

def str2dt_usec(s):
    EPOCH = DT.datetime(1970,1,1)
    
    # Either return list or single usec in posixtime
    if type(s) is list:
        if isinstance(s[0], pd.Timestamp):
            dt = [x.to_pydatetime() for x in s]
        else:
            dt = [DT.datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f") for x in s]
        return [int((x - EPOCH).total_seconds() * 1000000) for x in dt]
    else:
        if isinstance(s, pd.Timestamp):
            dt = s.to_pydatetime()
        dt= DT.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f")
	
    return int((dt - EPOCH).total_seconds() * 1000000)


def posix2dt_UTC(psx):
    try:
        utc= [DT.datetime.utcfromtimestamp(x*10**-6) for x in psx]
    except:
        utc = DT.datetime.utcfromtimestamp(psx*10**-6)
    return utc
 

def ptIdxLookup(config, ID_field, ID):
    '''
    Look up patient idex in config based on patient ID

    Args:
        config (dict): config.json object
        ID_field (string): field type to match
        ID (string): patient ID

    Returns:
        patient index
    '''
    
    ids = [f[ID_field] for f in config['patients']]
    return ids.index(ID)


def getDataPath(ptID, config, dataName):
    '''
    Returns path to deidentified RNS files or folders
    
    Args:
        ptID (string): Patient ID
        config (dict): config.json dictionary 
        NPDataName (str): Deidentified RNS File or Folder name (case insensitive)
            possible file/folder names: 
           * Ecog Catalog
           * Daily Histogram
           * Hourly Histogram
           * Episode Durations Folder
            
    Returns:
        string: path to NeuroPace data file or folder
    '''
    
    fld = pth.join(config['paths']['RNS_DATA_Folder'], ptID)
    
    switcher = {
        'ecog catalog':     pth.join(fld, 'ECoG_Catalog.csv'),
        'hourly histogram': pth.join(fld, ' Histograms', 'Histogram_Hourly.csv'),
        'daily histogram':  pth.join(fld, ' Histograms', 'Histogram_Daily.csv'),
        'episode durations folder': pth.join(fld, ' EpisodeDurations')
            }
    
    return switcher.get(dataName.lower(), "File/Folder not found")    


def filterWindows(windowsetOutside, windowsetInside):
    # Returns List where windowsetOutside _inculdes_ the entirety of windowsetInside, 
    # and where windowsetOutside excludes the entirety of windowsetInside.
    # set1_inclusive_inds: indices of windows in windowsetOutside that overlap
    # windows of windowsetInside
    # set1_exclusive_inds: indices of windows in windowsetOutside that have no
    # overlap with windowsetInside
    # set2_included_inds: indices of windowsetInside that are fully contained by 
    
    if np.ndim(windowsetInside) == 1:
        if len(windowsetInside) == 2:
            print('Warning: windowsetInside will be interpreted as two separate datapoints.', 
                'Input a 2D numpy array if the input should be interpreted as a single window')
        windowsetInside = np.stack((windowsetInside, windowsetInside), axis=1)
    
    # window start is between stim bounds
    noStim_inds1 = np.array([np.sum((x >= windowsetInside[:, 0]) & (x <= windowsetInside[:, 1]))==0 for x in windowsetOutside[:, 0]])
    
    # window end is between stim bounds
    noStim_inds2 = np.array([np.sum((x >= windowsetInside[:, 0]) & (x <= windowsetInside[:, 1]))==0 for x in windowsetOutside[:, 1]])
    
    # window contains both stim bounds
    noStim_inds3 = np.array([np.sum((windowsetOutside[i, 0] <= windowsetInside[:, 0]) & (windowsetOutside[i, 1] >= windowsetInside[:, 1]))==0 for i in range(windowsetOutside.shape[0])])
    
    set1_exclusive_inds = (noStim_inds1 & noStim_inds2 & noStim_inds3)
    set1_inclusive_inds = ~set1_exclusive_inds
    
    set2_included_inds = np.array([np.sum((windowsetInside[i, 0] >= windowsetOutside[:, 0]) & (windowsetInside[i, 1] <= windowsetOutside[:, 1]))==1 for i in range(windowsetInside.shape[0])])
    
    return set1_inclusive_inds, set1_exclusive_inds, set2_included_inds


