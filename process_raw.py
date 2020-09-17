#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
% process_raw script
% ------------------------------------------------------
% Convert .DAT files to .MAT files, place in MAT_Folder
% ------------------------------------------------------

% load configuration settings

Created on Wed Sep 16 16:43:22 2020

@author: bscheid
"""

import json
import os
import scipy
from conversion import dat2vector 


with open('./config.JSON') as f:
    config= json.load(f); 
    
npts = len(config['patients'])

for i_pt in range(0,npts):
    
   prefix = '%s_%s_%s'%(config['institution'], 
                        config['patients'][i_pt]['Initials'],
                        config['patients'][i_pt]['PDMS_ID']); 
  
   dataFolder = os.path.join(config['paths']['DAT_Folder'], prefix + ' EXTERNAL #PHI', prefix + ' Data EXTERNAL #PHI');
   catalog_csv= os.path.join(config['paths']['DAT_Folder'], prefix+ ' EXTERNAL #PHI', prefix+ '_ECoG_Catalog.csv');
                             
   savepath = os.path.join(config['paths']['MAT_Folder'], '%s.mat'%config['patients'][i_pt]['RNS_ID']);
   
   # Get converted Data and Time vectors 
   [AllData, AllTime, eventIdx]= dat2vector(dataFolder, catalog_csv);
   
   scipy.io.savemat(saveas, {"AllData":AllData, "AllTime": AllTime, "eventIdx": eventIdx})
   
   
    
