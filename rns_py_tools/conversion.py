# -*- coding: utf-8 -*-
"""
Conversion Tools
(RNS Processing Toolbox)

Functions in this file: 
    dat2vector(dataFolder, catalog_csv)
    str2dt_usec(s)
    posix2dt_UTC(psx)

"""
import glob
import sys
import os
import numpy as np
import pandas as pd

import datetime as DT



def str2dt_usec(s):
	dt=DT.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f")
	EPOCH = DT.datetime(1970,1,1)
	return int((dt - EPOCH).total_seconds() * 1000000)


def posix2dt_UTC(psx):
    psx = psx*10**-6
    if psx.shape == ():
        return DT.datetime.utcfromtimestamp(psx)
    utc= [DT.datetime.utcfromtimestamp(x) for x in psx]
    return utc
 

def ptIdxLookup(config, ID_field, ID):
    '''
    Look up patient idex in config based on patient ID

    Args:
        config (dict): config.json object
        ID_field (string): field type to match
        ID (string): patient ID

    Returns:
        patient index
    '''
    
    ids = [f[ID_field] for f in config['patients']]
    return ids.index(ID)



    
    
