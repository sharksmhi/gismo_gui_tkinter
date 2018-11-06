# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
'''
Created on 30 jun 2016

@author: a001985
'''

#import urllib2
import numpy as np
#from openpyxl import Workbook
import codecs
import re
import os
import time 
import pandas as pd 
import datetime
import time
import sys

odv_directory_path = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.dirname(odv_directory_path)
if lib_path not in sys.path:
    sys.path.append(lib_path)

import mapping_lib as mapping
import geography




"""
===============================================================================
===============================================================================
"""
class SpreadsheetFile():
    """
    Class to hande vocabulary things in ODV spreadsheet file
    """
    
    #==========================================================================
    def __init__(self, file_path=None): 
        
        self.file_path = file_path
         

    #==========================================================================
    def set_negative_value_to_zero(self, output_file_path):
        re_string = '\t-.+?\t'
        
        fid = codecs.open(self.file_path, 'r')
        fid_out = codecs.open(output_file_path, 'w')
        for line in fid:
            fid_out.write(re.sub(re_string, u'\t0\t', line))
        fid.close()
        fid_out.close()
                
    #==========================================================================
    def get_local_cdi_list(self, print_to_file='', show_process_every=100000): 
        """
        Created:    20180523
        Updated:    20180613
        
        Returns a list of all local_cdi_id:s found in the spreadseet file
        """
        t0 = time.time()
        cdi_set = set()
        print('='*50)
        print(self.file_path)
        print('-'*50)
        with codecs.open(self.file_path) as fid: 
            for k, line in enumerate(fid): 
                if show_process_every:
                    if not k%show_process_every:
                        print('Working on line {} as time {}'.format(k, time.time()-t0))
                if line.startswith('//'):
                    continue
                elif line.startswith('Cruise'):
                    continue 
                else:
                    split_line = line.split('\t')
                    if split_line[0].strip(): # added by MW 20180613
                        cdi_set.add(split_line[6])
        if show_process_every:
            print('Number of lines: {}'.format(k))
            print('Number of local_cdi_id is: {}'.format(len(cdi_set)))
            
        sorted_cdi_set = sorted(cdi_set)
        if print_to_file:
            with codecs.open(print_to_file, 'w') as fid:
                fid.write('\n'.join(sorted_cdi_set))
        return sorted_cdi_set
    
    
    #==========================================================================
    def get_odv_station_count(self, show_process_every=100000): 
        """
        Created:    20180613    by Magnus
        Updated:    
        
        Returns the number of stations acording to odv. 
        A station is identified as a non comment (or Cruise) row having value in first column (Cruise). 
        """
        t0 = time.time()
        nr_stations = 0
        print('='*50)
        print(self.file_path)
        print('-'*50)
        with codecs.open(self.file_path) as fid: 
            for k, line in enumerate(fid): 
                if show_process_every:
                    if not k%show_process_every:
                        print('Working on line {} as time {}'.format(k, time.time()-t0))
                if line.startswith('//'):
                    continue
                elif line.startswith('Cruise'):
                    continue
                else:
                    split_line = line.split('\t')
                    if split_line[0].strip(): 
                        nr_stations += 1
        if show_process_every:
            print('Number of lines: {}'.format(k))
            
        return nr_stations



    #==========================================================================
    def get_unique_list(self, col, print_to_file='', show_process_every=100000, **kwargs):
        """
        Created:    20180605
        Updated:    20181010
        
        Returns a list of all unique values of the given column in the spreadseet file
        """
        t0 = time.time()
        data_set = set()
        if show_process_every:
            print('='*50)
            print(self.file_path)
            print('-'*50)
        with codecs.open(self.file_path, encoding=kwargs.get('encoding', 'utf8')) as fid:
            for k, line in enumerate(fid): 
                if show_process_every:
                    if not k%show_process_every:
                        print('Working on line {} as time {}'.format(k, time.time()-t0))
                if line.startswith('//'):
                    continue
                elif line.startswith('Cruise'):
                    header = line.split('\t')
                    if col == 'id':
                        continue
                    else:
                        if col not in header:
                            print('Column "{}" not in header!'.format(col))
                            return False
                        index = header.index(col)
                    continue
                else:
                    split_line = line.split('\t')
                    if kwargs.get('metadata') and not split_line[0]:
                        continue
                    if col == 'id':
                        # Combine several columns
                        data_set_list = []
                        time_string = split_line[header.index('yyyy-mm-ddThh:mm:ss.sss')]
                        if not time_string.strip():
                            continue
                        try:
                            time_object = get_datetime_object(time_string)
                        except:
                            print(self.file_path)
                            print('k', k)
                            print(time_string)

                        data_set_list.append(time_object.strftime('%Y-%m-%d'))
                        if kwargs.get('include_time', True):
                            data_set_list.append(time_object.strftime('%H:%M'))
                        else:
                            data_set_list.append('')
                        # print(header.index('Latitude [degrees_north]'))
                        # print(split_line[header.index('Latitude [degrees_north]')])
                        # print(split_line)

                        lat = str(mapping.to_decmin(mapping.sdate_from_odv_time_string(split_line[header.index('Latitude [degrees_north]')])))[:kwargs.get('id_pos_precision', 6)]
                        lon = str(mapping.to_decmin(mapping.sdate_from_odv_time_string(split_line[header.index('Longitude [degrees_east]')])))[:kwargs.get('id_pos_precision', 6)]

                        # lat = geography.decdeg_to_decmin(split_line[header.index('Latitude [degrees_north]')], string_type=True)[:kwargs.get('id_pos_precision', 6)]
                        # lon = geography.decdeg_to_decmin(split_line[header.index('Longitude [degrees_east]')], string_type=True)[:kwargs.get('id_pos_precision', 6)]
                        data_set_list.append(lat)
                        data_set_list.append(lon)
                        data_set.add('_'.join(data_set_list))
                    else:
                        if not split_line[index]:
                            print(k)
                        data_set.add(split_line[index])
        if show_process_every:
            print('Number of lines: {}'.format(k))
            print('Number of "{}" is: {}'.format(col, len(data_set)))
            
        sorted_data_set = sorted(data_set)
        if print_to_file:
            with codecs.open(print_to_file, 'w') as fid:
                fid.write('\n'.join(sorted_data_set))
        return sorted_data_set

    # ==========================================================================
    def get_vocab_list(self, vocab='P01', sort=False, save_file_path=None, **kwargs):
        """
        Function to create P01 list from txt-files.
        """
        vocab_code_list = []

        with codecs.open(self.file_path, 'r', encoding=kwargs.get('encoding', 'utf8')) as fid:
            for line in fid:
                if line.startswith(u'Cruise'):
                    break
                try:
                    re_string = '(?<={}::)[ ]*[A-Z0-9]+'.format(vocab.upper())
                    vocab_string = re.findall(re_string, line)[0].strip()
                    vocab_code = vocab_string.split(u':')[-1]
                    if not vocab_code:
                        print(line)
                    vocab_code_list.append(vocab_code)
                except:
                    pass

        vocab_code_list = list(set(vocab_code_list))
        if sort:
            vocab_code_list = sorted(vocab_code_list)

        if save_file_path:
            with codecs.open(save_file_path, 'w') as fid:
                fid.write('\n'.join(vocab_code_list))

        return vocab_code_list
        
    #==========================================================================
    def create_row_data(self, print_to_file='', show_process_every=1000, **kwargs): 
        """
        Created:    20180831
        Updated:    
        
        Extracts data in a row data format. 
        """ 
        t0 = time.time() 
        metadata_dict = {}
        data_dict = {}
        
        data = [] 
        current_metadata_list = [] 
        current_metadata_dict = {}
        keep_pars = kwargs.get('keep_as_id', [])
        if type(keep_pars) != list:
            keep_pars = [keep_pars]
        vocab_dict = {}
        with codecs.open(self.file_path, encoding='utf8') as fid: 
            for k, line in enumerate(fid): 
                if show_process_every:
                    if not k%show_process_every:
                        print('Working on line {} as time {}'.format(k, time.time()-t0)) 
                if line.startswith('//<MetaVariable>'): 
                    par = line.split('="')[1].split('"')[0]
                    metadata_dict[par] = False 
                    metadata_dict['yyyy-mm-ddThh:mm:ss.sss'] = False  
                elif line.startswith('//<DataVariable>'): 
                    par = line.split('="')[1].split('"')[0]
                    # Check primary variable
                    if 'is_primary_variable="T"' in line:
                        metadata_dict[par] = False 
                    else:
                        data_dict[par] = False 
                        vocab_dict[par] = get_vocabs_from_string(line)
