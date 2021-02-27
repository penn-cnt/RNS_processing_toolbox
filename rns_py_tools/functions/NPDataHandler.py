# -*- coding: utf-8 -*-
"""
NPDataHandler
(RNS Processing Toolbox)

Purpose: Functions associated with handling raw NeuroPace data downloads, including 
filetype conversion, and file deidentification. 

Functions in this file:
    NPdownloadNewBoxData
    NPdeidentifier
    NPdat2vector(dataFolder, catalog_csv)
    NPgetDataPath
    NPdat2mef
    
    helper functions

"""

import glob
import numpy as np
import pandas as pd
import sys
import re
import datetime as DT
import os
from os import path as pth
from functions import utils as utils

import jpype
import jpype.imports


# Launch the JVM
if not jpype.isJVMStarted():
    jpype.startJVM(classpath=['../lib/MEF_writer.jar'])
    
from edu.mayo.msel.mefwriter import MefWriter

# Constants
NUM_CHANNELS = 4
SAMPLING_RATE = 250


def NPdownloadNewBoxData(ptID, config, client):
    '''
    Download new NeuroPace data from Box.com

    Args:
        folderID (str): id of root box folder (can be found in box folder URL)
        path (str): DESCRIPTION.
        client (OAuth2): DESCRIPTION.

    Returns:
        None.

    '''

    folderID= config['boxKeys']['Folder_ID']
    path = config['paths']['RNS_RAW_Folder']
    
    ptFolders = client.folder(folder_id=folderID).get_items()

    rt = pth.basename(NPgetDataPath(ptID, config, 'root folder'))
    ptFolder = [i for i in ptFolders if i.name == rt][0]
    
    print('Updating %s...'%ptFolder.name)
    fpath= os.path.join(path, ptFolder.name)
        
    if not os.path.exists(fpath):
        _downloadAll(ptFolder.id, path, 0, client)
    else:
        
        # Download the CSV catalog and read into variable
        pat = re.compile('.*ECoG_Catalog.csv')
        try:
            ecog_catalog =[item for item in ptFolder.get_items() if pat.match(item.name)][0]
            output_file = open(os.path.join(fpath, ecog_catalog.name), 'wb')
            client.file(file_id=ecog_catalog.id).download_to(output_file)
            output_file.close()
            print('     Ecog_Catalog updated')
        except IndexError:
            print('ECoG_Catalog.csv missing in %s'%(ptFolder.name))
            return
        
        # Download the Histograms
        try: 
            rh = re.compile('.*Histograms*')
            hist_folder =[item for item in ptFolder.get_items() if rh.match(item.name)][0]
            _downloadAll(hist_folder.id, fpath, 0, client)
            print('     Histograms updated')
        except IndexError:
            print('Histogram Folder missing in %s'%(ptFolder.name))
            pass
            
        # Download new Episode Durations files from box that are not local 
        _helper_downloadNew('.*EpisodeDurations*', ptFolder, fpath, client)
        print('     Episode Durations updated')

        # Download new Data files from box that are not local 
        _helper_downloadNew('.*Data*', ptFolder, fpath, client)
        print('     Dat files updated')


