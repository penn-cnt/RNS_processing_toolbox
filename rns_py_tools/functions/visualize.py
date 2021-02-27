#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualization
(RNS Processing Toolbox)

Functions in this file: 
    vis_event(AllData, AllTime, Ecog_Events, datapoints)
    
"""
import matplotlib.pyplot as plt
import numpy as np
from functions import utils

def vis_event(AllData, AllTime, Ecog_Events, datapoints):
    '''
    Args:
        AllData (npArray): patient's AllData array
        AllTime (npArray): patient's AllTime array
        Ecog_Events (table): patient's Ecog_Events table
        datapoints (list): vector of AllTime indices to plot

    Returns:
        ax (plot.axis): subplot including one plot of the EcoG event containing 
        each datapoint, respectively. 
    '''
    
    try:
        dlen = len(datapoints)
    except TypeError:
        dlen = 1
    
    # If datapoints are indices
    start= Ecog_Events['Event Start idx']
    end= Ecog_Events['Event End idx']
    
    ievent = [np.argmax(np.where((start-datapoints[i])<0)) for i in range(0,dlen)]
    
    fig, ax= plt.subplots(dlen, 1, squeeze=False)
    fig.subplots_adjust(hspace= 0.5)    
    
    for i in range(0,dlen):
        idx= ievent[i]
        dt= utils.posix2dt_UTC(AllTime[start[idx]:end[idx]+1])
        dat = AllData[:,start[idx]:end[idx]+1].T+np.arange(4)*100
        
        ymax = max([i for lis in dat for i in lis])
        ymin = min([i for lis in dat for i in lis])
        
        ax[i][0].plot(dt, dat)
        ax[i][0].vlines(utils.posix2dt_UTC(AllTime[datapoints[i]]),ymin, ymax)
        plt.sca(ax[i][0])
        plt.xticks(rotation=20)
        plt.title("%s Event"%(Ecog_Events['ECoG trigger'][idx]))
    
    return ax
    