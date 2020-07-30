# RNS processing toolbox

This repository contains code for processing and analyzing data from the responsive neurostimulation (RNS) device by NeuroPace. 

### Requirements

Python > 3.5    
Matlab > 2018a    
blackfynn == 4.0.0   

### Set-Up

Add data path settings and patient information to config.JSON. 
Raw data folders are expected to be arranged according to the NeuroPace documentation.

#### Prepare python environment

Create a new virtual environment or conda environment: 
 
```
virtualenv env --python=python3.7
source env/bin/activate
pip install -r requirements.txt
```

If using blackfynn profile following the instructions [here]( https://developer.blackfynn.io/python/latest/quickstart.html)

### Pipelines

- Blackfynn pipeline: load data from raw .dat files, load annoataions, download annotations for local processing. 
- Matlab pipeline: convert .dat files to .mat files

### bf_tools: blackfynn interface

bf_annotator.py: Change the output path, dataset ID, package ID, and name of the annotation layer on blackfynn to pull from.  
bf_data_interface.py: Adds annotations from an RNS patient's ECoG catalog file to a Blackfynn dataset

### conversion
Tools for converting raw data files (in .dat format) to other formats

- dat2mef
- dat2vector





