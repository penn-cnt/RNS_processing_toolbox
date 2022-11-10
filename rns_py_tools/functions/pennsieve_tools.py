

"""
Pennsieve Interface Tools
(RNS Processing Toolbox)

Functions in this file: 
    pull_annotations(package, layerName, outputPath)
    annotate_UTC_from_mat(package, newLayer, annot_mat_file)
    annotate_from_catalog(package, ecog_catalog)
    uploadMef(dataset, package, mefFolder)
    uploadNewDat(dataset, tsName, datFolder)
    
"""

import scipy.io as sio
from pennsieve import Pennsieve
from functions import NPDataHandler as npdh
from functions import utils
import pandas as pd
import numpy as np
import datetime as DT
import time
import csv
import pdb
import json
import logging
import tempfile
import os
import shutil



# Data Functions

def processPatientTimeseries(ptIDs, config, pnsv):
    
    for ptID in ptIDs:
        collection = get_pt_collection(ptID, config, pnsv)
        
        for item in collection.items:
            if item.state == 'UPLOADED':
                item.process()            
    

def get_pt_collection(ptID, config, pnsv):
    
    i_pt = utils.ptIdxLookup(config, 'ID', ptID)
    dataset = config['patients'][i_pt]['pnsv_dataset']
    ds = pnsv.get_dataset(dataset)
    
    # Get collection for ptID, create one if nonexistent
    collection  = [i for i in ds.items if i.type == 'Collection' and i.name == ptID]
    if not collection:
        collection = ds
    else: collection = collection[0]
    
    return collection
        

def uploadSingleDat(ptID, config, pnsv, ecog_catalog_inds = None):
    
    logging.info('Consolidating %s data for Pennsieve'%ptID)
    
    i_pt = utils.ptIdxLookup(config, 'ID', ptID)
    dataset = config['patients'][i_pt]['pnsv_dataset']
    
    collection = pnsv.get_dataset(dataset)    

    [ecog_df, tmpPath] = _upload_prep(ptID, config, pnsv, ecog_catalog_inds)
    
    ts_name = ptID
    npdh.createConcatDatLayFiles(ptID, config, ecog_df, ts_name, tmpPath)  

    _upload_dir_to_pnsv(ptID, tmpPath, collection)
    

