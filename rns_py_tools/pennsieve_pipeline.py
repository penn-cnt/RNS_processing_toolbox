# Upload and Annotate Files

import json
import os
from functions import pennseive_tools
from functions import NPDataHandler as npdh


def uploadPatientCatalogAnnots(ptList, config):
    ''' Load annotations from ECoG Catalog for all patient indices in ptID_list '''

    for ptID in ptList:
        pennseive_tools.annotate_from_catalog(ptID, config)


def pullPatientAnnots(config, layerName):
    '''pull annotatios from layerName for all patients in ptID_list '''

    ptList = [k['ID'] for k in config['patients']]

    for pt in ptList:
        outputPath = os.path.join(config['paths']['RNS_DATA_Folder'], pt)
        pennseive_tools.pull_annotations(pt, config, layerName, outputPath)
		
        print('Pulling annotations for patient %s'%pt)


def uploadNewPatient(ptList, config):
    
    for ptID in ptList:

        tsName = ptID
        # Convert any new .dat files into mef files
        npdh.NPdat2mef(ptID, config)
        
        # Upload mefs to Pennseive
        # pennseive_tools.uploadNewDat(tsName, ptID, config)
    

if __name__ == "__main__":
   
    with open('../config.JSON') as f:
        config= json.load(f)

    ptList = [pt['ID'] for pt in config['patients']]
    ptList = [ptList[3]]
    
    print('Running pennseive_pipeline.py with patient list: %s'%ptList)

    #Upload new data to Pennseive
    x = input('Upload new .dat files to Pennseive (y/n)?: ')
    if x =='y':
        uploadNewPatient(ptList, config)
    
    # Upload new annotations to Pennseive
    x = input('Upload new event annotations to Pennseive (y/n)?: ')
    if x =='y':
        uploadPatientCatalogAnnots(ptList, config)
        

        
    