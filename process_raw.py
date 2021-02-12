#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
% process_raw script
% ------------------------------------------------------
% Download new files from box, deidentify, aggregate .dat data
% ------------------------------------------------------

Created on Wed Sep 16 16:43:22 2020

@author: bscheid
"""

from boxsdk import Client, OAuth2
import json
import os
import numpy as np
import pandas as pd
from rns_py_tools import NPDataHandler as npdh


def downloadPatientDataFromBox(config):
    
    auth = OAuth2(
        client_id= config['boxKeys']['CLIENT_ID'],
        client_secret= config['boxKeys']['CLIENT_SECRET'],
        access_token= config['boxKeys']['CLIENT_ACCESS_TOKEN']
    )

    client = Client(auth)
    
    folderID= config['boxKeys']['Folder_ID']
    dataPath = config['paths']['RNS_RAW_Folder']
    
    npdh.NPdownloadNewBoxData(folderID, dataPath, client)
    
    return
    

def loadDeviceDataFromFiles(config):
    
    ptList = [p['ID'] for p in config['patients']]

    for ptID in ptList:
       
       print('loading data for patient %s ...'%ptID)
      
       dataFolder = npdh.NPgetDataPath(ptID, config, 'Dat Folder')
       catalog_csv= npdh.NPgetDataPath(ptID, config, 'ECoG Catalog')
                                 
       savepath = os.path.join(config['paths']['RNS_DATA_Folder'], ptID, 'py_dat');
       
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
       
       
def createDeidentifiedFiles(config):
        
    ptList = [p['ID'] for p in config['patients']]
    
    for ptID in ptList:
        print('Creating deidentified files for %s'%ptID)
        npdh.NPdeidentifier(ptID, config)
        
        
      
if __name__ == "__main__":
   
    with open('./config.JSON') as f:
        config= json.load(f); 
    
    if not os.path.exists(config['paths']['RNS_DATA_Folder']):
        os.makedirs(config['paths']['RNS_DATA_Folder'])
    
    # Download latest data from Box
    x = input('Download new data from Box drive (y/n)?: ')
    if x =='y': 
        downloadPatientDataFromBox(config)
    
    # Create Deidentified copies of files
    x = input('Populate RNS Data folder with deidentified NeuroPace files (y/n)?: ')
    if x =='y':     
        createDeidentifiedFiles(config)
    
    # Create readable device recording objects
    x = input('Aggregate NeuroPace device recordings (y/n)?: ')
    if x =='y': 
        loadDeviceDataFromFiles(config)
    
