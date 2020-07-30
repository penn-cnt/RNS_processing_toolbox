import scipy.io as sio
from blackfynn import Blackfynn
import numpy as np
import csv
import datetime as DT
import pdb


def pull_annotations(package, layerName, outputPath):

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
def annotate_UTC_from_mat(package, newLayer, annot_mat_file):

	bf = Blackfynn()
	ts = bf.get(package) # Your package ID here
	ts.add_layer(newLayer) # Your name for new annotation layer here
	layer = ts.get_layer(newLayer) # Your name for new annotation layer here

	annotations = sio.loadmat(annot_mat_file) # Your path to .mat file of timestamps in UST here (e.g. /home/data/RNS_DataSharing/...)
	annotations = annotations['timestamps'] # Include this line if MATLAB variable saved to .mat file was called "timestamps"
	length = len(annotations[0])

	duration = 1 # duration of annotation (in microseconds)

	#ESTtoUTC = 14400000000 # 4 hrs in microseconds, to convert EST to UTC
	annotationName = 'MagnetSwipe_' # name of label for each annotation

	count = 1
	for x in range(0,length):
	    startTime = annotations.astype(int)[0]
	    layer.insert_annotation(annotationName+str(count), start=startTime[x],end=startTime[x]+duration) # add 4 hours for time shift; add 1 ms for end time
	    count = count + 1
	    print(count)


def str2dt_usec(s):
	dt=DT.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f")
	EPOCH = DT.datetime(1970,1,1)
	return int((dt - EPOCH).total_seconds() * 1000000)


def annotate_from_catalog(package, ecog_catalog):
	''' package: blackfynn package ID 
		ecog_catalog: .csv file from Neuropace '''

	bf = Blackfynn()
	ts=bf.get(package)


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
		pt_i = header.index('Initials')

		aNames=[]
		aCtrs=[]
		for row in reader:
			# Parse datetimes into usec, shift timezone to GMT
			tz_offset=str2dt_usec(row[trig_UTC_i])-str2dt_usec(row[trig_local_i])
			start_local=str2dt_usec(row[start_local_i])

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



