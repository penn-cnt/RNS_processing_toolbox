# -*- coding: utf-8 -*-
"""
Conversion Tools
(RNS Processing Toolbox)

Functions in this file: 
    dat2vector(dataFolder, catalog_csv)
    str2dt_usec(s)
    posix2dt_UTC(psx)

"""
import glob
import sys
import os
import numpy as np
import pandas as pd

import jpype
import jpype.imports
from jpype.types import *
from edu.mayo.msel.mefwriter import MefWriter

import datetime as DT

# Constants
NUM_CHANNELS = 4
SAMPLING_RATE = 250


def dat2vector(dataFolder, catalog_csv):
    
    NumberOfFiles = len(glob.glob(os.path.join(dataFolder, "*.dat")));
    ecog_df= pd.read_csv(catalog_csv)

    _checkDatFolderEcogConcordance(ecog_df, NumberOfFiles)

    ctr = 0
    
    AllTime_UTC = []
    AllData = []
    eventIdx = []
    
    for i_file in range(0,NumberOfFiles):
              
        [fdata, ftime] = _readDatFile(dataFolder, ecog_df[i_file:i_file+1])
        dlen = fdata.shape[1]
        AllTime_UTC.append(ftime)
        eventIdx.append(ctr + np.array([0,dlen-1]))
        ctr = ctr + dlen

    AllTime_UTC = np.concatenate(AllTime_UTC)
    AllTime_UTC = AllTime_UTC.astype('uint64')
    AllData = np.concatenate(AllData, axis = 1)
    AllData = AllData.astype('uint16')
    eventIdx = np.array(eventIdx)
    eventIdx = eventIdx.astype('uint32')

    return AllData, AllTime_UTC, eventIdx


def dat2mef(ptID, dataFolder, catalog_csv, config):
    
    NumberOfFiles = len(glob.glob(os.path.join(dataFolder, "*.dat")));
    ecog_df= pd.read_csv(catalog_csv)

    _checkDatFolderEcogConcordance(ecog_df, NumberOfFiles)
    
    inst = config['institution']
    dpath = os.path.join(config['paths']['RNS_DATA_Folder'], ptID, 'mefs/')
    gain = 1; 
 

    for i_file in range(0,NumberOfFiles):
              
        [fdata, ftime] = _readDatFile(dataFolder, ecog_df[i_file:i_file+1])

        blocksize = 16
        th = 100000
        fname= ecog_df['Filename'][i_file]
        
        
        
        for i_chan in range(0,NUM_CHANNELS):
            
            chanLabel= '%s_%sC%d.mef'%(ptID, fname[0:-4], i_chan+1)
            
            print(fdata[i_chan][:])
            
            mw = MefWriter(dpath+chanLabel, blocksize, SAMPLING_RATE, th)
            mw.writeData((fdata[i_chan][:]).astype(int), ftime.astype('l'), fdata.shape[1])
            mw.setInstitution(inst);
            mw.setSubjectID(ptID);
            mw.setChannelName(chanLabel);
            mw.setVoltageConversionFactor(gain);
            mw.close;
    
    
    return None


def str2dt_usec(s):
	dt=DT.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f")
	EPOCH = DT.datetime(1970,1,1)
	return int((dt - EPOCH).total_seconds() * 1000000)


def posix2dt_UTC(psx):
    psx = psx*10**-6
    if psx.shape == ():
        return DT.datetime.utcfromtimestamp(psx)
    utc= [DT.datetime.utcfromtimestamp(x) for x in psx]
    return utc
 

def getNPDataPath(ptID, config, NPDataName):
    '''
    Returns path to NeuroPace files or folders
    
    Args:
        ptID (string): Patient ID
        config (dict): config.json dictionary 
        NPDataName (str): NeuroPace File or Folder name (case insensitive)
            possible file/folder names 
           * Ecog Catalog
           * Dat Folder
           * Daily Histogram
           * Hourly Histogram
           * Episode Durations Folder
            
    Returns:
        string: path to NeuroPace data file or folder
    '''
    
    ptnum = ptIdxLookup(config, 'ID', ptID)
    prefix = '%s_%s_%s'%(config['institution'], 
                         config['patients'][ptnum]['Initials'],
                         config['patients'][ptnum]['PDMS_ID'])
    
    fld = os.path.join(config['paths']['RNS_RAW_Folder'], prefix + ' EXTERNAL #PHI')
    
    switcher = {
        'ecog catalog':     os.path.join(fld, prefix + '_ECoG_Catalog.csv'),
        'hourly histogram': os.path.join(fld, prefix + ' Histograms EXTERNAL #PHI', prefix + '_Histogram_Hourly.csv'),
        'daily histogram':  os.path.join(fld, prefix + ' Histograms EXTERNAL #PHI', prefix + '_Histogram_Daily.csv'),
        'dat folder':       os.path.join(fld, prefix + ' Data EXTERNAL #PHI'),
        'episode durations folder': os.path.join(fld, prefix + ' EpisodeDurations EXTERNAL #PHI')
            }
    
    return switcher.get(NPDataName.lower(), "File/Folder not found")


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


#### Helper Functions #####

def _checkDatFolderEcogConcordance(ecog_df, NumberOfFiles):
    ''' Check for inconsistencies between files in dat folder and entries in ecog_df'''
    
    ecog_df['Raw UTC timestamp'] = pd.to_datetime(ecog_df['Raw UTC timestamp'], format= '%Y-%m-%d %H:%M:%S.%f')
    
    if ecog_df.shape[0] != NumberOfFiles:
        sys.exit("Error: mismatched number of.dat files and ECoG catalog length")
    
    if len(np.unique(ecog_df['Sampling rate'])) > 1:
        sys.exit("Error: Multiple SamplingRates in file")
        
    if not (ecog_df['Sampling rate'][0] == SAMPLING_RATE):
         sys.exit("Error: Unexpected sampling rate")
        
    if sum(n < np.timedelta64(0) for n in np.diff(ecog_df['Raw UTC timestamp'])) > 0:
        sys.exit("Error: RawUTCTimestamp is not chronological")
        
        
def _readDatFile(dataFolderPath, ecog_df):

    # Open up dat_file
    dat_file = os.path.join(dataFolderPath, ecog_df['Filename'][0])
    fs = ecog_df['Sampling rate'][0]
    
    with open(dat_file, 'rb') as fid:
        fdata = np.fromfile(fid, np.int16).reshape((-1, NUM_CHANNELS)).T
    
    # Add data in each channel of fdata array if channel is "ON", zeros if "OFF"
    if ecog_df['Ch 1 enabled'][0]== 'Off':
        fdata = np.insert(fdata, 0, 0, axis=0)
    if ecog_df['Ch 2 enabled'][0] == 'Off':
        fdata = np.insert(fdata, 1, 0, axis=0)
    if ecog_df['Ch 3 enabled'][0] == 'Off':
        fdata = np.insert(fdata, 2, 0, axis=0)
    if ecog_df['Ch 4 enabled'][0] == 'Off':
        fdata = np.insert(fdata, 3, 0, axis=0)
        
    # Calculate associated time vector    
    dlen = fdata.shape[1]
    t_vec = np.arange(dlen)/fs*10**6
    t_start = (ecog_df['Raw UTC timestamp'][0]- pd.Timestamp("1970-01-01")) // pd.Timedelta('1us')
    
    ftime = t_start + t_vec
    
    return fdata, ftime
    
    
