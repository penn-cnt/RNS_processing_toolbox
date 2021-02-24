# Upload and Annotate Files

import json
import os
from rns_py_tools import bf_tools
from rns_py_tools import NPDataHandler as npdh


with open('./config.JSON') as f:
    config= json.load(f); 


def uploadPatientCatalogAnnots(ptID, config):
	''' Load annotations from ECoG Catalog for all patient indices in ptID_list '''

	bf_tools.annotate_from_catalog(ptID, config)


def pullPatientAnnots(config, layerName):
    '''pull annotatios from layerName for all patients in ptID_list '''

    ptList = [k['ID'] for k in config['patients']]

    for pt in ptList:
        outputPath = os.path.join(config['paths']['RNS_DATA_Folder'], pt)
        bf_tools.pull_annotations(pt, config, layerName, outputPath)
		
        print('Pulling annotations for patient %s'%pt)


def uploadNewPatient(ptID, config):
    
    tsName = ptID
    # Convert any new .dat files into mef files
    npdh.NPdat2mef(ptID, config)
    
    # Upload mefs to blackfynn
    bf_tools.uploadNewDat(tsName, ptID, config)
    

if __name__ == "__main__":
   
    with open('./config.JSON') as f:
        config= json.load(f); 
        
    