#                    nr_metadata_rows += 1
                elif line.startswith('//'):
                    continue 
                elif line.startswith('Cruise'):
                    header = line.split('\t') 
                    
#                     header_dict = dict((item, k) for k, item in enumerate(header)) 
                    
                    # Find columns for data and metadata 
#                     for key in metadata_dict.keys():
#                         metadata_dict[key] = header_dict[key]
#                     for key in data_dict.keys():
#                         data_dict[key] = header_dict[key]
                        
                    # Check which vocabularies to add. Needs to be done after Data variable check 
                    vocab_set = set()
                    for par in vocab_dict:
                        vocab_set.update(vocab_dict[par].keys())
                    vocab_list = sorted(vocab_set)
                     
                else:
                    split_line = line.split('\t') 
                    line_dict = dict(zip(header, split_line))
                    # Save metadata line 
                    if split_line[3]: # time
                        for item in metadata_dict: 
                            current_metadata_dict[item] = line_dict[item]
                    else:
                        for item in metadata_dict: 
                            line_dict[item] = current_metadata_dict[item]
                            
                     
#                     print(split_line)
#                     # Update metadata. If metadata variable is missing the previos metadata is used
#                     for item in metadata_dict:
#                         print(item)
#                         if not line_dict[item]:
#                             line_dict[item] = current_metadata_dict[item]
#                         else: 
#                             current_metadata_dict[item] = line_dict[item]
                               
                               
                    
                            
#                     # Add keep parameters. They will be unique for each row 
#                     for par in keep_pars: 
#                         data_line.append(line_dict[par])
                    