def NPdeidentifier(ptID, config):
    ''' Note, this will overwrite the ecog_catalog and may cause it to lose the
    Index values. Maybe we should require user input to confirm '''
    
    np_ecog_catalog = NPgetDataPath(ptID, config, 'ecog catalog' );
    np_daily_histogram = NPgetDataPath(ptID, config, 'daily histogram');
    np_hourly_histogram = NPgetDataPath(ptID, config, 'hourly histogram' );
    np_episodes_folder = NPgetDataPath(ptID, config, 'episode durations folder');
    
    targ_pth = pth.join(config['paths']['RNS_DATA_Folder'],ptID)
    if not os.path.exists(targ_pth):
        os.makedirs(targ_pth)
    
    # Create Deidentified ECoG Catalog
    ecog_df = pd.read_csv(np_ecog_catalog)
    ecog_df= ecog_df.drop(columns=['Initials', 'Device ID'])
    ecog_df['Patient ID']= ptID
    ecog_df.to_csv(pth.join(targ_pth, 'ECoG_Catalog.csv'), index = False)
    
    # Create Deidentified histograms
    if not os.path.exists(pth.join(targ_pth, 'Histograms')):
        os.makedirs(pth.join(targ_pth, 'Histograms'))

    daily_hist_df = pd.read_csv(np_daily_histogram)
    daily_hist_df= daily_hist_df.drop(columns=['Device ID'])
    daily_hist_df['Patient ID']= ptID
    daily_hist_df.to_csv(pth.join(targ_pth, 'Histograms', 'Histogram_Daily.csv'), index = False)
    
    hourly_hist_df = pd.read_csv(np_hourly_histogram)
    hourly_hist_df= hourly_hist_df.drop(columns=['Device ID'])
    hourly_hist_df['Patient ID']= ptID
    hourly_hist_df.to_csv(pth.join(targ_pth, 'Histograms', 'Histogram_Hourly.csv'), index = False)
    
    
    # Create Deidentified EpisodeDurations
    if not os.path.exists(pth.join(targ_pth, 'EpisodeDurations')):
        os.makedirs(pth.join(targ_pth, 'EpisodeDurations'))
        
    epth= glob.glob(pth.join(np_episodes_folder, '*.csv'));
    for epdur in epth:
        
        ename = pth.basename(epdur).split('_')[3:]
        ename.insert(0,ptID)
        ename = '_'.join(ename)
        
        epdur_df = pd.read_csv(epdur)
        epdur_df= epdur_df.drop(columns=['Device ID'])
        epdur_df['Patient ID']= ptID
        epdur_df.to_csv(pth.join(targ_pth, 'EpisodeDurations', ename), index = False)
    
    return None
    
    
def NPgetDataPath(ptID, config, NPDataName):
    '''
    Returns path to NeuroPace files or folders
    
    Args:
        ptID (string): Patient ID
        config (dict): config.json dictionary 
        NPDataName (str): NeuroPace File or Folder name (case insensitive)
            possible file/folder names 
           * Root Folder
           * Ecog Catalog
           * Dat Folder
           * Daily Histogram
           * Hourly Histogram
           * Episode Durations Folder
            
    Returns:
        string: path to NeuroPace data file or folder
    '''
    
    ptnum = utils.ptIdxLookup(config, 'ID', ptID)
    prefix = '%s_%s_%s'%(config['institution'], 
                         config['patients'][ptnum]['Initials'],
                         config['patients'][ptnum]['PDMS_ID'])
    
    fld = pth.join(config['paths']['RNS_RAW_Folder'], prefix + ' EXTERNAL #PHI')
    
    switcher = {
        'root folder':      fld,
        'ecog catalog':     pth.join(fld, prefix + '_ECoG_Catalog.csv'),
        'hourly histogram': pth.join(fld, prefix + ' Histograms EXTERNAL #PHI', prefix + '_Histogram_Hourly.csv'),
        'daily histogram':  pth.join(fld, prefix + ' Histograms EXTERNAL #PHI', prefix + '_Histogram_Daily.csv'),
        'dat folder':       pth.join(fld, prefix + ' Data EXTERNAL #PHI'),
        'episode durations folder': pth.join(fld, prefix + ' EpisodeDurations EXTERNAL #PHI')
            }
    
    return switcher.get(NPDataName.lower(), "File/Folder not found")


def NPdat2mat(ptID, config):
    
    dataFolder = NPgetDataPath(ptID, config, 'Dat Folder')
    catalog_csv = NPgetDataPath(ptID, config, 'ECoG Catalog')

    NumberOfFiles = len(glob.glob(pth.join(dataFolder, "*.dat")));
    
    ecog_df= pd.read_csv(catalog_csv)
    ecog_df= ecog_df.drop(columns=['Initials', 'Device ID'])
    ecog_df['Patient ID']= ptID

    _checkDatFolderEcogConcordance(ecog_df, NumberOfFiles)

    ctr = 0
    
    AllData = []
    eventIdx = []
    dneIdx = []
    
    for i_file in range(0,ecog_df.shape[0]):
            
        try:
            [fdata, ftime, t_conversion_usec] = _readDatFile(dataFolder, ecog_df[i_file:i_file+1])
            dlen = fdata.shape[1]
            AllData.append(fdata)
            eventIdx.append(ctr + np.array([0,dlen-1]))
            ctr = ctr + dlen
            
        except (FileNotFoundError):
            print('File %s not found'%(ecog_df['Filename'][i_file]))
            dneIdx.append(i_file)
            

    AllData = np.concatenate(AllData, axis = 1)
    AllData = AllData.astype('int16').T
    eventIdx = np.array(eventIdx)
    eventIdx = eventIdx.astype('int32')

    assert eventIdx.shape[0] == ecog_df.shape[0]-len(dneIdx)

    return AllData, eventIdx, dneIdx


