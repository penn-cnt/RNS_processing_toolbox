# Upload and Annotate Files

import json
import os
from rns_py_tools import bf_tools
from rns_py_tools import NPDataHandler as npdh


with open('./config.JSON') as f:
    config= json.load(f); 

def uploadPatientAnnots(ptID_list):
	''' Load annotations from ECoG Catalog for all patient indices in ptID_list '''

	# Load data from config.JSON file 
	f = open('config.JSON') 
	data = json.load(f) 
	f.close() 

	inst = data['institution']
	ptList = data['patients']
	paths = data['paths']


	for i_pt in ptID_list:
		prefix =  "_".join([inst, ptList[i_pt]['Initials'], ptList[i_pt]['PDMS_ID']])
		package = ptList[i_pt]['bf_package']
		ecog_catalog = os.path.join(paths['RNS_RAW_Folder'], prefix +' EXTERNAL #PHI', '_'.join([prefix, 'ECoG_Catalog.csv']))

		print('Uploading annotations for patient %s'%ptList[i_pt]['Initials'])

		bf_tools.annotate_from_catalog(package, ecog_catalog)


def pullPatientAnnots(ptID_list, layerName):
	'''pull annotatios from layerName for all patients in ptID_list '''

	# Load data from config.JSON file 
	f = open('config.JSON') 
	data = json.load(f) 
	f.close() 

	ptList = data['patients']
	paths = data['paths']


	for i_pt in ptID_list:
		outputPath = os.path.join(paths['RNS_DATA_Folder'], ptList[i_pt]['RNS_ID'])
		package = ptList[i_pt]['bf_package']
		bf_tools.pull_annotations(package, layerName, outputPath)
		
		print('Pulling annotations for patient %s'%ptList[i_pt]['RNS_ID'])


# uploadPatientAnnots([16,5,3,12])
# pullPatientAnnots(np.arange(0,19), 'BL_Annotation')


def uploadNewPatient(ptID, config):
    
    tsName = ptID
    # Convert any new .dat files into mef files
    npdh.NPdat2mef(ptID, config)
    
    # Upload mefs to blackfynn
    bf_tools.uploadNewDat(tsName, ptID, config)
    
