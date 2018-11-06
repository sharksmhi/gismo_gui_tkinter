# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on Thu Aug 30 15:30:28 2018

@author:
"""

import os
import pandas as pd 
import codecs
import datetime

import mapping_lib as mapping


class CodeList(dict): 
    def __init__(self, file_path=False): 
        if not file_path:
            file_path = os.path.dirname(os.path.abspath(__file__)) + '/ices_codelist.txt' 
                                       
        self.file_path = file_path
        self.df = pd.read_csv(file_path, sep='\t', encoding='cp1252', dtype=str)  


    #==========================================================================
    def get_mapping_dict(self, f='ices_code', t='ices_description'): 
        return dict(zip(self.df[f], self.df[t]))        



#==============================================================================
#==============================================================================
class ImportMapping(dict): 
    def __init__(self, file_path=False): 
        if not file_path:
            file_path = os.path.dirname(os.path.abspath(__file__)) + '/ices_import_contaminants.txt' 
                                       
        self.file_path = file_path
        self.df = pd.read_csv(file_path, sep='\t', encoding='cp1252', dtype=str)
        self.df.fillna('', inplace=True)
        self.df['column'] = self.df['column'].apply(self._convert_to_int)
        self.df['parent_code'] = self.df['parent_code'].apply(self._convert_to_double_digit_string)
        self.df['ices_code'] = self.df['ices_code'].apply(self._convert_to_double_digit_string) 
        
        
    #==========================================================================
    def _convert_to_int(self, x):
        try:
            x = int(x)
        except:
            pass
        return x
    
    
    #==========================================================================
    def _convert_to_double_digit_string(self, x):
        try:
            x = int(x)
            x = str(x).rjust(2, '0')
        except:
            pass
        return x
    
    
    #==========================================================================
    def is_parent(self, item): 
        """
        Checks if item is present in the parent_code-column. 
        """
        if len(self.df.loc[self.df['parent_code']==item, :]): 
            return True
        return False
    
    
    #==========================================================================
    def get_internal_name_to_column_dict(self, parent=False): 
        if parent:
            df = self.df.loc[self.df['parent_code']==parent, :] 
            return dict(zip(df['internal_name'], df['column'])) 
        else: 
            return_dict = {}
            for parent_code in set(self.df['parent_code'].values):
                if not parent_code:
                    continue
                df = self.df.loc[self.df['parent_code']==parent_code, :] 
                return_dict[parent_code] = dict(zip(df['internal_name'], df['column']))
            return return_dict 
        
        
    #==========================================================================
    def get_mapping_dict(self, f='ices_code', t='internal_name'): 
        return dict(zip(self.df[f], self.df[t]))
    
    
    #==========================================================================
    def get_parameter_list(self):
        return list(self.df.loc[self.df['parent_code'] != '', 'internal_name'])
        


#==============================================================================
#==============================================================================
class ICEScontaminants(): 
    def __init__(self, file_path, sep=',', **kwargs): 
        self.import_mapping = ImportMapping(file_path=kwargs.get('ices_import_mapping_file_path'))
        self.codelist = CodeList(file_path=kwargs.get('ices_codelist_file_path'))
        
        self.mapping_parents = self.import_mapping.get_internal_name_to_column_dict() 
        self.mapping_label = self.codelist.get_mapping_dict()
        
        self.parameter_list = self.import_mapping.get_parameter_list() 
        
        
        
        self.data_matrix = []
        if type(file_path) == str:
            self._add_file(file_path, sep=sep, **kwargs)
        else:
            for f in file_path:
                self._add_file(f, sep=sep, **kwargs)

        self.row_df = pd.DataFrame(self.data_matrix, columns=self.parameter_list)
        
        # Convert columns
        self.row_df['SDATE'] = self.row_df['SDATE'].apply(mapping.split_date)
        self.row_df['LATIT'] = self.row_df['LATIT'].apply(mapping.strip_position)
        self.row_df['LONGI'] = self.row_df['LONGI'].apply(mapping.strip_position)

        self.row_df['time'] = pd.to_datetime(self.row_df['SDATE'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')))

        # Add source column
        self.row_df['source'] = 'ices'
        
        self._add_id_column(**kwargs)
        
        print('\n== DONE ==')
        
        
    #==========================================================================
    def _add_id_column(self, **kwargs):
        if kwargs.get('include_time_in_id', True):
            self.row_df['id'] = self.row_df['SDATE'].astype(str) + '_' + \
                                self.row_df['STIME'].astype(str) + '_' + \
                                self.row_df['LATIT'].apply(lambda x: x[:kwargs.get('id_pos_precision', 6)]).astype(str) + '_' + \
                                self.row_df['LONGI'].apply(lambda x: x[:kwargs.get('id_pos_precision', 6)]).astype(str)

            self.row_df['station_id'] = self.row_df['SDATE'].astype(str) + '_' + \
                                        self.row_df['STIME'].astype(str) + '_' + \
                                        self.row_df['STATN']
        else:
            self.row_df['id'] = self.row_df['SDATE'].astype(str) + '_' + \
                                self.row_df['LATIT'].apply(lambda x: x[:kwargs.get('id_pos_precision', 6)]).astype(str) + '_' + \
                                self.row_df['LONGI'].apply(lambda x: x[:kwargs.get('id_pos_precision', 6)]).astype(str)

            self.row_df['station_id'] = self.row_df['SDATE'].astype(str) + '_' + \
                                        self.row_df['STATN']


            #==========================================================================
    def _add_file(self, file_path, sep=',', **kwargs): 
        self.line_data = {}
        # print('utf8')
        with codecs.open(file_path, encoding='utf8') as fid:
            for line in fid: 
                if not line.strip():
                    continue 
                split_line = line.split(sep)
                code = split_line[0] 
                
                # Check if code is a parent code. If so, information should be retrieved from the row 
                if self.mapping_parents.get(code): 
                    mapping_dict = self.mapping_parents.get(code)
                    for item, col in mapping_dict.items():
                        value = split_line[col]
                        self.line_data[item] = self.mapping_label.get(value, value)
                
                # Save row 
                if code == '10': 
                    self.data_matrix.append([self.line_data[item] for item in self.parameter_list]) 
        print('File loaded: {}'.format(file_path))
                    
        
    #==========================================================================
    def save_data(self, file_path):
        self.row_df.to_csv(file_path, sep='\t', encoding='cp1252', index=False)
        
        

    