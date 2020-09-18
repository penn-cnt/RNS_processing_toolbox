# -*- coding: utf-8 -*-
"""
Ecog Analysis Tools
(RNS Processing Toolbox)

Functions in this file: 
    findStim(AllData, AllTime, Min=15, Channel=1)

"""

import sys
import numpy as np

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


def getEventFeature(AllData, AllTime, Ecog_Events, eventName, nwnd_samp, feature):
    
    startIdx = np.asarray(Ecog_Events['Event Start idx'][Ecog_Events['ECoG trigger']==eventName])
    
    return getFeature(AllData, AllTime, startIdx, nwnd_samp, feature)


def getFeature(AllData, AllTime, startIdx, nwnd_samp, feature):
    """ Get feature calculated over wnd_nsamp """
    
    v_smp = np.arange(nwnd_samp)
    wnd_idx = startIdx.reshape(len(startIdx),1) + v_smp
    
    wind_feats = np.empty([len(startIdx), 4])
    
    for i_chan in range(0,4):
        wind_feats[:,i_chan] = list(map(lambda x: sum(abs(np.diff(x)))/len(x), AllData[i_chan,wnd_idx]))
        
    return wind_feats

 
