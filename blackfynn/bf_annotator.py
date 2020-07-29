import scipy.io as sio
from blackfynn import Blackfynn

##SETTINGS:
outputPath='/Users/bscheid/Documents/LittLab/PROJECTS/p00_RNS_Project/V1'
dataset= 'N:dataset:c8a28f2d-47b7-42df-a09d-5c5d8e67fc7d'
package='N:package:d0f007da-3ebe-4c86-9667-b832c822ac84'
#Package Link
layerName='Expert Annotations'

bf = Blackfynn()
ds=bf.get_dataset(dataset)
ts=bf.get(package)
layer = ts.get_layer(layerName);

# Make sure annotations are correct. 
anns = [(a.start, a.end) for a in layer.annotations()];
desc = [(a.description) for a in layer.annotations()];
sio.savemat(outputPath+ layerName +'_annots.mat', {'annots':anns, 'descriptions': desc})

	
 