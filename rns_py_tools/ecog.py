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
  ''' Get time points and indices of all stimulation events in AllData. 
    Inputs: 
      AllData- vector of data in microseconds
      AllTime- vector of time in microseconds
      Min- table of patient events
      Channel - Which channel to find stims on. 
    
    Output: 
      StimStartStopIndex- An [N x 2] matrix of start/stop index pairs per stim
      StimStartStopTimes- An [N x 2] matrix of start/stop times per stim
      stats- information about distribution of stims. 
  '''
    
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


def getStimGroups(StimStartStopIndex, StimStartStopTimes, maxInterval=90):
    ''' Return start and stop times of groups of stimulations that fall within
      maxInterval. 
      
      Inputs: 
      StimStartStopTimes- An [N x 2] matrix of start/stop times per stim
      StimStartStopIndex- An [N x 2] matrix of start/stop index pairs per stim
      maxInterval- max time interval containing a group (sec), default: 90
      
      Example: 
      [stim_ind, stim_times] = findStim(AllData, AllTime)
      stimGroups = getStimGroups(stim_times)
    '''
      
    assert StimStartStopTimes.shape[0]==2, "StimStartStopTimes should be 2xN"
    assert StimStartStopIndex.shape[0]==2, "StimStartStopIndex should be 2xN"
    
    mxInt = maxInterval * 10**6        #convert to usec
    
    N = StimStartStopTimes.shape[1]
  
    stim_idx = 0
    n_grp = 1
    start_idx = 0 
    grp_start = StimStartStopTimes[0,0];
  
    stimGroups = []
  
    while stim_idx < N-1:
        # Record stim group if next stim ends outside of mxInt range
        if (StimStartStopTimes[1,stim_idx+1] - grp_start) > mxInt:
            grp_stop = StimStartStopTimes[1,stim_idx]
            stimGroups.append([grp_start, grp_stop, 
                               StimStartStopIndex[0,start_idx], StimStartStopIndex[1,stim_idx],
                               n_grp])
            # Restet counters
            n_grp = 0
            grp_start = StimStartStopTimes[0,stim_idx+1]
            start_idx = stim_idx+1
            
        # Increment counters
        n_grp += 1
        stim_idx += 1
  
    return np.array(stimGroups)
         

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

 
