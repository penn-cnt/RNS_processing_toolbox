import csv
import datetime as DT
from blackfynn import Blackfynn

## SETTINGS to CHANGE:

filename=('/home/data/RNS_DataSharing/processed_20181103/AA_catalog.csv') 	#Path to CSV 
INITIALS='AA'			#Patient Initials as in "Initials" column
dataset= 'Neuropace RNS Dataset'
package='N:package:02399265-21db-4c0b-b92c-c525e53795e9'		#Package Link


EPOCH = DT.datetime(1970,1,1)

bf = Blackfynn()
ds=bf.get_dataset(dataset)
ts=bf.get(package)


def str2dt_usec(s):
	dt=DT.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f")
	return int((dt - EPOCH).total_seconds() * 1000000)


with open(filename) as csvfile:
	reader = csv.reader(csvfile, delimiter=',')

	# Get indices of timestamp, annotation name columns, etc.
	header=next(reader)
	header[0]=header[0].replace(u'\ufeff', '')
	start_local_i = header.index('Timestamp')			# string ('2015-03-1 08:31:56.969')
	trig_UTC_i = header.index('Raw UTC Timestamp')
	trig_local_i = header.index('Raw Local Timestamp')
	annot_name_i = header.index('ECoG trigger')
	ecog_len_i = header.index('ECoG length') 		#sec
	pt_i = header.index('Initials')

	aNames=[]
	aCtrs=[]
	for row in reader:
		if row[pt_i] == INITIALS:
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

			ts.insert_annotation(annotName, annotName+' '+str(aCtrs[aNames.index(annotName)])
				, start=starttime, end=int(endtime))
			print(annotName, aNames, aCtrs)
			