def NPdat2mef(ptID, config):
    
    dataFolder = NPgetDataPath(ptID, config, 'Dat Folder')
    catalog_csv = NPgetDataPath(ptID, config, 'ECoG Catalog')
    
    NumberOfFiles = len(glob.glob(pth.join(dataFolder, "*.dat")));
    ecog_df= pd.read_csv(catalog_csv)

    _checkDatFolderEcogConcordance(ecog_df, NumberOfFiles)
    
    inst = config['institution']
    dpath = pth.join(config['paths']['RNS_DATA_Folder'], ptID, 'mefs/')
    gain = 1; 
 
    for i_file in range(0,ecog_df.shape[0]):
        
        fname= ecog_df['Filename'][i_file][0:-4]
        
        try:
            
            [fdata, ftime, t_conversion_usec] = _readDatFile(dataFolder, ecog_df[i_file:i_file+1])
        
            # Create mef subfolder, skip creation if mef folder already exists
            if pth.isdir(pth.join(dpath, fname)):
                continue
           
            os.mkdir(pth.join(dpath, fname))
                  
            blockSize = round(4000/SAMPLING_RATE)
            th = 100000
            
            for i_chan in range(0,NUM_CHANNELS):
                
                chanLabel= '%s_C%d.mef'%(ptID, i_chan+1)
                
                print(fdata[i_chan][:])
                
                mw = MefWriter(pth.join(dpath, fname, chanLabel), blockSize, SAMPLING_RATE, th)
                mw.writeData((fdata[i_chan][:]).astype(int), ftime.astype('l'), fdata.shape[1])
                mw.setInstitution(inst);
                mw.setSubjectID(ptID);
                mw.setChannelName(chanLabel[0:-4]);
                mw.setVoltageConversionFactor(gain);
                mw.close()  
                
        except(FileNotFoundError):
            print('File %s not found'%(ecog_df['Filename'][i_file]))
            continue
        
    return None

#### Helper Functions #####

def _helper_downloadNew(folder_keyword, parent_folder_box, fpath, client):
        
   pat = re.compile(folder_keyword)
   box_fold= [item for item in parent_folder_box.get_items() if pat.match(item.name)][0]
   box_filenames =  [i.name for i in box_fold.get_items()]
    
   try:
        local_fold = [item for item in os.listdir(fpath) if pat.match(item)][0]
        local_filenames = os.listdir(os.path.join(fpath, local_fold))
        
        download_inds = [i for i, x in enumerate(box_filenames) if x not in local_filenames]
        ids = [i.id for i in box_fold.get_items()]
        
        print('Downloading %s new files to %s'%(len(download_inds), local_fold))
        
        for ind in download_inds:
            output_file= open(os.path.join(fpath, box_fold.name, box_filenames[ind]), 'wb')
            client.file(file_id=ids[ind]).download_to(output_file)
            output_file.close()
    
   except (IndexError, FileNotFoundError):
       print('Local folder %s not found, downloading all'%(box_fold.name))
       _downloadAll(box_fold.id, fpath, 0)
       pass
            
   return

