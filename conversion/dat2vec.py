# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import glob
import sys
import os
import numpy as np
import pandas as pd

def dat2vector(dataFolder, catalog_csv):
    
    Folder = glob.glob(os.path.join(dataFolder, "*.dat"));
    NumberOfFiles = len(Folder)
    
    csv_file = pd.read_csv(catalog_csv)
    csv_file['Raw UTC timestamp'] = pd.to_datetime(csv_file['Raw UTC timestamp'], format= '%Y-%m-%d %H:%M:%S.%f')
    
    if csv_file.shape[0] != NumberOfFiles:
        sys.exit("Error: mismatched number of.dat files and ECoG catalog length")
    
    if len(np.unique(csv_file['Sampling rate'])) > 1:
        sys.exit("Error: Multiple SamplingRates in file")
        
    if sum(n < np.timedelta64(0) for n in np.diff(csv_file['Raw UTC timestamp'])) > 0:
        sys.exit("Error: RawUTCTimestamp is not chronological")
    
    fs = csv_file['Sampling rate'][1]
    startTime_rawUTC = (csv_file['Raw UTC timestamp']- pd.Timestamp("1970-01-01")) // pd.Timedelta('1us')
    ctr = 0
    
    AllTime_UTC = []
    AllData = []
    eventIdx = []
    
    for i_file in range(0,NumberOfFiles):
        
        NumChannels = csv_file['Waveform count'][i_file]
        fname = csv_file['Filename'][i_file]
        
        print(i_file)
        
        with open(os.path.join(dataFolder, fname), 'rb') as fid:
            fdata = np.fromfile(fid, np.int16).reshape((-1, NumChannels)).T
           
        if csv_file['Ch 1 enabled'][i_file] == 'Off':
            fdata = np.insert(fdata, 0, 0, axis=0)
        if csv_file['Ch 2 enabled'][i_file] == 'Off':
            fdata = np.insert(fdata, 1, 0, axis=0)
        if csv_file['Ch 3 enabled'][i_file] == 'Off':
            fdata = np.insert(fdata, 2, 0, axis=0)
        if csv_file['Ch 4 enabled'][i_file] == 'Off':
            fdata = np.insert(fdata, 3, 0, axis=0)
              
        
        dlen = fdata.shape[1]
        AllData.append(fdata)
        
        t_vec = np.arange(dlen)/fs
        AllTime_UTC.append(startTime_rawUTC[i_file]+t_vec*10**6)
        #AllTime_UTC= np.append(AllTime_UTC, startTime_rawUTC[i_file]+t_vec*10**6)
        
        eventIdx.append(ctr + np.array([0,dlen-1]))
        ctr = ctr + dlen; 

    AllTime_UTC = np.concatenate(AllTime_UTC)
    AllData = np.concatenate(AllData, axis = 1)
    eventIdx = np.array(eventIdx)

    return AllData, AllTime_UTC, eventIdx
    
    