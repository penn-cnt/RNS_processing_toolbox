import scipy.io as sio
from blackfynn import Blackfynn

##SETTINGS:
outputPath='/Users/bscheid/Documents/LittLab/DATA/RNS_Device/RNS009/'
dataset= 'N:dataset:c8a28f2d-47b7-42df-a09d-5c5d8e67fc7d'
package='N:package:f49305ad-face-47c8-ad36-390d5b482e9c'
#Package Link
layerName='Dr. Davis annotations'

bf = Blackfynn()
ds=bf.get_dataset(dataset)
ts=bf.get(package)
layer = ts.get_layer(layerName);

# Make sure annotations are correct. 
anns = [(a.start, a.end) for a in layer.annotations()];
desc = [(a.description) for a in layer.annotations()];
sio.savemat(outputPath+ layerName +'_annots.mat', {'annots':anns, 'descriptions': desc})

	
 