import scipy.io as sio
from blackfynn import Blackfynn

## UPDATE SETTINGS:

pathToOutputFile=('../false-postive-classification-pipeline/Classifiers/window_scheme3_5s/') 	#Path to CSV 
dataset= 'Neuropace RNS Dataset'
package='N:package:71b87a8f-b50c-4fcd-b2c7-65aa3078222f'		#Package Link
layerName='BL Marked Seizures'

bf = Blackfynn()
ds=bf.get_dataset(dataset)
ts=bf.get(package)
layer = ts.get_layer(layerName);

# Make sure annotations are correct. 
anns = [(a.start, a.end) for a in layer.annotations()]; 
sio.savemat(pathToOutputFile+'annots.mat', {'annots':anns})
