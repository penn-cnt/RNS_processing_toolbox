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
import matplotlib.pyplot as plt

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
        ctr = ctr + dlen

    AllTime_UTC = np.concatenate(AllTime_UTC)
    AllTime_UTC = AllTime_UTC.astype('uint64')
    AllData = np.concatenate(AllData, axis = 1)
    AllData = AllData.astype('uint16')
    eventIdx = np.array(eventIdx)
    eventIdx = eventIdx.astype('uint32')


    return AllData, AllTime_UTC, eventIdx

def findStim(AllData, AllTime, Min=15, Channel=1):
    
    #Check orientation of AllData
    if AllData.shape[0] != 4:
        if AllData.shape[1] !=4:
            sys.exit('Error: AllData does not contain 4 channels')
        AllData = AllData.T
    
    # Find Stimulation Triggers

    #Find Slope of Data   
    Slope= np.diff(AllData)/4000;
    Slope[1] = np.where(AllData[Channel][1:]<200, 1, Slope[1])
    Slope[1] = np.where(AllData[Channel][1:]>800, 1, Slope[1])
    
    #Find Start and End Locations of Regions with Zero Slope 
    ZeroSlopeInflections = np.diff(np.where(Slope[1]==0, 1, 0));
    ZeroSlopeStarts = np.argwhere(ZeroSlopeInflections==1).flatten()+1;
    ZeroSlopeEnds = np.argwhere(ZeroSlopeInflections==-1).flatten()+1;
    
    #Find Indices of Stimulation Start and End Points
    StimStartStopIndex= np.vstack(
            (ZeroSlopeStarts[np.argwhere(ZeroSlopeEnds-ZeroSlopeStarts>=Min).flatten()],
                             ZeroSlopeEnds[np.argwhere(ZeroSlopeEnds-ZeroSlopeStarts>=Min).flatten()]))

    #Find Stim Start and End Times
    StimStartStopTimes=np.vstack((AllTime[StimStartStopIndex[0]], AllTime[StimStartStopIndex[1]]))

    stats = dict(); 
    
    #Find Stimulation Lengths
    stats['StimLengths'] = np.diff(StimStartStopIndex, axis=0).flatten()
    
    #Find Max Stim Length
    stats['MaxStimLength'] = max(stats['StimLengths']);
    stats['MaxStimIndex'] = np.argmax(stats['StimLengths']);
    
    #Find Min Stim Length
    stats['MinStimLength'] = min(stats['StimLengths']);
    stats['MinStimIndex'] = np.argmin(stats['StimLengths']);    
    
    return StimStartStopIndex, StimStartStopTimes, stats

 
