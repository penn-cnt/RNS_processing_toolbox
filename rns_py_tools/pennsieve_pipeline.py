# Upload and Annotate Files

import json
import os
import sys
import logging
import traceback
import glob
import time
import numpy as np
import scipy.io as sio
import multiprocessing as mp
from pennsieve import Pennsieve
from functions import pennsieve_tools


def uploadPatientCatalogAnnots(ptList, config):
    ''' Load annotations from ECoG Catalog for all patient indices in ptID_list '''
    
    pnsv = Pennsieve()
    
    ptProcessed = np.array([False]*len(ptList))
    ptList = np.array(ptList)

    # Processing may take a while
    for i_iter in range(0,10):
        
        for i_pt in np.where(~ptProcessed)[0]:
            ptID = ptList[i_pt]
            try:
                annotComplete = pennsieve_tools.annotate_UTC_from_catalog(ptID, config, pnsv)
                ptProcessed[i_pt] = annotComplete
            except:
                logging.error('ERROR: %s catalog annotation failed'%ptID)
                logging.error(traceback.format_exc())
                pass
        
        if all(ptProcessed):
            return
        print('Still processing, trying for %d more minutes' % (10-i_iter))
        time.sleep(60)
    
    print('function timed out, %s are not completed' % ptList[~ptProcessed])
    
        

def uploadPatientAnnots(ptList, config, annotLayerName=None):
    ''' Uploads all annotations from files in patient's Annotations folder or files
    specified by annotLayerName input '''
    
    pnsv = Pennsieve()
    
    for ptID in ptList:
        print(ptID)
        
        # Get Annotation Paths
        if annotLayerName:
            annotPths = [os.path.join(config['paths']['RNS_DATA_Folder'], ptID,
                                          'Annotations', '%s.mat'%annotLayerName)]
        else: 
            annotPths = glob.glob(os.path.join(config['paths']['RNS_DATA_Folder'],
                                               ptID,'Annotations', '*.mat'))
        
        print(annotPths)
        
        for annotPth in annotPths:
            if os.path.exists(annotPth):
                annotLayerName = annotPth.split('/')[-1][:-4]
                print(annotLayerName)
            
                if annotLayerName == 'Device_Stim':
                    annotLayerName = 'Stims'
                
                pennsieve_tools.annotate_UTC_from_mat(ptID, config, 
                                                      annotLayerName, 
                                                      annotPth, pnsv)


def pullPatientAnnots(config, layerName, pnsv):
    '''pull annotatios from layerName for all patients in ptID_list '''

    ptList = [['ID'] for k in config['patients']]
    pnsv = Pennsieve()

    for pt in ptList:
        outputPath = os.path.join(config['paths']['RNS_DATA_Folder'], pt)
        annots_df = pennsieve_tools.pull_annotations(pt, config, layerName, pnsv)
		
        logging.info('Pulling annotations for patient %s'%pt)
        sio.savemat(os.path.join(outputPath, 'Annotations', layerName +'_annots.mat'), annots_df.to_dict('list'))


def uploadNewPatientData(ptList, config):
    
    pnsv = Pennsieve()
    
    for ptID in ptList:
        try:
            pennsieve_tools.uploadNewDatByMonth(ptID, config, pnsv)
        except:
            logging.error('%s upload failed'%ptID)
            logging.error(traceback.format_exc())
            pass


if __name__ == "__main__":
   
    with open('../config.JSON') as f:
        config= json.load(f)

    if len(sys.argv)>1:
        ptList = [sys.argv[1]]
    else:
        ptList = [pt['ID'] for pt in config['patients']]
        
    # Set up logging
    logfile = os.path.join(config['paths']['RNS_RAW_Folder'],'logfile.log');
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
  
    FORMAT = '%(asctime)s %(funcName)s: %(message)s'
    logging.basicConfig(filename=logfile, level=logging.INFO, format=FORMAT)
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    logging.info('Running pennsieve_pipeline.py with patient list: %s'%ptList)

    #Upload new data to Pennsieve
    x = input('Upload new .dat files to Pennsieve (y/n)?: ')
    if x =='y':
        uploadNewPatientData(ptList, config)
    
    # Upload new annotations to Pennsieve
    x = input('Upload new NeuroPace event annotations to Pennsieve (y/n)?: ')
    if x =='y':
        uploadPatientCatalogAnnots(ptList, config)
    
    # Upload new annotations to Pennsieve
    x = input('Upload new annotations from file to Pennsieve (y/n)?: ')
    if x =='y':
        uploadPatientAnnots(ptList, config)
        
                

        
    