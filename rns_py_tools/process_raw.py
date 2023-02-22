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

#%%

import json
import os
import sys
import pandas as pd
import hdf5storage
import traceback
from datetime import datetime
sys.path.insert(1,os.getcwd())
from functions import NPDataHandler as npdh
from functions import utils
import logging

#%%

def downloadPatientDataFromBox(ptList, config):
    
    from boxsdk import Client, OAuth2
    
    auth = OAuth2(
        client_id= config['boxKeys']['CLIENT_ID'],
        client_secret= config['boxKeys']['CLIENT_SECRET'],
        access_token= config['boxKeys']['CLIENT_ACCESS_TOKEN']
    )

    client = Client(auth)

    for ptID in ptList:
        npdh.NPdownloadNewBoxData(ptID, config, client)
    
    return


#%% 

def update_config_dataRange(ptList, config):

    for ptID in ptList:

        catalog_csv = utils.getDataPath(ptID, config, 'ecog catalog')
        if not os.path.exists(catalog_csv):
            print('Ecog path not found for %s, skipping...'%ptID)
            continue
        ecog_df = pd.read_csv(catalog_csv)
        idx = utils.ptIdxLookup(config, 'ID', ptID)

        data_start = ecog_df['Raw UTC timestamp'].iloc[0]
        data_end = ecog_df['Raw UTC timestamp'].iloc[-1]
        config['patients'][idx]['UTC_date_range'] = [data_start, data_end]

    return config


#%%
    
def loadDeviceDataFromFiles(ptList, config):

    errlist= []
    
    for ptID in ptList:
        
       try:
           
           # Create deidentified versions of csv files
           logging.info('Creating deidentified files for %s'%ptID)
           npdh.NPdeidentifier(ptID, config)

           logging.info('loading data for patient %s ...'%ptID)
          
           savepath = os.path.join(config['paths']['RNS_DATA_Folder'], ptID);
           
           # Get converted Data and Time vectors 
           [AllData, eventIdx, dneIdx] = npdh.NPdat2mat(ptID, config)
        
           #Update (and deidentify) ECoG Catalog:
           catalog_csv= npdh.NPgetDataPath(ptID, config, 'ECoG Catalog')
           Ecog_Events = pd.read_csv(catalog_csv);
           
           # Remove rows that don't have an associated .dat file
           if dneIdx:
               Ecog_Events.drop(index=dneIdx, inplace=True)
               Ecog_Events.reset_index(drop=True, inplace=True)
               logging.info('Removing %d entries from deidentified ECoG_Catalog.csv due to missing data'%(len(dneIdx)))
    
           Ecog_Events = Ecog_Events.drop(columns=['Initials', 'Device ID'])
           Ecog_Events['Patient ID']= ptID
           
           # Add event index to ecog_events file, add +1 for matlab 1-indexing
           Ecog_Events['Event Start idx'] = [row[0]+1 for row in eventIdx]; 
           Ecog_Events['Event End idx'] = [row[1]+1 for row in eventIdx];
           
                  # Save updated csv and all events
           Ecog_Events.to_csv(os.path.join(savepath,'ECoG_Catalog.csv'), index=False)
           
           hdf5storage.savemat(os.path.join(savepath, 'Device_Data.mat'), {"AllData": AllData, "EventIdx":eventIdx}, 
                               format ='7.3', oned_as='column', store_python_metadata=True)
        
           print('complete')
       
       except:
           logging.error('ERROR: %s catalog annotation failed'%ptID)
           logging.error(traceback.format_exc())
           errlist.append(ptID)
           pass
       
       if errlist:
            logging.warning('ERROR SUMMARY: load data failed for %s'%errlist)
       
                      

if __name__ == "__main__":
    """ Usage: python process_raw.py ../config.JSON HUPxyz"""
   
    if len(sys.argv)>1:
        confName = sys.argv[1]
    else:
        confName = '../config.JSON'

    with open(confName) as f:
        config= json.load(f)

    if len(sys.argv)>2:
        ptList = [sys.argv[2]]
    else:
        ptList = [pt['ID'] for pt in config['patients']]
    
    # Set up logging
    logfile = os.path.join(config['paths']['RNS_RAW_Folder'],'raw_processing.log');
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    FORMAT = '%(asctime)s %(funcName)s: %(message)s'
    logging.basicConfig(filename=logfile, level=logging.INFO, format=FORMAT)
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)


    logging.info('Running process_raw.py pipeline with patient list: %s \n'%ptList)
    
    if not os.path.exists(config['paths']['RNS_DATA_Folder']):
        os.makedirs(config['paths']['RNS_DATA_Folder'])
    
    # Download latest data from Box
    if config['boxKeys']['CLIENT_ACCESS_TOKEN']:
        x = input('Download new data from Box using sdk (y/n)?: ')
        if x =='y': 
            downloadPatientDataFromBox(ptList, config)
    else:
        print('NOTE: BoxKey ACCESS TOKEN not in config. The ACCESS TOKEN must be ' +
              'specified if using the Box SDK to download raw data. Otherwise,' +
              ' raw data can be downloaded if RNS_RAW_FOLDER can be accessed locally.\n')
                
    # Create Deidentified copies of files
    x = input('Populate RNS Data folder with deidentified NeuroPace files (y/n)?: ')
    if x =='y':
       
        # Create Backup config file with former start/end dates
        json_object = json.dumps(config, indent=4)
        fname = os.path.join(os.path.dirname(confName),
         'config_backup_%s.JSON'%datetime.today().strftime('%S%M%H%d%m%Y'))
        with open(fname, "w") as outfile:
            outfile.write(json_object)  

        loadDeviceDataFromFiles(ptList, config)

        # Update current config with new dataRanges
        update_config_dataRange(ptList, config)
        json_object = json.dumps(config, indent=4)
        with open(os.path.join(confName), "w") as outfile:
            outfile.write(json_object)  
    