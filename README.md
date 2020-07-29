# RNS_Data_Handling

This repository contains code for processing and analyzing RNS code. 

### Conversion Tools
Raw .dat files are received from Neuropace. The .dat files can be converted into .mef files, and for uploading data and annotations to Blackfynn.	
Note, you will need acces to the Litt Lab Neuropace Google Drive folder to access the instructions.

Step 1: Convert .dat files to .mef files, follow instructions in [RNS_dat2mef_ConversionProcess](https://docs.google.com/document/d/1aXiWRMeYwVfB4AN6IHJ4NOTemEXYbyrTGBliTGvTZ8c/edit) document.  
Step 2: Upload RNS data files onto Blackfynn, follow instructions here ***!!TODO!!***  
Step 3: Upload RNS annotations onto Blackfynn, follow instructions in [RNS_annotations_to_Blackfynn](https://docs.google.com/document/d/1yuphq6hIXBlFlPky14yoIfu-UAbiahWYg3WsSE_5T18/edit) document.	 

### bf_tools: Blackfynn Interface

#### Python Environment Set-Up
Interfacing with blackfynn is accomplished using the Blackfynn Python sdk. You can create a virtual environment following the next steps, or install the dependencies in "requirements.txt" into an environment running python > 3.5. 

Create virtual environment in a bash shell, activate it, and install the requirements from "requirements.txt"

```
virtualenv env --python=python3.7
source env/bin/activate
pip install -r requirements.txt
```

#### Blackfynn interface functions

The Blackfynn interface uses many functions from the Blackfynn Python SDK. You will have to configure a Blackfynn profile from the commandline for the interface functions to work. Run the following command and follow the prompts to add API keys (generated from your online Blackfynn account). More information [here]( https://developer.blackfynn.io/python/latest/quickstart.html)

```
bf_profile create
```

bf_annotator.py: Change the output path, dataset ID, package ID, and name of the annotation layer on blackfynn to pull from. 
RNS_annotator.py: Adds annotations from an RNS patient's ECoG catalog file to a Blackfynn dataset



