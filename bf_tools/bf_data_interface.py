from blackfynn import Blackfynn
import TimeSeries 
import os

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

 	for mef_file in mefFolder
		package.append_files(mef_file)


#TODO, finish:
def uploadNewDat(dataset, tsName, datFolder):
	''' Uploads mef files to package. If package is "None", 
		then a new package is created within the dataset '''

	bf = Blackfynn()
	ds = bf.get_dataset(dataset)
	ts = TimeSeries(tsName)
	ds.add(ts)

	if os.path.isdir(datFolder)
		files = 
	elif os.path.isfile(path):  
		files = datFolder

	# Check if single mef file, otherwise upload folder
	if package == None:	
		ds.set_ready()
		ds.upload(datFolder)