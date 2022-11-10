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
from pandas import DateOffset
import sys
import re
import datetime as DT
import os
import logging
from os import path as pth
from functions import utils as utils

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
    
    logging.info('Updating %s...'%ptFolder.name)
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
            logging.info('     Ecog_Catalog updated')
        except IndexError:
            logging.error('ECoG_Catalog.csv missing in %s'%(ptFolder.name))
            return
        
        # Download the Histograms
        try: 
            rh = re.compile('.*Histograms*')
            hist_folder =[item for item in ptFolder.get_items() if rh.match(item.name)][0]
            _downloadAll(hist_folder.id, fpath, 0, client)
            logging.info('     Histograms updated')
        except IndexError:
            logging.warning('Histogram Folder missing in %s'%(ptFolder.name))
            pass
            
        # Download new Episode Durations files from box that are not local 
        try:
            _helper_downloadNew('.*EpisodeDurations*', ptFolder, fpath, client)
            logging.info('     Episode Durations updated')
        except IndexError:
            logging.warning('Episode Durations missing in %s'%(ptFolder.name))
        

        # Download new Data files from box that are not local 
        _helper_downloadNew('.*Data*', ptFolder, fpath, client)
        logging.info('     Dat files updated')


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
    ecog_df= ecog_df.drop(columns=['Initials'])
    ecog_df['Device ID']= ecog_df.groupby('Device ID').ngroup()+1
    ecog_df['Patient ID']= ptID
    ecog_df.to_csv(pth.join(targ_pth, 'ECoG_Catalog.csv'), index = False)
    

    # Create Deidentified histograms
    if os.path.exists(np_daily_histogram):
        
        if not os.path.exists(pth.join(targ_pth, 'Histograms')):
            os.makedirs(pth.join(targ_pth, 'Histograms'))
     
        daily_hist_df = pd.read_csv(np_daily_histogram)
        daily_hist_df['Device ID']= daily_hist_df.groupby('Device ID').ngroup()+1
        daily_hist_df['Patient ID']= ptID
        daily_hist_df.to_csv(pth.join(targ_pth, 'Histograms', 'Histogram_Daily.csv'), index = False)
    else: 
        print('%s file not found, skipping Daily Histograms'%pth.basename(np_daily_histogram))
    
    # check if exists
    if os.path.exists(np_hourly_histogram):
        
        if not os.path.exists(pth.join(targ_pth, 'Histograms')):
            os.makedirs(pth.join(targ_pth, 'Histograms'))
        
        hourly_hist_df = pd.read_csv(np_hourly_histogram)
        hourly_hist_df['Device ID']= hourly_hist_df.groupby('Device ID').ngroup()+1
        hourly_hist_df['Patient ID']= ptID
        hourly_hist_df.to_csv(pth.join(targ_pth, 'Histograms', 'Histogram_Hourly.csv'), index = False)
    else: 
        print('%s file not found, skipping Hourly Histograms'%pth.basename(np_hourly_histogram))
    

    # Create Deidentified EpisodeDurations
    if os.path.exists(np_episodes_folder):
        
        if not os.path.exists(pth.join(targ_pth, 'EpisodeDurations')):
            os.makedirs(pth.join(targ_pth, 'EpisodeDurations'))
        
        epth= glob.glob(pth.join(np_episodes_folder, '*.csv'));
        for epdur in epth:
            
            ename = pth.basename(epdur).split('_')[3:]
            ename.insert(0,ptID)
            ename = '_'.join(ename)
            
            epdur_df = pd.read_csv(epdur)
            epdur_df['Device ID']= epdur_df.groupby('Device ID').ngroup()+1
            epdur_df['Patient ID']= ptID
            epdur_df.to_csv(pth.join(targ_pth, 'EpisodeDurations', ename), index = False)
    else:
        print('%s folder not found, skipping Episode Durations'%pth.basename(np_episodes_folder))
    
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
            [fdata, ftime, t_conversion_usec] = _readDatFile(dataFolder, ecog_df.iloc[[i_file]])
            dlen = fdata.shape[1]
            AllData.append(fdata)
            eventIdx.append(ctr + np.array([0,dlen-1]))
            ctr = ctr + dlen
            
        except (FileNotFoundError):
            logging.error('File %s not found'%(ecog_df['Filename'][i_file]))
            dneIdx.append(i_file)
            

    AllData = np.concatenate(AllData, axis = 1)
    AllData = AllData.astype('int16').T
    eventIdx = np.array(eventIdx)
    eventIdx = eventIdx.astype('int32')

    assert eventIdx.shape[0] == ecog_df.shape[0]-len(dneIdx)

    return AllData, eventIdx, dneIdx