#                     if split_line[metadata_dict['Station']]: 
#                         # First row for station. Add information to be used on the rest of the lines 
#                         current_metadata_list = split_line[:len(metadata_dict)] 
                    
                    
                    # Add data 
                    for par in sorted(data_dict):
                        data_line = []
                        # Add metadata 
                        for item in header: # To get the right order 
                            if item in metadata_dict:
                                data_line.append(line_dict[item]) 
                        
                        # Add data from line
                        
#                         # Metadata first 
#                         data_line = current_metadata_list[:] 
                        
                        # Then vocabulary 
                        for voc in vocab_list:
                            data_line.append(vocab_dict.get(par, {}).get(voc, ''))
                        
                        # Then data
                        data_line.append(par)                           # Parameter
                        data_line.append(split_line[data_dict[par]])    # Value     
                        data_line.append(split_line[data_dict[par]+1])  # QF 

                        # Add line to data
#                         print(len(data_line))
                        data.append(data_line)


        # Create dataframe  
        data_header = [item for item in header if item in metadata_dict] + vocab_list + ['parameter', 'value', 'qflag']
#         print(len(data_header), len(data[0]))
        self.row_df = pd.DataFrame(data, columns=data_header) 
        
        
        # Map header 
        mapping_file_path = os.path.join(odv_directory_path, 'odv_parameter_mapping.txt')
        parameter_mapping = mapping.ParameterMapping(mapping_file_path, from_col='ODV', to_col='SMHI')
        new_header = [parameter_mapping.get_mapping(item) for item in self.row_df.columns] 
        
        self.row_df.columns = new_header 
#         for par in sorted(self.row_df.columns): 
#             print(par)

        # Refine data 
        for key in kwargs: 
            if key in self.row_df.columns: 
                value = kwargs[key] 
                if type(value) == str:
                    value = [value]
                self.row_df = self.row_df.loc[self.row_df[key].isin(value), :]
            
        self.data_dict = data_dict
        self.metadata_dict = metadata_dict
        
        # Add columns 
        self.row_df['SDATE'] = self.row_df['odv_time_string'].apply(mapping.sdate_from_odv_time_string)
        self.row_df['STIME'] = self.row_df['odv_time_string'].apply(mapping.stime_from_odv_time_string) 
        
        # Convert lat lon 
        self.row_df['LATIT'] = self.row_df['LATIT'].apply(mapping.to_decmin)
        self.row_df['LONGI'] = self.row_df['LONGI'].apply(mapping.to_decmin)

        # Add MYEAR
        if kwargs.get('add_myear'):
            self.row_df['MYEAR'] = self.row_df['SDATE'].apply(lambda x: int(x[:4]))

        # Add source column
        self.row_df['source'] = kwargs.get('source', kwargs.get('source_column', 'odv'))
        
        self._add_id_column()
        
        
        if print_to_file:
            kw = {'sep': '\t', 
                  'encoding': 'cp1252', 
                  'index': False}
            for k in kw:
                if k in kwargs:
                    kw[k] = kwargs[k]
                    
            self.row_df.to_csv(print_to_file, **kw)
        
        
    #==========================================================================
    def _add_id_column(self): 
        self.row_df['id'] = self.row_df['SDATE'].astype(str) + '_' + \
                            self.row_df['STIME'].astype(str) + '_' + \
                            self.row_df['LATIT'].apply(lambda x: x[:7]).astype(str) + '_' + \
                            self.row_df['LONGI'].apply(lambda x: x[:7]).astype(str)
        # astype(str) ???


