

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
import datetime as DT
import csv
import pdb
import json
import os
import shutil


def pull_annotations(ptID, config, layerName, outputPath):
    
    i_pt = utils.ptIdxLookup(config, 'ID', ptID)
    package = config['patients'][i_pt]['pnsv_package']

    pnsv = Pennsieve()
    ts= pnsv.get(package)

    pdb.set_trace();

    try: 
        layer = ts.get_layer(layerName);
    except:
        print('Could not find layer %s'%layerName)
        return

    print(outputPath+ layerName +'_annots.mat')
	# Make sure annotations are correct. 
    anns = [(a.start, a.end) for a in layer.annotations()];
    desc = [(a.description) for a in layer.annotations()];
    sio.savemat(outputPath+ layerName +'_annots.mat', {'annots':anns, 'descriptions': desc})

	

# TODO: test this function
def annotate_UTC_from_mat(ptID, config, newLayer, annot_mat_file):
    
    i_pt = utils.ptIdxLookup(config, 'ID', ptID)
    package = config['patients'][i_pt]['pnsv_package']

    pnsv = Pennsieve()
    ts = pnsv.get(package) # Your package ID here
    ts.add_layer(newLayer) # Your name for new annotation layer here
    layer = ts.get_layer(newLayer) # Your name for new annotation layer here

    annotations = sio.loadmat(annot_mat_file) # Your path to .mat file of timestamps in UTC here (e.g. /home/data/RNS_DataSharing/...)
    annotations = annotations['timestamps']   # Include this line if MATLAB variable saved to .mat file was called "timestamps"
    length = len(annotations[0])

    durations = annotations['annotDur']       # duration of annotation (in microseconds)
    annotationName = annotations['annotName'] # name of label for each annotation

    for x in range(0,length):
        startTime = annotations.astype(int)[0]
        layer.insert_annotation(annotationName[x], start=startTime[x],end=startTime[x]+durations[x]) # add 4 hours for time shift; add 1 ms for end time
        print(x)



def annotate_from_catalog(ptID, config):
    ''' package: Pennsieve package ID 
    ecog_catalog: .csv file from Neuropace '''
        
    i_pt = utils.ptIdxLookup(config, 'ID', ptID)
    package = config['patients'][i_pt]['pnsv_package']
    pnsv = Pennsieve()
    ts = pnsv.get(package)
    
    ecog_catalog = utils.getDataPath(ptID, config, 'ecog catalog')


    with open(ecog_catalog) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
		# Get indices of timestamp, annotation name columns, etc.
        header=next(reader)
        header[0]=header[0].replace(u'\ufeff', '')
        start_local_i = header.index('Timestamp')			# string ('2015-03-1 08:31:56.969')
        trig_UTC_i = header.index('Raw UTC timestamp')
        trig_local_i = header.index('Raw local timestamp')
        annot_name_i = header.index('ECoG trigger')
        ecog_len_i = header.index('ECoG length') 		#sec

        aNames=[]
        aCtrs=[]
        for row in reader:
		# Parse datetimes into usec, shift timezone to GMT
            tz_offset= utils.str2dt_usec(row[trig_UTC_i])-utils.str2dt_usec(row[trig_local_i])
            start_local= utils.str2dt_usec(row[start_local_i])
            starttime=start_local+tz_offset
            endtime=float(row[ecog_len_i])*1000000+starttime

			#Increment annotation ctr and add annotation type list
            try:
                annotName= row[annot_name_i]
                aCtrs[aNames.index(annotName)]+=1
            except:
                aNames.append(annotName)
                aCtrs.append(1)

            description= annotName+' '+str(aCtrs[aNames.index(annotName)])+'-- '+row[trig_UTC_i]
            ts.insert_annotation(annotName, description, start=starttime, end=int(endtime))

        print(annotName, aNames, aCtrs)


#TODO, finish 
def uploadMef(dataset, package, mefFolder):
    ''' Uploads mef files to package. If package is "None", 
    then a new package is created within the dataset '''

    pnsv = Pennsieve()
    ds = pnsv.get_dataset(dataset)

	# Check if single mef file, otherwise upload folder

    if package == None:	
		# Create new package
        ds.uplaod(mefFolder(1))

    for mef_file in mefFolder:
        package.append_files(mef_file)
        

def uploadDatLay(collection, datlay_folder):
    return 0


#TODO: Only append _new_ .dat files
def uploadNewDat(ptID, config):
    ''' Uploads new .dat files to patient folder in dataset. All .dat files
    for a given month are concatenated into a single timeseries '''

    i_pt= utils.ptIdxLookup(config, 'ID', ptID)    
    dataset = config['patients'][i_pt]['pnsv_dataset']
    
    pnsv = Pennsieve()
    ds = pnsv.get_dataset(dataset)
    
    # Get collection for ptID, create one if nonexistent
    collection  = [i for i in ds.items if i.type == 'Collection' and i.name == ptID]
    if not collection:
        collection = ds.create_collection(ptID)
    else: collection = collection[0]
    

    # Get last year and month of data in collection
    uploaded = [i.name for i in collection.items if i.type == 'TimeSeries']
    # parse to last year and last month
    
    catalog_csv = npdh.NPgetDataPath(ptID, config, 'ECoG Catalog')
    ecog_df= pd.read_csv(catalog_csv)
    
    utc_dt = [DT.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f") for s in ecog_df['Raw UTC timestamp']]
    yrmin= min(y.year for y in utc_dt)
    yrmax = max(y.year for y in utc_dt)
    
    tmpPath = os.path.join(config['paths']['RNS_RAW_Folder'],'tmp_%s'%ptID)
    
    # Overwrite temp folder if existing
    if os.path.exists(tmpPath):
        shutil.rmtree(tmpPath)
    os.makedirs(tmpPath)      
            
    # Concatenate .dat files for each month, then upload 
    for yr in range(yrmin,yrmax+1):
        for mon in range (1,13):
            
            ts_name = '%s_%d_%02d'%(ptID, yr, mon)     
            mon_inds = [i for i, x in enumerate(utc_dt)
                    if x.month == mon and x.year == yr]
                
            if mon_inds:
                npdh.createConcatDatLayFiles(ptID, config,
                                             ecog_df.iloc[mon_inds],
                                             ts_name,
                                             tmpPath)              
    # Upload folder with monthly datasets
    collection.upload(tmpPath)
            
    #shutil.rmtree(tmpPath)
                
            
if __name__ == "__main__":
    
    with open('../config.JSON') as f:
        config= json.load(f)
    
    uploadNewDat('HUP101', config)
    