def NPdat2mef(ptID, config):
    
    import jpype
    import jpype.imports

    # Launch the JVM
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=['../lib/MEF_writer.jar'])
        
    from edu.mayo.msel.mefwriter import MefWriter
    
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
            
            [fdata, ftime, t_conversion_usec] = _readDatFile(dataFolder, ecog_df.iloc[[i_file]])
        
            # Create mef subfolder, skip creation if mef folder already exists
            if pth.isdir(pth.join(dpath, fname)):
                continue
           
            os.mkdir(pth.join(dpath, fname))
                  
            blockSize = round(4000/SAMPLING_RATE)
            th = 100000
            
            for i_chan in range(0,NUM_CHANNELS):
                
                chanLabel= '%s_C%d.mef'%(ptID, i_chan+1)
                
                logging.debug(fdata[i_chan][:])
                
                mw = MefWriter(pth.join(dpath, fname, chanLabel), blockSize, SAMPLING_RATE, th)
                mw.writeData((fdata[i_chan][:]).astype(int), ftime.astype('l'), fdata.shape[1])
                mw.setInstitution(inst);
                mw.setSubjectID(ptID);
                mw.setChannelName(chanLabel[0:-4]);
                mw.setVoltageConversionFactor(gain);
                mw.close()  
                
        except(FileNotFoundError):
            logging.Error('File %s not found'%(ecog_df['Filename'][i_file]))
            continue
        
    return None


