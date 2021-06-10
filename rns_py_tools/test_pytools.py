#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 14:38:21 2021
test_pytools.py 

To run:
    - cd to 
    - "python -m pytest"

@author: bscheid
"""

import pytest
import numpy as np
import pandas as pd
import os
from functions import utils
from functions import NPDataHandler as npdh
#from pennsieve import Pennsieve


# Set up fixtures

@pytest.fixture
def tst_config(tmpdir):
    tst_config = dict()
    tst_config['institution']= 'sample_institution'
    tst_config['paths'] = {'RNS_RAW_Folder': os.path.join(tmpdir, "raw_data"),
                           'RNS_DATA_Folder': os.path.join(tmpdir, "data")
                           }
    tst_config['patients'] =  [{'ID': 'RNS001',
                                'PDMS_ID': '12345',
                                'Initials': 'ABC',
                                'pnsv_dataset': 'N:dataset:1234-5678-91011',
                                'pnsv_package': ' '
                                }, 
                               {'ID': 'RNS002',
                                'PDMS_ID': '97890',
                                'Initials': 'DEF',
                                'pnsv_dataset': 'N:dataset:1234-5678-91011',
                                'pnsv_package': ' '
                                }]
    
    return tst_config


@pytest.fixture
def ecog_df():
    ecog_data = [['2020-02-06 02:02:35.964', "12345.dat", 250, "On", "On", "On", "On",
                 "2020-02-06 02:03:36.000", "2020-02-06 07:03:36.000"],
                 ['2020-02-06 02:02:35.964', "DNE.dat", 250, "On", "On", "On", "On",
                 "2020-02-06 02:03:36.000", "2020-02-06 07:03:36.000"]]
    ecog_df = pd.DataFrame(ecog_data, 
                           columns=["Timestamp", "Filename","Sampling rate",
                                          "Ch 1 enabled", "Ch 2 enabled",
                                          "Ch 3 enabled", "Ch 4 enabled",
                                          "Raw local timestamp", 
                                          "Raw UTC timestamp"])
    return ecog_df

        

## UTILS TESTS ##
def test_ptIdxLookup(tst_config):
    ptID = 'RNS001'
    assert utils.ptIdxLookup(tst_config, 'ID', ptID) == 0
    
    
    

## NPDataHandler TESTS ##
def test_readDatFile(tmpdir, ecog_df):
    
    p = tmpdir.mkdir("test_dats")
    dataIn = np.array([[524,531,526,533,533,524,516,516,521,521,518],
                      [456,466,469,480,486,512,510,528,539,548,558],
                      [571,579,554,561,542,542,544,544,549,549,542],
                      [491,	493,503,502,502,513,492,496,519,529,526]],
                     dtype=np.int16)
    
    print(p)
    f = open(os.path.join(p,"12345.dat"), 'wb')
    f.write(bytes(dataIn.T.reshape(-1,1)))
    f.close()
    
    [fdata1, ftime1, t_conv1]= npdh._readDatFile(p, ecog_df.iloc[0])
    assert (fdata1 == dataIn-512).all()

def test_readDatFile_empty(tmpdir, ecog_df):
    p = tmpdir.mkdir("test_dats")
    
    with pytest.raises(Exception) as e_info:
        assert npdh._readDatFile(p, ecog_df.iloc[1])
    
    
## Pennsieve Tools TESTS ##

# Test uplooad
# Test download
    
    

    