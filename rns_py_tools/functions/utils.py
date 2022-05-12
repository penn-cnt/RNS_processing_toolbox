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


def str2dt_usec(s):
    EPOCH = DT.datetime(1970,1,1)
    
    # Either return list or single usec in posixtime
    try:
        dt = [DT.datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f") for x in s]
        return [int((x - EPOCH).total_seconds() * 1000000) for x in dt]
    except:
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
    
    
