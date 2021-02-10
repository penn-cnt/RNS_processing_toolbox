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
from rns_py_tools import conversion as cnv

def vis_event(AllData, AllTime, Ecog_Events, datapoints):
    
    dlen = len(datapoints)
    
    # If datapoints are indices
    start= Ecog_Events['Event Start idx']
    end= Ecog_Events['Event End idx']
    
    ievent = [np.argmax(np.where((start-datapoints[i])<0)) for i in range(0,dlen)]
    
    fig, ax= plt.subplots(dlen,1)
    fig.subplots_adjust(hspace=0.5)    
    
    for i in range(0,dlen):
        idx= ievent[i]
        dt= cnv.posix2dt_UTC(AllTime[start[idx]:end[idx]+1])
        
        
        ax[i+1].plot(dt, AllData[:,start[idx]:end[idx]+1].T+np.arange(4)*100)
        ax[i+1].vlines(cnv.posix2dt_UTC[idx])
        ax[i+1].xticks(rotation=45)
        ax[i+1].title('%s Event'%Ecog_Events['ECoG trigger'][idx])
    
    return ax
    