def uploadNewDatByMonth(ptID, config, pnsv, ecog_catalog_inds=None):
    """
    Uploads new .dat files to patient folder in dataset. All .dat files
    for a given month are concatenated into a single timeseries.
    
    Args:
        ptID (string): DESCRIPTION.
        config (dict): config dictionary
        pnsv (Pennsieve): Pennsieve object
        ecog_catalog_inds ([int], optional): indices of selected events 
        in ecog catalog to upload. Defaults to None.

    Returns:
        None.

    """

    logging.info('Consolidating %s data for Pennsieve'%ptID)

    i_pt = utils.ptIdxLookup(config, 'ID', ptID)
    dataset = config['patients'][i_pt]['pnsv_dataset']
    
    try:
        ds = pnsv.get_dataset(dataset)
    except:
        ds = pnsv.create_dataset(dataset)
        
    # Get collection for ptID, create one if nonexistent
    collection  = [i for i in ds.items if i.type == 'Collection' and i.name == ptID]
    print('trying to get a collection')
    if not collection:
        collection = ds.create_collection(ptID)
    else: collection = collection[0]
    [ecog_df, tmpPath] = _upload_prep(ptID, config, pnsv, ecog_catalog_inds)
    
    utc_dt = [DT.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f") for s in ecog_df['Raw UTC timestamp']]
    yrmin= min(y.year for y in utc_dt)
    yrmax = max(y.year for y in utc_dt)
    today = DT.date.today()
            
    # Concatenate .dat files for each month if collection doesn't exist, then upload 
    for yr in range(yrmin,yrmax+1):
        for mon in range (1,13):
            
            # Skip current month to avoid partial month upload
            if (mon == today.month and yr == today.year):
                break
            
            ts_name = '%s_%d_%02d'%(ptID, yr, mon)
            
            mon_inds = [i for i, x in enumerate(utc_dt)
                    if x.month == mon and x.year == yr]
                
            if mon_inds and not collection.get_items_by_name('%s_%d_%02d'%(ptID, yr, mon)):
                npdh.createConcatDatLayFiles(ptID, config,
                                              ecog_df.iloc[mon_inds],
                                              ts_name,
                                              tmpPath) 
    
    _upload_dir_to_pnsv(ptID, tmpPath, collection)




# Annotation Functions

def pull_annotations(ptID, config, layerName, pnsv):
    
    
    collection = get_pt_collection(ptID, config, pnsv)
    
    anns = []
    desc = []
    
    for ts in collection.items:
        
        if ts.type != 'TimeSeries':
            continue
        
        if not np.isin(layerName, [l.name for l in ts.layers]):
            continue
        
        layer = ts.get_layer(layerName)
        labels = [annot.label for annot in ts.get_layer(layerName).annotations()]
        print(labels)
        
     	# Make sure annotations are correct. 
        anns = anns + [(a.start, a.end) for a in layer.annotations()];
        desc = desc + [(a.description) for a in layer.annotations()];

        print(anns)
        print(desc)
    
    
    annots_dict = {'annots':anns, 'descriptions': desc}

    return annots_dict
    
def add_empty_layer(ptID, config, layerName, pnsv):
    
    collection = get_pt_collection(ptID, config, pnsv)
    for ts in collection.items:
            if ts.type == 'TimeSeries':
                ts.add_layer(layerName)
    
def delete_layer(ptID, config, layerName, pnsv):
    
    collection = get_pt_collection(ptID, config, pnsv)
    for ts in collection.items:
        if ts.type == 'TimeSeries':
            if any([layerName in i.name for i in ts.layers]):
                layer = ts.get_layer(layerName)
                ts.delete_layer(layer)
            

def annotate_UTC_from_mat(ptID, config, newLayer, annot_mat_file, pnsv):
    
    collection = get_pt_collection(ptID, config, pnsv)
    
    logging.info('Adding new annotations to %s layer for %s'%(newLayer, ptID))

    annotations = sio.loadmat(annot_mat_file) # Your path to .mat file of timestamps in UTC here (e.g. /home/data/RNS_DataSharing/...)
    annots = annotations['annots']  # Get annots, should be stored in posixtime microseconds
    
    annots_dt= []
    annots_dt.append(utils.posix2dt_UTC(annots[:,0]))  # Clunky but I don't know how to do this better... 
    annots_dt.append(utils.posix2dt_UTC(annots[:,1]))
    
    try: 
         descriptions = annotations['descriptions']
    except: 
        descriptions = [newLayer] * len(annots)

    annot_time_str = [DT.datetime.strftime(annot, "%Y-%m-%d %H:%M:%S.%f")[:-3]for annot in annots_dt[0]]
    annot_str = ['%s-- %s'%(i,j) for i,j in zip(descriptions, annot_time_str)]
    
    yrmin= min(y.year for y in annots_dt[0])
    yrmax = max(y.year for y in annots_dt[1])
    
    # Upload annotations to layer
    for yr in range(yrmin,yrmax+1):
        for mon in range (1,13):
            
            mon_inds = [i for i, x in enumerate(annots_dt[0])
                    if x.month == mon and x.year == yr]
            
            if mon_inds:
                item = collection.get_items_by_name('%s_%d_%02d'%(ptID, yr, mon))[0]
                
                if any([newLayer in i.name for i in item.layers]):
                    old_labels = [annot.label for annot in item.get_layer(newLayer).annotations()]
                    new_labels_i = [count for count, i in  enumerate([annot_str[i] for i in mon_inds]) if i not in old_labels]
                    mon_inds = [mon_inds[i] for i in new_labels_i]
                
                logging.info('Uploading %d new annotations to layer %s in %s'%(len(mon_inds), newLayer, item.name))
                
                for i in mon_inds:
                    item.insert_annotation(newLayer, annot_str[i], 
                                           start = int(round(annots[i,0]/1000, 0)*1000), 
                                           end = int(round(annots[i,1]/1000, 0)*1000))
                    
                    
def annotate_UTC_from_dataframe(ptID, config, newLayer, annot_df, pnsv):
    '''
    Args:
        ptID (String): Patient ID (e.g. 'HUP1234')
        config (dict): configuration file 
        newLayer (String): Annotation Layer name
        annot_df (dataFrame): Annotation dataframe containing the following fields: 
                - annot_start
                - annot_end
                - descriptions
        pnsv (TYPE): DESCRIPTION.

    Returns:
        None.

    '''
    
    collection = get_pt_collection(ptID, config, pnsv)
    
    logging.info('Adding new annotations to %s layer for %s'%(newLayer, ptID))

    annotstart = annot_df['annot_start']  # Get annots, should be stored in posixtime microseconds
    annotend = annot_df['annot_end'] 
    
    annots_dt= []
    annots_dt.append(utils.posix2dt_UTC(annotstart))  # Clunky but I don't know how to do this better... 
    annots_dt.append(utils.posix2dt_UTC(annotend))
    
    try: 
         descriptions = annot_df['descriptions']
    except: 
        descriptions = [newLayer] * len(annotstart)

    annot_time_str = [DT.datetime.strftime(annot, "%Y-%m-%d %H:%M:%S.%f")[:-3]for annot in annots_dt[0]]
    annot_str = ['%s-- %s'%(i,j) for i,j in zip(descriptions, annot_time_str)]
    
    yrmin= min(y.year for y in annots_dt[0])
    yrmax = max(y.year for y in annots_dt[1])
    
    # Upload annotations to layer
    for yr in range(yrmin,yrmax+1):
        for mon in range (1,13):
            
            mon_inds = [i for i, x in enumerate(annots_dt[0])
                    if x.month == mon and x.year == yr]
            
            if mon_inds:
                item = collection.get_items_by_name('%s_%d_%02d'%(ptID, yr, mon))[0]
                
                if any([newLayer in i.name for i in item.layers]):
                    old_labels = [annot.label for annot in item.get_layer(newLayer).annotations()]
                    new_labels_i = [count for count, i in  enumerate([annot_str[i] for i in mon_inds]) if i not in old_labels]
                    mon_inds = [mon_inds[i] for i in new_labels_i]
                
                logging.info('Uploading %d new annotations to layer %s in %s'%(len(mon_inds), newLayer, item.name))
                
                for i in mon_inds:
                    item.insert_annotation(newLayer, annot_str[i], 
                                           start = int(round(annotstart[i]/1000, 0)*1000), 
                                           end = int(round(annotend[i]/1000, 0)*1000))
                    

def annotate_timeseries_from_dataframe(newLayer, annot_df, ts):
    
    annotstart = annot_df['annot_start']  # Get annots, should be stored in posixtime microseconds
    annotend = annot_df['annot_end'] 
    
    annots_dt= []
    annots_dt.append(utils.posix2dt_UTC(annotstart))  # Clunky but I don't know how to do this better... 
    annots_dt.append(utils.posix2dt_UTC(annotend))
    
    try: 
         descriptions = annot_df['descriptions']
    except: 
        descriptions = [newLayer] * len(annotstart)
        
    annot_time_str = [DT.datetime.strftime(annot, "%Y-%m-%d %H:%M:%S.%f")[:-3]for annot in annots_dt[0]]
    annot_str = ['%s-- %s'%(i,j) for i,j in zip(descriptions, annot_time_str)]

    for i in annot_df.index:
        ts.insert_annotation(newLayer, annot_str[i], 
                               start = int(round(annotstart[i]/1000, 0)*1000), 
                               end = int(round(annotend[i]/1000, 0)*1000))
    

def annotate_UTC_from_catalog(ptID, config, pnsv):
    ''' Uploads all annotations from ecog_catalog to a patient's data. Does not 
        upload duplicate annotations, skips upload if a timeseries is not processed. 
    '''
    
    logging.info('Adding annotations from catalog for %s'%ptID)
    
    collection = get_pt_collection(ptID, config, pnsv)
    
    # Error if collection doesn't exist!
    
    catalog_csv = npdh.NPgetDataPath(ptID, config, 'ECoG Catalog')
    
    try:
        ecog_df= pd.read_csv(catalog_csv)
    except TimeoutError:
        logging.info('Timeout error reading EcoG Catalog, trying again')
        ecog_df= pd.read_csv(catalog_csv)
    
    utc_dt = [DT.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f") for s in ecog_df['Raw UTC timestamp']]
    
    # Get the timeseries corresponding to each month/year, and upload
    # corresponding annotations to that month. 
    
    itemsProcessed = True
    
    for item in collection.items:
        
        # First check that item has been procesed:
        if not item.state=='READY':
            if item.state=='UPLOADED':
                item.process() 
            itemsProcessed = False
            logging.warning('Item %s not processed, current status %s'%(item.name, item.state))
         
            continue
        
        # Get event indexes corresponding to year and month
        [ID, yr, mon] = item.name.split('_')
        mon_inds = [i for i, x in enumerate(utc_dt)
                    if x.month == int(mon) and x.year == int(yr)]
        if mon_inds:
            trigger_utc_datetime = ecog_df['Raw UTC timestamp'].iloc[mon_inds]
            trigger_utc = utils.str2dt_usec(trigger_utc_datetime.tolist())
            trigger_local = utils.str2dt_usec(ecog_df['Raw local timestamp'].iloc[mon_inds].tolist())
            start_local =  utils.str2dt_usec(ecog_df['Timestamp'].iloc[mon_inds].tolist())
            ecog_len  =  ecog_df['ECoG length'].iloc[mon_inds]
            trigger_types = ecog_df['ECoG trigger'].iloc[mon_inds]

            tz_offset = np.subtract(trigger_utc,trigger_local)
            starttimes = np.add(start_local,tz_offset)
            endtimes = list(ecog_len*1000000 + starttimes)
            
            all_descriptions = [i+' '+str(j)+'--'+k for i, j,k in zip(trigger_types, mon_inds, trigger_utc_datetime)]
            
            # only upload descriptions not in current annotation labels to prevent duplicates
            annotlist = [l.annotations() for l in item.layers]
            labels = [annot.label for annot in [i for sub in annotlist for i in sub]]
            descriptions = [i for i in all_descriptions if i not in labels]
            
            for i_annot in range(0,len(descriptions)):
                
                #logging.info('Uploading %d new annotations to %s'%(len(descriptions), item.name))
                item.insert_annotation(trigger_types.iloc[i_annot], descriptions[i_annot],
                                       start=int(starttimes[i_annot]), 
                                       end=int(endtimes[i_annot]))
        
    return itemsProcessed
        


# Helper Functions

def _upload_prep(ptID, config, pnsv, ecog_catalog_inds):
            
    catalog_csv = npdh.NPgetDataPath(ptID, config, 'ECoG Catalog')
    
    try:
        ecog_df= pd.read_csv(catalog_csv)
    except TimeoutError:
        logging.info('Timeout error reading EcoG Catalog, trying again')
        ecog_df= pd.read_csv(catalog_csv)
    
    # Only upload data specified by ecog_catalog_inds
    if ecog_catalog_inds:
        ecog_df = ecog_df.iloc[ecog_catalog_inds]
        
    tmpdir = tempfile.gettempdir()
    tmpPath = os.path.join(tmpdir,'RNS_RAW_Folder','tmp_%s'%ptID)
    
    # Overwrite temp folder if existing
    if os.path.exists(tmpPath):
        shutil.rmtree(tmpPath)
    os.makedirs(tmpPath)     
    
    return ecog_df, tmpPath


def _upload_dir_to_pnsv(ptID, tmpPath, collection):
    #Upload folder with datasets if directory contains files
    if os.listdir(tmpPath):
        try:
            logging.info('Uploading %s data to Pennsieve at %s' % (ptID, tmpPath))
            
            try:
                collection.upload(tmpPath, display_progress=True)
            except TimeoutError:
                logging.info('Upload Timeout error, trying again')
                collection.upload(tmpPath)
            
            # Trigger processing of data (might be able to use process 
            # method of collection item)
            logging.info('processing uploaded items')
            for item in collection.items:
                if item.state == 'UPLOADED':
                    item.process()
                
        except:
            logging.exception('')
    else:
        print('No new data to upload for %s'%ptID)
                        
    shutil.rmtree(tmpPath)
    
                
            
if __name__ == "__main__":
    
    with open('../config_server.JSON') as f:
        config= json.load(f)
    
    #ptList = [pt['ID'] for pt in config['patients']]
    pnsv = Pennsieve()
    uploadNewDatByMonth('HUP137', config, pnsv)
    
    pnsv.delete()
    
    #annotate_from_catalog('HUP059', config)
    
    #processPatientTimeseries(ptList, config)
    

    
    # ptID = 'HUP137'
    # annot_mat_file = os.path.join(config['paths']['RNS_DATA_Folder'], ptID, 'Annotations', 'BL Marked Seizures_annots.mat')
    # newLayer = 'GOLD_STANDARD_SEIZURES_BL'
    # annotate_UTC_from_mat(ptID, config, newLayer, annot_mat_file, pnsv)
    
    
    