# recursively download all NeuroPace files in boxFolder
def _downloadAll(folderID, path, ctr, client):
    """ folderID: box folder ID
        path: path where folder should be downloaded (don't include name of folder being downloaded
        ctr: used to print progress
    """          
                        
    folder = client.folder(folder_id=folderID).get()
    items = client.folder(folder_id=folderID).get_items()

    if not os.path.exists(os.path.join(path, folder.name)):
        os.makedirs(os.path.join(path, folder.name))
        

    # mkdir folder name
    for item in items:
        # If item is a folder
        if item.type == 'folder':
            print(item.name)
            _downloadAll(item.id, os.path.join(path, folder.name), ctr)
        # output_file = open('file.pdf', 'wb')
        elif item.type == 'file':
            if item.name[0] == '.':
                continue
            ctr = ctr+1
            if ctr%20 == 0:
                print('Downloading' + pth.join(path, folder.name, item.name) + 'ctr %d'%ctr)
            output_file = open(pth.join(path, folder.name, item.name), 'wb')
            client.file(file_id=item.id).download_to(output_file)
            output_file.close()


def _checkDatFolderEcogConcordance(ecog_df, NumberOfFiles):
    ''' Check for inconsistencies between files in dat folder and entries in ecog_df'''
    
    ecog_df['Raw UTC timestamp'] = pd.to_datetime(ecog_df['Raw UTC timestamp'], format= '%Y-%m-%d %H:%M:%S.%f')
    
    if ecog_df.shape[0] != NumberOfFiles:
        print("Warning: mismatched number of.dat files (%d) and ECoG catalog length (%d)"%
            (NumberOfFiles, ecog_df.shape[0]))
    
    if len(np.unique(ecog_df['Sampling rate'])) > 1:
        sys.exit("Error: Multiple SamplingRates in file")
        
    if not (ecog_df['Sampling rate'][0] == SAMPLING_RATE):
         sys.exit("Error: Unexpected sampling rate")
        
    if sum(n < np.timedelta64(0) for n in np.diff(ecog_df['Raw UTC timestamp'])) > 0:
        sys.exit("Error: RawUTCTimestamp is not chronological")
        
        
def _readDatFile(dataFolderPath, ecog_df):

    # Open up dat_file
    dat_file = pth.join(dataFolderPath, ecog_df['Filename'].item())
    fs = ecog_df['Sampling rate'].item()
    
    enabled = (ecog_df[['Ch 1 enabled', 'Ch 2 enabled', 
                        'Ch 3 enabled', 'Ch 4 enabled']] == 'On').values.tolist()[0]

    num_channels = sum(enabled)
       
    # Note, 512 is mid-rail
    with open(dat_file, 'rb') as fid:
        fdata = np.fromfile(fid, np.int16).reshape((-1, num_channels)).T-512
    

    # Pad with zeros in each channel of fdata array if channel is "OFF"
    # Note, ideally this would be Nan but python doesn't support Nan integers....
    off_chans = [i for i, x in enumerate(enabled) if x == False]
    for oc in off_chans:
        fdata = np.insert(fdata, oc, 0, axis=0)
        
    # Get UTC and local trigger times, and timestamp as strings. 
    if isinstance(ecog_df['Raw UTC timestamp'].item(),DT.datetime):
        raw_UTC_str = ecog_df['Raw UTC timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S.%f").item()
    else: 
        raw_UTC_str = ecog_df['Raw UTC timestamp'].item()
        
    if isinstance(ecog_df['Raw local timestamp'].item(), DT.datetime):
        raw_local_str = ecog_df['Raw local timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S.%f").item()
    else: 
        raw_local_str = ecog_df['Raw local timestamp'].item()
        
    if isinstance(ecog_df['Timestamp'].item(), DT.datetime):
        timestamp_str = ecog_df['Timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S.%f").item()
    else: 
        timestamp_str = ecog_df['Timestamp'].item()
        
        
    # Calculate associated time vector    
    dlen = fdata.shape[1]
    t_vec = np.arange(dlen)/fs*10**6
    t_trigger_UTC = utils.str2dt_usec(raw_UTC_str)
    t_trigger_local = utils.str2dt_usec(raw_local_str)
    t_conversion_usec = t_trigger_UTC - t_trigger_local
    t_start = utils.str2dt_usec(timestamp_str) + t_conversion_usec 
    
    
    ftime = t_start + t_vec
    
    return fdata, ftime, t_conversion_usec
    

    