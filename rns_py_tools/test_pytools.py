#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 14:38:21 2021
test_pytools.py 

To run:
    - cd to rns_py_tools
    -  python -m pytest
    - options: "-s" To capture std out, "--trace" to debug (c-cont. n-next, s-step)
    

@author: bscheid
"""

import pytest
import numpy as np
import pandas as pd
import os
from functions import utils
from functions import NPDataHandler as npdh
from process_raw import loadDeviceDataFromFiles
from functions import pennsieve_tools
import logging
import sys
from pennsieve import Pennsieve


# Set up static data 
@pytest.fixture
def exmpl_dat():
    exmpl_dat =  np.array([[524,531,526,533,533,524,516,516,521,521,518],
                          [456,466,469,480,486,512,510,528,539,548,558],
                          [571,579,554,561,542,542,544,544,549,549,542],
                          [491,	493,503,502,502,513,492,496,519,529,526]],
                         dtype=np.int16)
    return exmpl_dat
   

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
                                'pnsv_dataset': 'pytest',
                                'pnsv_package': ' '
                                }, 
                               {'ID': 'RNS002',
                                'PDMS_ID': '97890',
                                'Initials': 'DEF',
                                'pnsv_dataset': 'pytest',
                                'pnsv_package': ' '
                                }]
     
    return tst_config


@pytest.fixture
def ecog_df(tmpdir):
    
    # To add: Missing channels, out of order
    
    ecog_data = [['ABC', 12345, 111111, '2020-02-06 02:02:35.964', "12345.dat",
                  "Scheduled", 0.044, 250, 4, "On", "On", "On", "On",
                 "2020-02-06 02:02:35.980", "2020-02-06 07:02:35.980", 0.016],
                 ['ABC', 12345, 111111, '2020-02-06 02:03:35.964', "23456.dat",
                  "Scheduled", 0.044, 250, 4, "On", "On", "On", "On",
                 "2020-02-06 02:03:35.980", "2020-02-06 07:03:35.980", 0.016],
                 ['ABC', 12345, 111111, '2020-02-06 02:03:35.988', "34567.dat",
                  "Scheduled", 0.044,250, 4, "On", "On", "On", "On",            # overlaps with prev by 20 ms
                 "2020-02-06 02:03:36.004", "2020-02-06 07:03:36.004", 0.016],
                 ['ABC', 12345, 211111, '2020-02-06 02:03:36.012', "45678.dat", "Scheduled", 0.016, # Completely overlapped by prev
                  250, 4, "On", "On", "On", "On",
                 "2020-02-06 02:03:36.020", "2020-02-06 07:03:36.020", 0.008],
                 ['ABC', 12345, 211111, '2020-02-06 02:03:36.064', "56789.dat", "Scheduled", 0.044, # Only has 2 channels on
                  250, 2, "On", "Off", "Off", "On",
                 "2020-02-06 02:03:36.080", "2020-02-06 07:03:36.080", 0.016],
                 ['ABC', 12345, 211111, '2020-02-06 02:02:35.964', "DNE.dat", "Scheduled", 0.044,
                  250, 4, "On", "On", "On", "On",
                 "2020-02-06 02:02:35.980", "2020-02-06 07:02:35.980", 0.016]]
    ecog_df = pd.DataFrame(ecog_data, 
                           columns=["Initials", "Patient ID", "Device ID", "Timestamp", "Filename", "ECoG trigger",
                                    "ECoG length", "Sampling rate", "Waveform count",
                                          "Ch 1 enabled", "Ch 2 enabled",
                                          "Ch 3 enabled", "Ch 4 enabled",
                                          "Raw local timestamp", 
                                          "Raw UTC timestamp", "ECoG pre-trigger length"])
    return ecog_df     

@pytest.fixture
def tstlogger(tmpdir):
    
    logfile = os.path.join(tmpdir,'logfile.log');
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    FORMAT = '%(asctime)s %(funcName)s: %(message)s'
    logging.basicConfig(filename=logfile, level=logging.INFO, format=FORMAT)
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

## HELPER SETUP FUNCTIONS

def _setupRawDir(ptID, tst_config, tmpdir, ecog_df, exmpl_dat):
    
    #Create and populate raw directory     
    dat_pth = npdh.NPgetDataPath(ptID, tst_config, 'dat folder')
    ecog_pth = npdh.NPgetDataPath(ptID, tst_config, 'ecog catalog')
    
    p = os.path.join(tmpdir,dat_pth)
    os.makedirs(p)
    
    ecog_df = ecog_df[:-1]  # Remove last entry since it is "wrong"
    ecog_df.to_csv(ecog_pth, index=False)
    
    for i in ecog_df.Filename:
        f = open(os.path.join(p,i), 'wb')
        f.write(bytes(exmpl_dat.T.reshape(-1,1)))
        f.close()
    
    
    print(ecog_pth)
    
    return ecog_df


## UTILS TESTS ##
def test_ptIdxLookup(tst_config):
    ptID = 'RNS001'
    assert utils.ptIdxLookup(tst_config, 'ID', ptID) == 0


def test_filterWindows():
    win1 = np.array([[1,3], [6,7],
        [10,12],
        [13,16],
        [18,21],
        [24,26],
        [25,27],
        [31,32]])

    win2 = np.array([[2,4],
            [5,8],
            [9,11],
            [14,15],
            [17,20],
            [19,22],
            [23,28],
            [29, 30],
            [33,34]])

    [incl1, excl1, set2] = utils.filterWindows(win1, win2)
    [incl2, excl2, set1] = utils.filterWindows(win2, np.array([11,12,13]))
    [incl3, excl3, set3] = utils.filterWindows(win2, np.array([11,12]))

    assert(np.all(incl1 == [1,1,1,1,1,1,1,0]))
    assert(np.all(excl1 == [0,0,0,0,0,0,0,1]))
    assert(np.all(set2 == [0,0,0,1,0,0,0,0,0]))

    assert(np.all(incl2 == [0,0,1,0,0,0,0,0,0]))
    assert(np.all(excl2 == [1,1,0,1,1,1,1,1,1]))
    assert(np.all(set1 == [1,0,0]))

    assert(np.all(incl3 == [0,0,1,0,0,0,0,0,0]))
    assert(np.all(excl3 == [1,1,0,1,1,1,1,1,1]))
    assert(np.all(set3 == [1,0]))


    

#TODO: Test single and list input for converters
    

## NPDataHandler TESTS ##
def test_NPdeidentifier(tstlogger, tmpdir,tst_config, ecog_df, exmpl_dat):
    
    #Create and populate raw directory     
    ptID = 'RNS001'
    _setupRawDir(ptID, tst_config, tmpdir, ecog_df, exmpl_dat)
    
    print(tmpdir)
    
    # Test that directory can be deidentified if missing Histograms and EventDurations
    npdh.NPdeidentifier(ptID, tst_config)
    loadDeviceDataFromFiles([ptID], tst_config)

def test_NPgetDataPath(tmpdir,tst_config, ecog_df, exmpl_dat):
    
    ptID = 'RNS001'
    
    _setupRawDir(ptID, tst_config, tmpdir, ecog_df, exmpl_dat)
    
    # Check DAT path
    dat_pth = npdh.NPgetDataPath(ptID, tst_config, 'dat folder')
    expected_dat_pth = 'raw_data/sample_institution_ABC_12345 EXTERNAL #PHI/sample_institution_ABC_12345 Data EXTERNAL #PHI'
    assert(dat_pth == os.path.join(tmpdir, expected_dat_pth))
    assert(os.path.exists(os.path.join(tmpdir, expected_dat_pth)))
    
    # Check ECoG path
    ecog_pth = npdh.NPgetDataPath(ptID, tst_config, 'ecog catalog')
    expected_ecog_pth = 'raw_data/sample_institution_ABC_12345 EXTERNAL #PHI/sample_institution_ABC_12345_ECoG_Catalog.csv'
    assert(ecog_pth == os.path.join(tmpdir, expected_ecog_pth))
    assert(os.path.exists(os.path.join(tmpdir, expected_ecog_pth)))
    
    

def test_dat2mat(tst_config, tmpdir, ecog_df, exmpl_dat):
    
    ptID = 'RNS001'
    
    _setupRawDir(ptID, tst_config, tmpdir, ecog_df, exmpl_dat)
    npdh.NPdat2mat(ptID, tst_config)
    
    print(tmpdir)
    
    # TODO: test case where some .dat files are missing
        

def test_readDatFile(tmpdir, ecog_df, exmpl_dat):
    
    p = tmpdir.mkdir("test_dats")

    print(p)
    f = open(os.path.join(p,"12345.dat"), 'wb')
    f.write(bytes(exmpl_dat.T.reshape(-1,1)))
    f.close()
    
    [fdata1, ftime1, t_conv1]= npdh._readDatFile(p, ecog_df.iloc[[0]])
    assert (fdata1 == exmpl_dat-512).all()

def test_readDatFile_empty(tmpdir, ecog_df):
    p = tmpdir.mkdir("test_dats")
    
    with pytest.raises(Exception):
        assert npdh._readDatFile(p, ecog_df.iloc[[1]])
        

def test_createConcatDatLayFiles(tmpdir, tst_config, ecog_df, exmpl_dat):
    
    # Setup
    ptID = 'RNS001'
    dat_pth = npdh.NPgetDataPath(ptID, tst_config, 'dat folder')
    newpath = os.path.join(tmpdir, 'test_dats')
    
    p = os.path.join(tmpdir,dat_pth)
    
    os.makedirs(p)
    tmpdir.mkdir('test_dats')
    print(p)
    with open(os.path.join(p,"12345.dat"), 'wb') as f:
        f.write(bytes(exmpl_dat.T.reshape(-1,1)))
        
    # Test when a .dat files are missing from folder
    print('test01_concat')
    rm_dict1 = npdh.createConcatDatLayFiles(ptID, tst_config, ecog_df.iloc[0:-1], 'test01_concat', newpath)
    assert rm_dict1 == {}
    assert os.path.getsize(os.path.join(tmpdir,'test_dats','test01_concat.dat')) == os.path.getsize(os.path.join(p,"12345.dat"))
        
    with open(os.path.join(p,"23456.dat"), 'wb') as f:
        f.write(bytes(exmpl_dat.T.reshape(-1,1)))
        
    with open(os.path.join(p,"34567.dat"), 'wb') as f:
        f.write(bytes(exmpl_dat.T.reshape(-1,1)))
        
    with open(os.path.join(p,"45678.dat"), 'wb') as f:
        short_exmpl= exmpl_dat[:,1:5]
        f.write(bytes(short_exmpl.T.reshape(-1,1)))
        
    with open(os.path.join(p,"56789.dat"), 'wb') as f:
        two_chan_exmpl= exmpl_dat[1:3,:]
        f.write(bytes(two_chan_exmpl.T.reshape(-1,1)))
        
        
    # Test concatenation when overlap exists 
    print('test02_concat')
    rm_dict2 = npdh.createConcatDatLayFiles(ptID, tst_config, ecog_df.iloc[0:-1], 'test02_concat', newpath)
    assert rm_dict2 == {'34567.dat': 40.0, '45678.dat': 32.0}
    assert os.path.getsize(os.path.join(tmpdir,'test_dats','test02_concat.dat')) == 88*4-40 
      
    # Test with one file 
    print('test03_concat')
    rm_dict3 = npdh.createConcatDatLayFiles(ptID, tst_config, ecog_df.iloc[0:1], 'test03_concat', newpath)
    assert rm_dict3 == {}
    assert os.path.getsize(os.path.join(tmpdir,'test_dats','test03_concat.dat')) == os.path.getsize(os.path.join(p,"12345.dat"))
    
def test_getOffChs(ecog_df):
    ch = npdh._getOffChs(ecog_df, "12345.dat")
    print(ch)


def test_getTimeStrings(ecog_df):
    # Test getTimeStrings for single and multiple ros
    
    # Test single input:
    ecog_df_row = ecog_df.iloc[[0]]
    one_out = npdh._getTimeStrings(ecog_df_row)
    
    assert all(isinstance(x, list) for x in one_out)
    assert one_out[0][0] == 1580972555964000
    assert one_out[1][0] == 1580972555980000
    assert one_out[2][0] == 1580954555980000
    assert one_out[3][0] == 18000000000
    
    # Test multiple row input:
    ecog_df_row = ecog_df.iloc[[0,1]]
    multi_out = npdh._getTimeStrings(ecog_df_row)
    
    assert all(isinstance(x, list) for x in multi_out)
    
    assert one_out[0][0] == 1580972555964000
    assert one_out[1][0] == 1580972555980000
    assert one_out[2][0] == 1580954555980000
    assert one_out[3][0] == 18000000000
    
    # Test incorrect input type
    with pytest.raises(Exception):
        assert npdh._getTimeStrings(ecog_df.iloc[0])
    
    
    
    
## Pennsieve Tools TESTS ##

# # Test uplooad
# def test_Pennsieve_layer_tools(tst_config, tmpdir, ecog_df, exmpl_dat):
   
#     pnsv = Pennsieve()
#     ptID = 'RNS001'
#     layerName = 'test_layer'
    
#     _setupRawDir(ptID, tst_config, tmpdir, ecog_df, exmpl_dat)
    
#     # Upload example dat
#     pennsieve_tools.uploadNewDatByMonth(ptID, tst_config, pnsv)
#     ds = pnsv.get_dataset("pytest")
#     assert(ds.name == "pytest")
    
#    # uploadSingleDat(ptID, tst_config, pnsv)
    
#     # Process TimeSeries
#     #pennsieve_tools.processPatientTimeseries(ptID, tst_config, pnsv)
    
#     # Add Annotations
#     annotComplete = pennsieve_tools.annotate_UTC_from_catalog(ptID, tst_config, pnsv)
#     col = ds.items[0]
#     ts = col.items[0]
#     isReady = (ts.state == 'READY')
#     assert(annotComplete == isReady)
    
#     # Add Layer
    
    # Delete Layers
    
    # Delete dataset
    
    # pnsv.delete(ds.id)
    # dsetNames = [x.name for x in pnsv.datasets()]
    # assert("pytest" not in dsetNames)
    
    
    #pennsieve_tools.add_empty_layer(ptID, tst_config, layerName, pnsv)
    
    

# Test download
# Test 
    
    

    