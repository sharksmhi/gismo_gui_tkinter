# -*- coding: utf-8 -*-
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on Tue Mar 07 09:36:32 2017

@author:
"""
import codecs
import os
import shutil


"""
================================================================================
================================================================================
================================================================================
"""
class ColumnMapping():
    """
    Reads a text file with columns (tab as delimiter). Maps internal and external columns based on the given input.
    Several columns can be given for each of these arguments to form a combined mapping structure. 
    Ex:
    internal_column_name = ['parameter_name', 'unit'] # Will take information from both columns for the internal name.
    
    If add_all_matches=True, all matches are added and results from "get_" are given as a list.
    """
     
    #==========================================================================
    def __init__(self, 
                 source_file_path=None, 
                 local_file_path=None, 
                 internal_column=None, 
                 external_column=None, 
                 encoding=None, 
                 add_all_matches=False):
#        print '='*30
#        print source_file_path
#        print local_file_path
#        print internal_column
#        print external_column
#        print '-'*30
        if not all([local_file_path, internal_column, external_column]):
            print('Not enough input arguments to create ColumnMapping file')
            return
            
        if not isinstance(internal_column, list):
            internal_column = [internal_column]
 
        if not isinstance(external_column, list):
            external_column = [external_column]
    
        self.source_file_path = source_file_path
        self.local_file_path = local_file_path
        
        self.internal_column = internal_column
        self.external_column = external_column
        
        self.all_columns = internal_column + external_column
        
        self.encoding = encoding
        self.add_all_matches = add_all_matches
        
        self.update_file()
        
    #===========================================================================
    def update_file(self):
        """
        Copies the current version of the file from the source. 
        """
        if os.path.exists(self.source_file_path):
            self.source_file_path = self.source_file_path.replace('\\', '/')
            self.local_file_path = self.local_file_path.replace('\\', '/')
            
            if not self.source_file_path:
                pass
            else:
                try:
                    if self.source_file_path != self.local_file_path:
                        os.remove(self.local_file_path)
                        shutil.copy2(self.source_file_path, self.local_file_path)
                except:
                    print('Could not copy file...')
                    print('From: "%s"' % self.source_file_path)
                    print('To: "%s"' % self.local_file_path)
                
        self._load_data()
 
    #==========================================================================
    def _load_data(self):
        self.internal_to_external = {}
        self.external_to_internal = {}
        fid = codecs.open(self.local_file_path, 'r')
         
        for r, line in enumerate(fid):
            if not line:
                continue
            if line.startswith('#'): # Comment
                continue
            split_line = [item.strip() for item in line.split('\t')]
            if r == 0:
                header = split_line
            else:
                line_dict = dict(zip(header, split_line))
                try:
                    internal_value = ' '.join([line_dict[item] for item in self.internal_column]).strip()
                    external_value = ' '.join([line_dict[item] for item in self.external_column]).strip()
                except:
                    pass
                
                if self.add_all_matches:
                    if internal_value not in self.internal_to_external:
                        self.internal_to_external[internal_value] = []
                    if external_value not in self.external_to_internal:
                        self.external_to_internal[external_value] = []
                    
                    self.internal_to_external[internal_value].append(external_value)
                    self.external_to_internal[external_value].append(internal_value)
                else:
                    self.internal_to_external[internal_value] = external_value
                    self.external_to_internal[external_value] = internal_value
                 
        fid.close()
 
    #==========================================================================
    def get_external(self, internal):
        par = self.internal_to_external.get(internal)
        if par:
            return par
        else:
            return internal
         
    #==========================================================================
    def get_internal(self, external):
        par = self.external_to_internal.get(external)
        if par:
            return par
        else:
            return external
        
        
"""
================================================================================
================================================================================
================================================================================
"""
class ParameterMapping(ColumnMapping):
    
    #==========================================================================
    def __init__(self, settings_object=None):
                     
        ColumnMapping.__init__(self,
                               source_file_path=settings_object.parameter_mapping.source_file_path, 
                               local_file_path=settings_object.parameter_mapping.local_file_path, 
                               internal_column=settings_object.parameter_mapping.internal_column, 
                               external_column=settings_object.parameter_mapping.external_column)
        
        
"""
================================================================================
================================================================================
================================================================================
"""
class StationMapping():

    #===========================================================================
    def __init__(self, 
                 settings_object=None, 
                 source_file_path=None, 
                 local_file_path=None, 
                 header_starts_with=None, 
                 external_column=None, 
                 internal_column=None, 
                 platform_type_column=None, 
                 encoding=None):
                     
        """
        kwargs is for arguments in codecs.open. 
        """
        
        if not settings_object or all([source_file_path, local_file_path, header_starts_with, external_column, internal_column]):
            print('Not enyough input arguments to create ColumnMapping file')
            return
            
        if settings_object:
            for item in ['source_file_path', 'local_file_path', 'header_starts_with', 'external_column', 'internal_column', 'platform_type_column', 'encoding']:
                try:
                    setattr(self, item, getattr(settings_object.station_mapping, item))
                except:
                    print('Could not add attribute: %s' % item)
        else:
            self.source_file_path = source_file_path
            self.local_file_path = local_file_path
            self.header_starts_with = header_starts_with
            self.external_column = external_column 
            self.internal_column = internal_column 
            self.platform_type_column = platform_type_column
            self.encoding = encoding
        
        self.update_file()
    
    #===========================================================================
    def update_file(self):
        """
        Copies the current version of the file from the source. 
        """
        if os.path.exists(self.source_file_path):
            
            if os.path.exists(self.local_file_path):
                os.remove(self.local_file_path)
            
            try:
                if self.source_file_path != self.local_file_path:
                    shutil.copy2(self.source_file_path, self.local_file_path)
            except:
                print('Could not copy file...')
                print('From: "%s"' % self.source_file_path)
                print('To: "%s"' % self.local_file_path)
                
        self._load_file()
        
    #===========================================================================
    def _load_file(self):
            
        self.internal_to_external = {}
        self.internal_to_type = {}
        
        self.external_to_internal = {}
        self.external_to_type = {}
        
        self.internal_by_type = {}
        self.external_by_type = {}

        
        # Load data
        fid = codecs.open(self.local_file_path, 'r', encoding=self.encoding)
        self.header = False
        for r, line in enumerate(fid):
            line = line.strip()
            split_line = [item.strip() for item in line.split('\t')]
            if not line:
                continue
            if '=' not in line and line.startswith(self.header_starts_with):
                self.header = split_line
            elif self.header:
                line_dict = dict(zip(self.header, split_line))
                
                external = line_dict[self.external_column]
                internal = line_dict[self.internal_column]
                platform_type = line_dict[self.platform_type_column]
                
                self.internal_to_external[internal] = external
                self.internal_to_type[internal] = platform_type
                
                self.external_to_internal[external] = internal
                self.external_to_type[external] = platform_type
                
                if platform_type not in self.internal_by_type:
                    self.internal_by_type[platform_type] = []
                self.internal_by_type[platform_type].append(internal)
                
                if platform_type not in self.external_by_type:
                    self.external_by_type[platform_type] = []
                self.external_by_type[platform_type].append(external)
                
        fid.close()

    #===========================================================================
    def get_ferybox_list(self):
        return sorted(self.internal_by_type['FB'])
    
    #===========================================================================
    def get_platform_type(self, item):
        for t in self.internal_by_type:
            if item in self.internal_by_type[t]:
                return t
            
        for t in self.external_by_type:
            if item in self.external_by_type[t]:
                return t
        return 'Unknown'
    
    #===========================================================================
    def get_internal(self, item):
        return self.external_to_internal.get(item, item)
        
    #===========================================================================
    def get_external(self, item):
        return self.internal_to_external.get(item, item)

    #===========================================================================
    def list_platforms(self, match=''):
        return sorted([item for item in self.internal_to_external if match in item])
    
    #===========================================================================
    def list_external(self, match=''):
        return sorted([item for item in self.external_to_internal if match in item])

"""
================================================================================
================================================================================
================================================================================
"""


"""
================================================================================
================================================================================
================================================================================
"""