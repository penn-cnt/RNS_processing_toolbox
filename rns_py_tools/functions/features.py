#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hdf5storage
import json
import os
import numpy as np
import pandas as pd


def findStim(AllData, ecogT, Min=15, show=False):
    '''findStim finds the Stimulation Group periods in Neuropace RNS timeseries data
    
      To use default Channel=1, Min=15, show = false
    
      [StimStartStopIndex, StimStartStopTimes, StimGap, stats]= findStim(AllData, AllTime)
    
      To use Channel 2 with a min of 3 points length
    
      [StimStartStopIndex, StimStartStopTimes, StimGap, stats]= findStim(AllData, AllTime ,'Min',3,'Channel',2)
    
    Inputs
      AllData: A matrix in which each row contains Voltage data for a given
      channel
    
      AllTime: Corresponding Times to Data points in AllData
    
      Min (optional): The Minimum Number of consecutive 0 slope points to be considered
      a Stimulation
    
      Channel (optional): The Channel in which you search for stimulations
    
    Outputs
    
        StimStartStopIndex: Index of Stimulation Group Start and End Points
        StimLengths: Length of each Stimulation Group measured in Samples(1/250 s)
        stats
          MaxStimLength: Longest Stimulation Group Length in Samples
          MinStimLength: Minimum Stimulation Group length in Samples
          MaxStimIndex: Index of longest stimulation Group
          MinStimIndex: Index of shortest stimulation Group
          NumStims: The number of smaller stimulations per stim group
    
      Arjun Ravi Shankar
      Litt Lab July 2018
    
      Updated Brittany Scheid (bscheid@seas.upenn.edu) & Kenji Aono Aug 2022
      '''
 

    AllData = AllData+512; # Make sure it is all positive
    
    if not AllData.shape[0] == 4:
        AllData = AllData.T 
    
    
    ## Find Stimulation Triggers
    
    # Find Slope of Data
    Slope = np.diff(AllData,1,1)
    Slope[:, ecogT['Event Start idx']-1] = 1;
    
    # Correct for max and min flatlines and analog to digital conversion
    # artifacts: Set slope to 1 if hits lower or upper rails for < "Min" samples
    
    SSI_all = []; 
    
    for Channel in range(0,4):
    
        Slope[Channel, np.where(runInds(AllData[Channel,:]<100, Min))] = 1
        Slope[Channel, np.where(runInds(AllData[Channel,:]>900, Min))] = 1
        
        # Find Start and End Locations of Regions with Zero Slope 
        ZeroSlopeInflections = np.diff((Slope[Channel,:]==0).astype(int));
        ZeroSlopeStarts = np.where(ZeroSlopeInflections==1)[0] + 1 
        ZeroSlopeEnds = np.where(ZeroSlopeInflections==-1)[0] + 1
        
        # If more starts then ends, ignore last one
        if ZeroSlopeEnds[-1] < ZeroSlopeStarts[-1]:
            ZeroSlopeStarts = ZeroSlopeStarts[0:-2]
        
        # Find Indices of Stimulation Start and End Points
        SSI_start = ZeroSlopeStarts[ZeroSlopeEnds-ZeroSlopeStarts>=Min]
        SSI_end = ZeroSlopeEnds[ZeroSlopeEnds-ZeroSlopeStarts>=Min]
        
        
        st = np.vstack((SSI_start, np.ones((len(SSI_start)))))
        end = np.vstack((SSI_end, -1*np.ones((len(SSI_end)))))
        
        np.concatenate((SSI_all, st,end), 1)
        
        SSI_all = [SSI_all;...
            [SSI_start, np.ones((len(SSI_start),1))];...
            [SSI_end, -1*np.ones((len(SSI_end),1))]];
        
        np.concatenate([SSI_all],  [SSI_start, np.ones((len(SSI_start),1))])
        
        print('%d/4 '%Channel)
        
        
    # Get union of stims across at least 3 channels:
    srted = sortrows(SSI_all, 1);
    ivl_count = np.cumsum(srted[:,2]);
    is2 = find(ivl_count == 2); 
    
    i_ivl_starts = is2(ivl_count(is2+1)==3);
    i_ivl_ends = is2(ivl_count(is2-1)==3);
    
    SSI_start = srted(i_ivl_starts,1);
    SSI_end = srted(i_ivl_ends,1);
    
    print('\n')
    
    
    # Correct for Double Stimulation or low-frequency stim conditions
    # Don't merge if start and ends are on different sides of a start index
    
    StimGap = SSI_start[1:]-SSI_end[0:-2];
    
    incl = filterWindows([SSI_end[0:-2],SSI_start[1:]], ecogT.EventStartIdx);
    i_gp = find(StimGap<100 & ~incl);
    SSI_start[i_gp+1]= []; 
    SSI_end[i_gp]= []; 
    
    
    StimStartStopIndex = np.vstack[SSI_start, SSI_end];

    
    ## Statistics
    
    stats = struct(); 
    # Find Stimulation Lengths
    stats.StimLengths= diff(StimStartStopIndex,[],2);
    
    # Find Max Stim Length
    stats.MaxStimLength=max(stats.StimLengths);
    stats.MaxStimIndex=find(stats.StimLengths==stats.MaxStimLength);
    
    # Find Min Stim Length
    stats.MinStimLength=min(stats.StimLengths);
    stats.MinStimIndex=find(stats.StimLengths==stats.MinStimLength);
    
    ## Plot Statistics
    
    # Plot Histogram of Stimulation Lengths
    if show:
        figure()
        histogram(stats.StimLengths)
        title('Histogram of Stimulation Lengths')
        xlabel('Lengths of Stimulation')
        ylabel('Occurences')
    
    
    return stimStartStopIndex, stats



def runInds(q,maxRun):
    ''' 
    given a binary input vector, returns a binary mask with 1 at
    locations of consecutive runs of ones less than "maxRun" in length
    '''

    padded = np.concatenate(([0], q, [0]))
    s = np.diff(padded)
    iboth = np.where(abs(s) == 1)[0]
    i_beg = iboth[0::2]
    i_end = iboth[1::2]
    gp_sz =  i_end - i_beg;
   
    indOut = np.full(len(q), False, dtype=bool);
    for i_g in np.where(gp_sz < maxRun)[0]:
        indOut[i_beg[i_g]:i_end[i_g]] = True
        
    return indOut
   

if __name__ == "__main__":
    
    with open('../../config.JSON') as f:
        config= json.load(f)
    
    pt = 'HUP153'
    dataPath = os.path.join(config['paths']['RNS_DATA_Folder'], pt)
    data = hdf5storage.loadmat(os.path.join(dataPath, 'Device_Data.mat'))
   
    ecogT = pd.read_csv(os.path.join(dataPath, 'ECoG_Catalog.csv'))
    AllData = data['AllData'];     

    #[StimIndex, stats] = findStim(AllData, ecogT)
    
