# Upload and Annotate Files

import json
import os
import sys
import logging
import traceback
import glob
import multiprocessing as mp
from pennsieve import Pennsieve

from functions import pennsieve_tools


def uploadPatientCatalogAnnots(ptList, config):
    ''' Load annotations from ECoG Catalog for all patient indices in ptID_list '''
    
    pnsv = Pennsieve()

    for ptID in ptList:

        try:
            pennsieve_tools.annotate_from_catalog(ptID, config, pnsv)
        except:
            logging.error('%s catalog annotation failed'%ptID)
            logging.error(traceback.format_exc())
            pass
        

def uploadPatientAnnots(ptList, config, annotLayerName=None):
    ''' Uploads all annotations from files in patient's Annotations folder or files
    specified by annotLayerName input '''
    
    pnsv = Pennsieve()
    
    for ptID in ptList:
        
        # Get Annotation Paths
        if annotLayerName:
            annotPths = [os.path.join(config['paths']['RNS_DATA_Folder'], ptID,
                                          'Annotations', '%s.mat'%annotLayerName)]
        else: 
            annotPths = glob.glob(os.path.join(config['paths']['RNS_DATA_Folder'],
                                               ptID,'Annotations','*.mat'))
        
        for annotPth in annotPths:
            if os.path.exists(annotPth):
                annotLayerName = annotPth.split('/')[-1][:-4]
            
                if annotLayerName == 'Device_Stim':
                    annotLayerName = 'Stims'
                
                pennsieve_tools.annotate_UTC_from_mat(ptID, config, 
                                                      annotLayerName, 
                                                      annotPth, pnsv)
        
        # TODO: Eventually harmonize annotation format, add to annotation folder
        if annotLayerName == 'Device_Stim':
            annotLayerName = 'Stims'
            annotPth = os.path.join(config['paths']['RNS_DATA_Folder'], ptID, 'Device_Stim.mat')
            
            pennsieve_tools.annotate_UTC_from_mat(ptID, config, 
                                                      annotLayerName, 
                                                      annotPth, pnsv)

def pullPatientAnnots(config, layerName):
    '''pull annotatios from layerName for all patients in ptID_list '''

    ptList = [['ID'] for k in config['patients']]

    for pt in ptList:
        outputPath = os.path.join(config['paths']['RNS_DATA_Folder'], pt)
        pennsieve_tools.pull_annotations(pt, config, layerName, outputPath)
		
        logging.info('Pulling annotations for patient %s'%pt)


def uploadNewPatient(ptList, config):
    
    pnsv = Pennsieve()
    
    for ptID in ptList:
        try:
            pennsieve_tools.uploadNewDat(ptID, config, pnsv)
        except:
            logging.error('%s upload failed'%ptID)
            logging.error(traceback.format_exc())
            pass


if __name__ == "__main__":
   
    with open('../config.JSON') as f:
        config= json.load(f)

    ptList = [pt['ID'] for pt in config['patients']]
    
    # Set up logging
    logfile = os.path.join(config['paths']['RNS_RAW_Folder'],'logfile.log');
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
  
    logging.basicConfig(filename=logfile, level=logging.INFO)
 
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    logging.info('Running pennsieve_pipeline.py with patient list: %s'%ptList)

    #Upload new data to Pennsieve
    x = input('Upload new .dat files to Pennsieve (y/n)?: ')
    if x =='y':
        uploadNewPatient(ptList, config)
    
    # Upload new annotations to Pennsieve
    x = input('Upload new NeuroPace event annotations to Pennsieve (y/n)?: ')
    if x =='y':
        uploadPatientCatalogAnnots(ptList, config)
    
    # Upload new annotations to Pennsieve
    x = input('Upload new annotations from file to Pennsieve (y/n)?: ')
    if x =='y':
        uploadPatientAnnots(ptList, config)
        
                

        
    