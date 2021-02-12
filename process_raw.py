#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
% process_raw script
% ------------------------------------------------------
% Convert .DAT files to .MAT files, place in MAT_Folder
% ------------------------------------------------------

% load configuration settings

Created on Wed Sep 16 16:43:22 2020

@author: bscheid
"""

import json
import os
import numpy as np
import pandas as pd
from rns_py_tools import conversion as cnv
from rns_py_tools import NPDataHandler as npdh


with open('./config.JSON') as f:
    config= json.load(f); 


if not os.path.exists(config['paths']['RNS_DATA_Folder']):
   os.makedirs(config['paths']['RNS_DATA_Folder'])
    
npts = len(config['patients'])

def loadPatientDataFromFiles():

    for i_pt in range(0,npts):

       ptID =  config['patients'][i_pt]['ID']
       
       print('loading data for patient %s ...'%ptID)
      
       dataFolder = npdh.NPgetDataPath(ptID, config, 'Dat Folder')
       catalog_csv= npdh.NPgetDataPath(ptID, config, 'ECoG Catalog')
                                 
       savepath = os.path.join(config['paths']['RNS_DATA_Folder'], '%s'%config['patients'][i_pt]['RNS_ID']);
       
       # Get converted Data and Time vectors 
       [AllData, AllTime, eventIdx]= npdh.dat2vector(dataFolder, catalog_csv);
    
       #Add in additional metadata
       Ecog_Events = pd.read_csv(catalog_csv);
       Ecog_Events = Ecog_Events.drop(columns=['Initials', 'Patient ID', 'Device ID'])
       Ecog_Events['Event Start idx'] = [row[0] for row in eventIdx]; 
       Ecog_Events['Event End idx'] = [row[1] for row in eventIdx];
       
       # Save updated csv and all events
       Ecog_Events.to_csv(savepath+'_Ecog.csv', index=False)
       np.savez_compressed(savepath, AllData=AllData, AllTime=AllTime, eventIdx=eventIdx)
    
       print('complete')
       
 
loadPatientDataFromFiles()       

   
   
    
