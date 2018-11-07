# -*- coding: utf-8 -*-
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on Thu May 31 10:21:09 2018

@author: a001985
"""

import codecs

def generate_yearlist_sliding_window(from_year=None, 
                                     to_year=None, 
                                     sliding_window=None, 
                                     file_path=None): 
    """
    Created 20180531    by Magnus
    
    Creates a yearlist uesd by Diva. 
    """
    yearlist = []
    current_year = from_year 
    while current_year <= (to_year-sliding_window+1): 
        year_interval = '{}{}'.format(current_year, current_year+sliding_window-1)
        print(year_interval)
        yearlist.append(year_interval)
        current_year += 1
        
    if file_path:
        with codecs.open(file_path, 'w', encoding='utf8') as fid:
            fid.write('\n'.join(yearlist))
            fid.write('\n')
    return yearlist