"""
===============================================================================
===============================================================================
"""


class SpreadsheetFileColumns():
    """
    Class takes an ODV spreadsheet file, removes all comment lines and reads as pandas dataframe.
    OBS! Make sure NOT to "Use compact output".
    """

    # ==========================================================================
    def __init__(self, file_path=None, **kwargs):
        self.file_path = file_path
        self._load_data()
        self._add_columns(**kwargs)

    def _load_data(self):
        if type(self.file_path) == list:
            self._load_several_files()
            return

        data_lines = []
        print('utf8')
        with codecs.open(self.file_path, encoding='utf8') as fid:
            for line in fid:
                if line.startswith('//'):
                    continue
                else:
                    split_line = line.strip().split('\t')
                    if line.startswith('Cruise'):
                        # Header
                        header = split_line
                    else:
                        # Data line
                        data_lines.append(split_line)

        self.df = pd.DataFrame(data_lines, columns=header)


    def _load_several_files(self):
        dfs = {}
        headers = {}
        for file_path in self.file_path:
            data_lines = []
            with codecs.open(file_path, encoding='utf8') as fid:
                for line in fid:
                    if line.startswith('//'):
                        continue
                    else:
                        split_line = line.strip().split('\t')
                        if line.startswith('Cruise'):
                            # Header
                            header = split_line
                            new_header = []
                            latest = None
                            for h in header:
                                if h == 'QV:SEADATANET':
                                    new_header.append(' - '.join([latest, h]))
                                else:
                                    latest = h
                                    new_header.append(h)
                            headers[file_path] = new_header
                        else:
                            # Data line
                            data_lines.append(split_line)
            dfs[file_path] = pd.DataFrame(data_lines, columns=new_header)

        header_list = []
        for h in headers:
            header_list.extend(headers[h])
        header_list = sorted(set(header_list))

        for item in dfs:
            for h in header_list:
                if h not in dfs[item].columns:
                    dfs[item][h] = ''
        self.header_list = header_list
        # self.dfs = dfs
        self.df = None
        for item in dfs:
            df = dfs[item].copy(deep=True)[header_list]
            if self.df is None:
                self.df = df
            else:
                # return
                self.df = self.df.append(df)


    def _add_columns(self, **kwargs):
        # Add columns
        self.df['SDATE'] = self.df['yyyy-mm-ddThh:mm:ss.sss'].apply(mapping.sdate_from_odv_time_string)
        self.df['STIME'] = self.df['yyyy-mm-ddThh:mm:ss.sss'].apply(mapping.stime_from_odv_time_string)

        self.df['time'] = pd.to_datetime(self.df['yyyy-mm-ddThh:mm:ss.sss'].apply(get_datetime_object))

        # Convert lat lon

        self.df['LATIT_decdeg'] = self.df['Latitude [degrees_north]']
        self.df['LONGI_decdeg'] = self.df['Longitude [degrees_east]']
        self.df['LATIT'] = self.df['LATIT_decdeg'].apply(mapping.to_decmin)
        self.df['LONGI'] = self.df['LONGI_decdeg'].apply(mapping.to_decmin)
        self.df['STATN'] = self.df['Station']

        # Add MYEAR
        self.df['MYEAR'] = self.df['SDATE'].apply(lambda x: int(x[:4]))

        # Add source column
        self.df['source'] = 'ODV'
        # self.df['source'] = 'ODV: {}'.format(os.path.basename(self.file_path))

        # Add id column
        if kwargs.get('include_time_in_id', True):
            self.df['id'] = self.df['SDATE'].astype(str) + '_' + \
                                self.df['STIME'].astype(str) + '_' + \
                                self.df['LATIT'].apply(lambda x: x[:kwargs.get('id_pos_precision', 6)]).astype(str) + '_' + \
                                self.df['LONGI'].apply(lambda x: x[:kwargs.get('id_pos_precision', 6)]).astype(str)

            self.df['station_id'] = self.df['SDATE'].astype(str) + '_' + \
                                    self.df['STIME'].astype(str) + '_' + \
                                    self.df['STATN']
        else:
            self.df['id'] = self.df['SDATE'].astype(str) + '_' + \
                                self.df['LATIT'].apply(lambda x: x[:kwargs.get('id_pos_precision', 6)]).astype(str) + '_' + \
                                self.df['LONGI'].apply(lambda x: x[:kwargs.get('id_pos_precision', 6)]).astype(str)

            self.df['station_id'] = self.df['SDATE'].astype(str) + '_' + \
                                    self.df['STATN']

