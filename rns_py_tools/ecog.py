# -*- coding: utf-8 -*-
"""
Ecog Analysis Tools
(RNS Processing Toolbox)

Functions in this file: 
    findStim(AllData, AllTime, Min=15, Channel=1)

"""

import sys
import numpy as np

def findStims(AllData, AllTime, Min=15, Channel=1):
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
  StimStartStopIndex = np.vstack(
          (ZeroSlopeStarts[np.argwhere(ZeroSlopeEnds-ZeroSlopeStarts>=Min).flatten()],
                           ZeroSlopeEnds[np.argwhere(ZeroSlopeEnds-ZeroSlopeStarts>=Min).flatten()]))
  
  #Find Stim Start and End Times
  StimStartStopTimes = np.vstack((AllTime[StimStartStopIndex[0]], AllTime[StimStartStopIndex[1]]))
  
  stats = dict(); 
  
  #Find Stimulation Lengths
  stats['StimLengths'] = np.diff(StimStartStopIndex, axis=0).flatten()
  
  #Find Max Stim Length
  stats['MaxStimLength'] = max(stats['StimLengths']);
  stats['MaxStimIndex'] = np.argmax(stats['StimLengths']);
  
  #Find Min Stim Length
  stats['MinStimLength'] = min(stats['StimLengths']);
  stats['MinStimIndex'] = np.argmin(stats['StimLengths']);    
  
  return StimStartStopIndex.T, StimStartStopTimes.T, stats


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
      
    assert StimStartStopTimes.shape[1]==2, "StimStartStopTimes should be Nx2"
    assert StimStartStopIndex.shape[1]==2, "StimStartStopIndex should be Nx2"
    
    mxInt = maxInterval * 10**6        #convert to usec
    
    N = StimStartStopTimes.shape[0]
  
    stim_idx = 0
    n_grp = 1
    start_idx = 0 
    grp_start = StimStartStopTimes[0,0];
  
    stimGroups = []
  
    while stim_idx < N-1:
        # Record stim group if next stim ends outside of mxInt range
        if (StimStartStopTimes[stim_idx+1,1] - grp_start) > mxInt:
            grp_stop = StimStartStopTimes[stim_idx,1]
            stimGroups.append([grp_start, grp_stop, 
                               StimStartStopIndex[start_idx,0], StimStartStopIndex[stim_idx,1],
                               n_grp])
            # Restet counters
            n_grp = 0
            grp_start = StimStartStopTimes[stim_idx+1,0]
            start_idx = stim_idx+1
            
        # Increment counters
        n_grp += 1
        stim_idx += 1
  
    return np.array(stimGroups)
         

def getEventIdx(AllData, Ecog_Events, eventName):
    strt = Ecog_Events['Event Start idx'][Ecog_Events['ECoG trigger']== eventName]
    end = Ecog_Events['Event End idx'][Ecog_Events['ECoG trigger']== eventName]
    
    return np.vstack((strt, end)).T


def getIntersectingIntervals(ivals1, ivals2):
    '''
    get indices for intervals that overlap in two interval lists
    
    Parameters
    ----------
    ivals1 : [N x 2] list of disjoint intervals
    ivals2 : [N x 2] list of disjoint intervals

    Returns
    -------
    overlp_idx1 : index list of intervals in ivals1 that overlap ivals2 
    overlp_idx2 : index list of intervals in ivals2 that overlap ivals1

    '''
    assert ivals1.shape[1]==2, "StimStartStopTimes should be 2xN"
    assert ivals2.shape[1]==2, "StimStartStopIndex should be 2xN"
    
    # i and j pointers for ivals1  
    # and ivals2 respectively 
    i = j = 0
      
    n = len(ivals1) 
    m = len(ivals2)
    
    overlp_idx1 = set()
    overlp_idx2= set()
    
    ivals1 = sorted(ivals1, key=lambda x: x[0])
    ivals2 = sorted(ivals2, key=lambda x: x[0])
  
    # Loop through all intervals unless one  
    # of the interval gets exhausted 
    while i < n and j < m: 
          
        # Left bound for intersecting segment 
        l = max(ivals1[i][0], ivals2[j][0]) 
          
        # Right bound for intersecting segment 
        r = min(ivals1[i][1], ivals2[j][1]) 
          
        # If segment is overlapping
        if l <= r:  
            overlp_idx1.add(i)
            overlp_idx2.add(j)
  
        # If i-th interval's right bound is  
        # smaller increment i else increment j 
        if ivals1[i][1] < ivals2[j][1]: 
            i += 1
        else: 
            j += 1
            
    return list(overlp_idx1), list(overlp_idx2)
      

def getWindowIdx(stIdx, AllTime, winDur, offsetDur):
    '''

    Parameters
    ----------
    stIdx : vector of starting indices from which to calculate the window
    AllTime : Time vector
    winDur : positive int, duration of window in seconds
    offsetDur : signed int: offset (in seconds) at which to start counting the window

    Returns
    -------
    windowIdx : [N x 2] matrix of window indices

    '''
    offset = offsetDur * 10**6
    wind = winDur * 10**6
    
    start_times = AllTime[stIdx] + offset
    end_times = AllTime[stIdx] + offset + wind
    
    #Map start and end times to closest index 
    start_idx=ecog._mapTimeToIdx(AllTime, start_times)
    end_idx=ecog._mapTimeToIdx(AllTime, end_times)
    
    #Throw out windows that may straddle multiple clips
    
    AllTime[end_idx]-AllTime[start_idx]
    
    return windowIdx


# def getFeature(AllData, AllTime, startIdx, nwnd_samp, feature):
#     """ Get feature calculated over wnd_nsamp """
    
#     v_smp = np.arange(nwnd_samp)
#     wnd_idx = startIdx.reshape(len(startIdx),1) + v_smp
    
#     wind_feats = np.empty([len(startIdx), 4])
    
#     for i_chan in range(0,4):
#         wind_feats[:,i_chan] = list(map(lambda x: sum(abs(np.diff(x)))/len(x), AllData[i_chan,wnd_idx]))
        
#     return wind_feats

def _mapTimeToIdx(AllTime, timeVector):
    
    #t_idx = [abs(AllTime-time).argmin() for time in timeVector]
    
    diff= np.inf
    j = 0 #pointer to sorted timeVector
    
    t_idx = []
    
    for i in range(0,len(AllTime)-1):
        d = abs(AllTime[i+1]-timeVector[j]) 
        #print(d)
        if d >= diff:
            while d >= diff:
                #print(i)
                t_idx.append(i)
                j = j + 1
                if j >= len(timeVector):
                    return t_idx
                diff = abs(AllTime[i]-timeVector[j])
                d = abs(AllTime[i+1]-timeVector[j])
            diff = d
        else: 
            diff = d
              
    return t_idx

    
 