def createConcatDatLayFiles(ptID, config, ecog_df, newFilename, newFilePath):
    '''
        Creates a .dat and corresponding .lay file at "newFilePath" that concatenates
        all data contained in ecog_df.
        Pads off channels and eliminates overlap.
        
    Args:
        ptID (string): patient ID
        config (object): config file
        ecog_df (Pandas dataframe): ecog dataframe containing rows corresponding to data to concatenate
        newFilename (string): Name for concatenated file (extension should be omitted).
        newFilePath (string): Path to folder for concatenated output files

    Returns:
        dictionary of filenames and # bytes removed from them. 

    Example:
          catalog_csv = npdh.NPgetDataPath(ptID, config, 'ECoG Catalog')
          ecog_df= pd.read_csv(catalog_csv)
          ecog_rows = ecog_df[1:10]
          
          createLayFile(ecog_row, /path/to/lay/folder)

    '''

    try:
        assert isinstance(ecog_df, pd.DataFrame)
    except AssertionError as err:
        logging.error('Expected a DataFrame input')
        raise err

    # General file info variables, 
    dataFolder = NPgetDataPath(ptID, config, 'Dat Folder')
    datcat = pth.join(newFilePath, '%s.dat' % newFilename)
    
    # First remove rows in ecog_df if associated .dat files are missing
    fnames = os.listdir(dataFolder);
    isin = np.array([x in fnames for x in ecog_df.Filename.tolist()])
    if (~isin).any():
        idx = np.where(~isin)[0]
        logging.warning('Files not in data folder, skipping associated rows ' +
                        'in ecog.csv: %s'%ecog_df.iloc[idx].Filename.tolist())
        ecog_df = ecog_df.loc[isin, :]
        if ecog_df.empty:
            return {}
              
    # Sort by files by UTC start times
    start_utc,_,_,_ = _getTimeStrings(ecog_df)
    srt_inds = np.argsort(start_utc)
    datfiles = ecog_df['Filename'].tolist()
    datfiles = [datfiles[i] for i in srt_inds]

    datFileCount = len(datfiles)

    # Lists are appended and then written to .lay
    startTimes = []
    datSizes = []

    # For edge case with only one file in a month (while loop won't run as is in range(0, 0))
    if datFileCount == 1:
        target1_name = datfiles[0]
        target1 = pth.join(dataFolder, target1_name)
        
        _catExporter(ecog_df, datcat, target1)

        rawUTC1 = pd.Timestamp(ecog_df.loc[ecog_df['Filename'] == target1_name, 'Raw UTC timestamp'].iloc[0])
        ecog_PTL1 = ecog_df.loc[ecog_df['Filename'] == target1_name, 'ECoG pre-trigger length'].iloc[0]
        start1 = rawUTC1 - DateOffset(seconds=ecog_PTL1)

        startTimes.append(start1)
        datSizes.append(pth.getsize(target1))

    # Primary loop, compare_pass used to iterate through files
    rm_bytes = {}
    compare_pass = 0
    while compare_pass in range(0, datFileCount - 1):

        # File names and paths vars
        target1_name = datfiles[compare_pass] 
        target1 = pth.join(dataFolder, target1_name)
        target2_name = datfiles[compare_pass + 1]
        target2 = pth.join(dataFolder, target2_name)

        # Time vars (could be streamlined but would result in really long definitions)
        rawUTC1 = pd.Timestamp(ecog_df.loc[ecog_df['Filename'] == target1_name, 'Raw UTC timestamp'].iloc[0])
        ecog_PTL1 = ecog_df.loc[ecog_df['Filename'] == target1_name, 'ECoG pre-trigger length'].iloc[0]
        ecog_L1 = ecog_df.loc[ecog_df['Filename'] == target1_name, 'ECoG length'].iloc[0]
        t2end1 = ecog_L1 - ecog_PTL1
        start1 = rawUTC1 - DateOffset(seconds=ecog_PTL1)
        end1 = rawUTC1 + DateOffset(seconds=t2end1)

        rawUTC2 = pd.Timestamp(ecog_df.loc[ecog_df['Filename'] == target2_name, 'Raw UTC timestamp'].iloc[0])
        ecog_PTL2 = ecog_df.loc[ecog_df['Filename'] == target2_name, 'ECoG pre-trigger length'].iloc[0]
        start2 = rawUTC2 - DateOffset(seconds=ecog_PTL2)


        try:
            assert start1 <= start2
        except AssertionError as err:
            logging.error('Start times out of order %s:%s, %s:%s'%(target1_name, 
                                                                      start1.strftime("%m/%d/%Y, %H:%M:%S"),
                                                                      target2_name,                                                                     start2.strftime("%m/%d/%Y, %H:%M:%S")))
            raise err
        
        # Uses latest known end
        total_end = pd.Timestamp(ecog_df['Raw UTC timestamp'].iloc[0]) - DateOffset(
            seconds=ecog_df['ECoG pre-trigger length'].iloc[0])
        if end1 > total_end:
            total_end = end1

        # Amount of time overlap (both forms used)
        overlapTimeSeconds = pd.Timedelta.total_seconds(total_end - start2)
        overlapTimedelta = pd.Timedelta(total_end - start2)

        # Overlap in bytes based on off chs
        chs2 = _getOffChs(ecog_df, target2_name)
        bytes2del = overlapTimeSeconds * 500 * (4 - len(chs2))

        # In the event file is completely overlapped
        if bytes2del >= pth.getsize(target2):
            datfiles.remove(target2_name)
            
            bytes2del = pth.getsize(target2)
            overlapTimeSeconds = bytes2del / 500 / (4 - len(chs2))
            overlapTimedelta = pd.to_timedelta(overlapTimeSeconds, 's')
            
            rm_bytes[target2_name] = bytes2del
            
            datFileCount -= 1
            continue

        # < 0 as in no overlap, so just sends files to be concatenated
        if overlapTimeSeconds < 0:
            if compare_pass == 0:
                # For first step, where first file needs to be concatenated as well
                _catExporter(ecog_df, datcat, target1)
                startTimes.append(start1)
                datSizes.append(pth.getsize(target1))
            _catExporter(ecog_df, datcat, target2)
            startTimes.append(start2)
            datSizes.append(pth.getsize(target2))
            compare_pass += 1

        # In the event that overlap exists, sends files to be concatenated along with amount to drop of second file
        if overlapTimeSeconds >= 0:

            logging.info('Overlap found, between %s and %s'%(target1_name, target2_name))
            logging.info('Bytes to delete bytes2del %d, File1 start: %s'%(bytes2del, start1.strftime("%m/%d/%Y, %H:%M:%S")))

            start2new = start2 + overlapTimedelta
            
            rm_bytes[target2_name] = bytes2del
            
            if compare_pass == 0:
                _catExporter(ecog_df, datcat, target1)
                startTimes.append(start1)
                datSizes.append(pth.getsize(target1))
                
            _catExporter(ecog_df, datcat, target2, int(bytes2del))
            startTimes.append(start2new)
            datSizes.append(pth.getsize(target2) - int(bytes2del))
            compare_pass += 1


    # Below section creates corresponding .lay file

    # Sample indices corresponding to each .dat segment
    i_samp = np.cumsum([0] + [int(x / 2 / (4 - len(_getOffChs(ecog_df, i))))
                              for i, x in zip(datfiles, datSizes)])

    dat_fnames = [x[:-4] for x in ecog_df['Filename']]
    EPOCH = pd.Timestamp('1970-1-1')
    
    logging.debug(i_samp)

    # FileInfo Section
    layframe = ['[N_Config_String]\n'
                'DATFiles=%s.dat\n\n' % dat_fnames,

                '[FileInfo]\n',
                'File=%s.dat\n' % newFilename,
                'FileType=Interleaved\n',
                'SamplingRate=%d\n' % ecog_df['Sampling rate'].tolist()[0],
                'HeaderLength=0\n',
                'Calibration=1.0\n',
                'WaveformCount=%d\n' % ecog_df['Waveform count'].tolist()[0],
                'DataType=0\n\n'

                '[Patient]\n',  # Patient Section
                'ID=%s\n' % ptID,
                'Birthdate=\n',
                'Sex=\n',
                'TestDate=%s\n' % startTimes[0].strftime("%m/%d/%Y"),
                'TestTime=%s\n' % startTimes[0].strftime("%H:%M:%S.%f"),
                'Comments1=\n',
                'Technician=\n\n',

                '[SampleTimes]\n'
                ] + ['%s=%s\n' % (x, pd.Timedelta.total_seconds(y - EPOCH))
                     for x, y in zip(i_samp[:-1], startTimes)
                     ] + [
                   '\n[ChannelMap]\n',
                   'Ch.1=1\n',
                   'Ch.2=2\n',
                   'Ch.3=3\n',
                   'Ch.4=4\n\n',
                   '[Comments]\n\n',
                   '[UserEvents]\n\n']

    with open(pth.join(newFilePath, '%s.lay' % newFilename), "w") as f:
        f.writelines(layframe)
        
    return rm_bytes


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
        
        logging.info('Downloading %s new files to %s'%(len(download_inds), local_fold))
        
        for ind in download_inds:
            output_file= open(os.path.join(fpath, box_fold.name, box_filenames[ind]), 'wb')
            client.file(file_id=ids[ind]).download_to(output_file)
            output_file.close()
    
   except (IndexError, FileNotFoundError):
       logging.error('Local folder %s not found, downloading all'%(box_fold.name))
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
        logging.warning("Warning: mismatched number of.dat files (%d) and ECoG catalog length (%d)"%
            (NumberOfFiles, ecog_df.shape[0]))
    
    if len(np.unique(ecog_df['Sampling rate'])) > 1:
        sys.exit("Error: Multiple SamplingRates in file")
        
    if not (ecog_df['Sampling rate'][0] == SAMPLING_RATE):
         sys.exit("Error: Unexpected sampling rate")
        
    if sum(n < np.timedelta64(0) for n in np.diff(ecog_df['Raw UTC timestamp'])) > 0:
        sys.exit("Error: RawUTCTimestamp is not chronological")
        
        
