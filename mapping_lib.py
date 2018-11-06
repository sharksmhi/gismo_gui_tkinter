# -*- coding: utf-8 -*-
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on Thu Aug 30 15:53:08 2018

@author: a001985
"""
import os 
import pandas as pd 
import datetime
import numpy as np

class ParameterMapping():
    
    def __init__(self, file_path=None, from_col=None, to_col=None, **kwargs): 
        
        if not file_path:
            return False

        kw = {'sep': '\t', 
              'encoding': 'cp1252'} 
        kw.update(kwargs)
        
        self.from_col = from_col 
        self.to_col = to_col
        
        self.df = pd.read_csv(file_path, **kw) 
        
        
    def get_mapping(self, item, from_col=None, to_col=None): 
        if not from_col:
            from_col = self.from_col
        if not to_col:
            to_col = self.to_col 
            
        result = self.df.loc[self.df[from_col] == item, to_col]
        if len(result):
            return result.values[0]
        else: 
            return item
        
        
        
def to_decmin(pos):
    """
    Converts a position form decimal degree to decimal minute. 
    """
    pos = float(strip_position(pos))
    deg = np.floor(pos)
    dec_deg = pos-deg
    minute = 60 * dec_deg 
    
    deg_str = str(int(deg))
    minute_str = str(minute)
    if deg < 10: 
        deg_str = '0' + deg_str
    
    if minute < 10:
        minute_str = '0' + minute_str
    #print(minute)
    
    return deg_str + minute_str
    #print(new_lat)
    
    
def strip_position(pos):
    """
    Stripes position from +- and blankspaces. 
    """
    pos = str(pos)
    return pos.strip(' +-').replace(' ', '')
    
    
    
def split_date(date): 
    """
    Splits date from format %y%m%d to %y-%m-%d
    """
    
    date = str(date) 
    y = date[:4]
    m = date[4:6]
    d = date[6:]
    return '-'.join([y, m, d]) 



def datetime_from_odv(odv_time_string, apply_function=None): 
    """
    Converts an ODV time string to a datetime object. 
    The ODV time format is "yyyy-mm-ddThh:mm:ss.sss" or parts of it
    """
    parts = []
    T_parts = odv_time_string.split('T') 
    parts.extend(T_parts[0].split('-'))
    if len(T_parts) == 2: 
        time_parts = T_parts[1]. split(':')
        if len(time_parts) == 3 and '.' in time_parts[-1]: 
            time_parts = time_parts[:2] + time_parts[-1].split('.') 
        parts.extend(time_parts) 
    
    parts = [int(p) for p in parts]
    return datetime.datetime(*parts) 


def sdate_from_odv_time_string(odv_time_string): 
    return odv_time_string.split('T')[0]


def stime_from_odv_time_string(odv_time_string): 
    T_parts = odv_time_string.split('T') 
    if len(T_parts) == 2:
        return T_parts[1][:5]
    else:
        return ''
    

def sdate_from_datetime(datetime_object, format='%y-%m-%d'): 
    """
    Converts a datetime object to SDATE string. 
    """ 
    return datetime_object.strftime(format)



def stime_from_datetime(datetime_object, format='%H:%M'): 
    """
    Converts a datetime object to STIME string. 
    """ 
    return datetime_object.strftime(format)
    
    
    
    
    
    
    
    
    
    