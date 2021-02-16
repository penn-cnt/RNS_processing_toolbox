#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 14:38:21 2021
test_pytools.py 

To run: "python -m pytest"

@author: bscheid
"""

import pytest
from rns_py_tools import utils


# Set up fixtures

@pytest.fixture
def tst_config():
    tst_config = dict()
    tst_config['institution']= 'sample_institution'
    tst_config['paths'] = {'RNS_RAW_Folder': 'tests/exampleRaw',
                           'RNS_DATA_Folder': '/tmp'
                           }
    tst_config['patients'] =  [{'ID': 'RNS001',
                                'PDMS_ID': '12345',
                                'Initials': 'ABC',
                                'bf_dataset': 'N:dataset:1234-5678-91011',
                                'bf_package': ' '
                                }, 
                               {'ID': 'RNS002',
                                'PDMS_ID': '97890',
                                'Initials': 'DEF',
                                'bf_dataset': 'N:dataset:1234-5678-91011',
                                'bf_package': ' '
                                }]
    
    return tst_config
    

def test_ptIdxLookup(tst_config):
    ptID = 'RNS001'
    assert utils.ptIdxLookup(tst_config, 'ID', ptID) == 0
    

    