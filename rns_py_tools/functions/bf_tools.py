

"""
Blackfynn Interface Tools
(RNS Processing Toolbox)

Functions in this file: 
    pull_annotations(package, layerName, outputPath)
    annotate_UTC_from_mat(package, newLayer, annot_mat_file)
    annotate_from_catalog(package, ecog_catalog)
    uploadMef(dataset, package, mefFolder)
    uploadNewDat(dataset, tsName, datFolder)
    
"""

import scipy.io as sio
from blackfynn import Blackfynn
from blackfynn.models import TimeSeries
from functions import utils
import glob
import csv
import pdb
import os


def pull_annotations(ptID, config, layerName, outputPath):
    
    i_pt = utils.ptIdxLookup(config, 'ID', ptID)
    package = config['patients'][i_pt]['bf_package']

    bf = Blackfynn()
    ts= bf.get(package)

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
    package = config['patients'][i_pt]['bf_package']

    bf = Blackfynn()
    ts = bf.get(package) # Your package ID here
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
    ''' package: blackfynn package ID 
    ecog_catalog: .csv file from Neuropace '''
        
    i_pt = utils.ptIdxLookup(config, 'ID', ptID)
    package = config['patients'][i_pt]['bf_package']
    bf = Blackfynn()
    ts=bf.get(package)
    
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

    bf = Blackfynn()
    ds = bf.get_dataset(dataset)

	# Check if single mef file, otherwise upload folder

    if package == None:	
		# Create new package
        ds.uplaod(mefFolder(1))

    for mef_file in mefFolder:
        package.append_files(mef_file)


#TODO, check for Blackfynn agent, if not, agent = false
#TODO: Only append _new_ .dat files
#TODO: Perhaps pull all .mef files into one folder and do single upload. 
def uploadNewDat(tsName, ptID, config):
    ''' Uploads mef files to package. If package is "None", 
		then a new package is created within the dataset '''

    i_pt= utils.ptIdxLookup(config, 'ID', ptID)    
    dataset = config['patients'][i_pt]['bf_dataset']
    
    bf = Blackfynn()
    ds = bf.get_dataset(dataset)
    ts = TimeSeries(tsName)
 
    dpath = os.path.join(config['paths']['RNS_DATA_Folder'], ptID, 'mefs/')
        
    allMefs = glob.glob(os.path.join(dpath,'*', '*.mef'))
    
    # Check that ts doesn't exist. If not: 
    ds.add(ts)
    ctr = 1
    
    for x in allMefs:
        print('Upload %d of %d'%(ctr, len(allMefs)))
        ts.append_files(x) 
        ctr = ctr+1

# 	# Check if single mef file, otherwise upload folder
#     if package == None:	
#         #ds.set_ready()
    ds.upload(dpath,  recursive=True, display_progress = True)


