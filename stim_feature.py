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
import numpy as np
import pandas as pd
from rns_py_tools import ecog, visualize

with open('./config.JSON') as f:
    config= json.load(f); 
    
pdata = np.load('/Users/bscheid/Desktop/RNS015.npz', allow_pickle=True)
AllData = pdata['AllData']
AllTime = pdata['AllTime'].astype(int)
Ecog_Events = pd.read_csv('/Users/bscheid/Desktop/RNS015_Ecog.csv');
[StimIdx, StimTime, stimStats] = ecog.findStims(AllData, AllTime)


stimGroups = ecog.getStimGroups(StimIdx, StimTime)

# Get indices of all scheduled events
sched_idx = ecog.getEventIdx(AllData, Ecog_Events, 'Scheduled')

# Find scheduled events with stimulations in them
overlap= ecog.getIntersectingIntervals(sched_idx, StimIdx)


st_sched= sched_idx[overlap[0]].T[0]

visualize.vis_event(AllData, AllTime, Ecog_Events, sched_idx[161:164,0]+1)