def _readDatFile(dataFolderPath, ecog_row):
    
    assert isinstance(ecog_row, pd.DataFrame), 'Expected a DataFrame input.'
    assert ecog_row.shape[0] == 1, 'Expected a single row'

    # Open up dat_file
    dat_file = pth.join(dataFolderPath, ecog_row['Filename'].item())
    fs = ecog_row['Sampling rate'].item()
    
    enabled = (ecog_row[['Ch 1 enabled', 'Ch 2 enabled', 
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
    [t_start, t_trigger_UTC, t_trigger_local, t_conversion_usec] = _getTimeStrings(ecog_row)
    
    # Calculate associated time vector    
    dlen = fdata.shape[1]
    t_vec = np.arange(dlen)/fs*10**6
    ftime = t_start + t_vec
    
    return fdata, ftime, t_conversion_usec[0]

def _getTimeStrings(ecog_df_row):
    '''
    Args:
        ecog_df_row (TYPE): pandas Series object

    Returns:
        t_start_UTC (TYPE): DESCRIPTION.
        t_trigger_UTC (TYPE): DESCRIPTION.
        t_trigger_local (TYPE): DESCRIPTION.
        t_conversion_usec (TYPE): DESCRIPTION.

    '''
    
    assert isinstance(ecog_df_row, pd.DataFrame), 'Expected a DataFrame input'
    
    raw_UTC_str = ecog_df_row['Raw UTC timestamp'].tolist()
    raw_local_str = ecog_df_row['Raw local timestamp'].tolist()
    timestamp_str = ecog_df_row['Timestamp'].tolist()
        
    t_trigger_UTC = utils.str2dt_usec(raw_UTC_str)
    t_trigger_local = utils.str2dt_usec(raw_local_str)

    t_conversion_usec = [a - b for a, b in zip(t_trigger_UTC, t_trigger_local)]
    t_start_UTC = [a + b for a, b in zip(utils.str2dt_usec(timestamp_str), t_conversion_usec)]

    
    return t_start_UTC, t_trigger_UTC, t_trigger_local, t_conversion_usec

def _getOffChs(ecog_df, file):
    # Helper that returns list of off channels for a given file

    ch = []
    name = os.path.basename(file)
    for x in range(1, 5):
        if ecog_df.loc[ecog_df['Filename'] == name, 'Ch %s enabled' % x].iloc[0] == 'Off':
            ch.append(x)
    ch.sort()
    return ch


def _catExporter(ecog_df, datcat, file, overlap=0):
    # Saves a given file to concatenated month file
    # Pads off channels, last variable is # of bytes overlapping to get rid of (default 0)    
    ch = _getOffChs(ecog_df, file)
    if len(ch) > 0:
        with open(file, 'rb') as outfile:
            outfile.seek(overlap)
            a = np.fromfile(outfile, np.int16).reshape((-1, 4 - len(ch))).T
        for x in ch:
            a = np.insert(a, x - 1, 512, axis=0)
        with open(datcat, 'ab') as infile:
            a.T.astype(np.int16).tofile(infile)
    else:
        with open(datcat, 'ab') as infile:
            with open(file, 'rb') as outfile:
                infile.write(outfile.read()[overlap:])
    


    