"""
===============================================================================
===============================================================================
"""       
def get_vocabs_from_string(string): 
    """
    Search in the string to find BODC vocabularies (P01, P06 etc. 
    Returns a dict where: 
        key = vocabulary 
        value = code 
    """
    result = re.findall('SDN:[A-Z0-9]*::[A-Z0-9]*', string) 
    vocabs = {}
    for item in result: 
        split_item = item.split(':')
        vocabs[split_item[1]] = split_item[3]
        
    return vocabs 


            
"""
===============================================================================
===============================================================================
"""
def compare_non_matching_local_cdi_id(directory='', 
                                      spreadsheet_file_name_1=None, 
                                      spreadsheet_file_name_2=None, 
                                      print_to_files=False): 
    """
    Created:    20180523
    Updated:    
    
    Compares the local_cdi_ids in two spreadsheet files. 
    input files needs to be in the same directory. 
    Returns a dict with the result. 
    Prints to files in print_to_files=True 
    """
    result = {}
    
    base_1 = spreadsheet_file_name_1.split('.')[0]
    base_2 = spreadsheet_file_name_2.split('.')[0]
    
    spreadsheet_file_path_1 = os.path.join(directory, spreadsheet_file_name_1)
    spreadsheet_file_path_2 = os.path.join(directory, spreadsheet_file_name_2)
    
    object_1 = SpreadsheetFile(spreadsheet_file_path_1)
    object_2 = SpreadsheetFile(spreadsheet_file_path_2) 
    
    cdi_list_1 = object_1.get_local_cdi_list()
    print('= Done getting first list!')
    cdi_list_2 = object_2.get_local_cdi_list()
    print('= Done getting second list!')
    
    result['cdi_id_list_' + base_1] = cdi_list_1
    result['cdi_id_list_' + base_2] = cdi_list_2
    
    # Check 2 not in 1  
    cdi_not_in_1 = set()
    for cdi in cdi_list_2:
        if cdi not in cdi_list_1:
            cdi_not_in_1.add(cdi)
    cdi_not_in_1 = sorted(cdi_not_in_1)
    print('Nr of local_cdi_id not in file 1: {}'.format(len(cdi_not_in_1))) 
    result['cdi_id_not_in_' + base_1] = cdi_not_in_1
    
    t0 = time.time()
    # Check 1 not in 2 
    cdi_not_in_2 = set()
#    print(type(cdi_not_in_2))
    for cdi in cdi_list_1:
        if cdi not in cdi_list_2:
#            print(type(cdi_not_in_2))
            cdi_not_in_2.add(cdi)
    print('TIME:', time.time()-t0)
    cdi_not_in_2 = sorted(cdi_not_in_2)
    print('Nr of local_cdi_id not in file 1: {}'.format(len(cdi_not_in_2))) 
    result['cdi_id_not_in_' + base_2] = cdi_not_in_2
          
    if print_to_files:
        for key in result:
            file_name = os.path.join(directory, key+'.txt')
            with codecs.open(file_name, 'w') as fid: 
                fid.write('\n'.join(result[key]))
    

    return result


# ==========================================================================
def get_datetime_object(time_string):
    for time_format in ['%Y-%m-%dT%H:%M:%S',
                        '%Y-%m-%dT%H:%S',
                        '%Y-%m-%d',
                        '%Y-%m-%dT',
                        '%Y-%m-%dT%H']:
        try:
            return datetime.datetime.strptime(time_string, time_format)
        except:
            pass
    print(time_string, )
    raise ValueError

            