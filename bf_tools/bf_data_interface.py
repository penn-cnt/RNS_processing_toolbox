from blackfynn import Blackfynn


#TODO, finish 
def uploadMef(dataset, package, mefFolder):
	''' Uploads mef files to package. If package is "None", 
		then a new package is created within the dataset '''
	
	ds = bf.get_dataset(dataset)
	bf = Blackfynn()

	# Check if single mef file, otherwise upload folder

	if package == None:	
		# Create new package
		ds.uplaod(mefFolder(1))

 	for mef_file in mefFolder
		package.append_files(mef_file)
