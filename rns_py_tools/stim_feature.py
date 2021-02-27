#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
% window feature
% ------------------------------------------------------
% Convert .DAT files to .py files, place in MAT_Folder
% ------------------------------------------------------

% load configuration settings

Created on Wed Sep 16 16:43:22 2020

@author: bscheid
"""
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from functions import ecog, visualize, utils

with open('../config.JSON') as f:
    config= json.load(f);
    paths = config['paths']
    
    
def ft_pipeline(ptID):
    
    pdata = np.load(os.path.join(paths['RNS_DATA_Folder'], ptID,'%s.npz'%ptID), allow_pickle=True)
    AllData = pdata['AllData']
    AllTime = pdata['AllTime'].astype(int)
    Ecog_Events = pd.read_csv(os.path.join(paths['RNS_DATA_Folder'], ptID, '%s_Ecog.csv'%ptID));
    [StimIdx, StimTime, stimStats] = ecog.findStims(AllData, AllTime)
    
    
    stimGroups = ecog.getStimGroups(StimIdx, StimTime)
    
    # Get indices of all scheduled events
    sched_idx = ecog.getEventIdx(AllData, Ecog_Events, 'Scheduled')
    
    # Find scheduled events with stimulations in them
    overlap= ecog.getIntersectingIntervals(sched_idx, StimIdx)
    
    
    st_sched= sched_idx[overlap[0]].T[0]
    visualize.vis_event(AllData, AllTime, Ecog_Events, sched_idx[161:164,0]+1)
    
    

def align_histograms():
    
    npts = 5
    
    for i_pt in range(0,npts):
        csvFile = utils.histPath(i_pt, config)
        hourly = pd.read_csv(csvFile)
    
        plt.plot(hourly['UTC start time'], hourly['Episode starts'])





