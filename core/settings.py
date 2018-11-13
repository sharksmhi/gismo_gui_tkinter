#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import codecs
import os
import shutil
import pickle

        
"""
========================================================================
========================================================================
========================================================================
"""
class Settings(dict):

    def __init__(self,
                 default_settings_file_path=None,
                 root_directory=False):
        """
        Updated 20171002    by
        """
        self.settings_are_modified = False
        if not default_settings_file_path:
            return
        self.default_settings_file_path = default_settings_file_path
        self.root_directory = root_directory
        self._load_settings()
        self._load_unit_list()
        
#        self._create_file_paths()
#        self._fix_lists()
#        self.create_fonts()
    
    #===========================================================================
    def _load_settings(self, load_default=False):

        # Always load default settings first
        self._load_default_settings()
        
        self.file_path = self['directory']['Settings file path']
        # Overwrite with pkl-file
        if not load_default and os.path.exists(self.file_path): 
            self._load_pkl_settings()
                
    
    #===========================================================================
    def _load_default_settings(self):
        """
        Updated 20181002    by Magnus Wenzer
        """
        # self.default_settings_file_path = os.path.join(self.root_directory,
        #                                                u'system', u'settings.ini')
        self.settings_list = []
        fid = codecs.open(self.default_settings_file_path, 'r', 'cp1252')
        for line in fid:
            if line.startswith(u'#'): # Comment
                continue
            
            if line.startswith('end'):
                break
            if line.strip():
                split_line = line.strip().split(u'\t')
                key = split_line[0].strip()
                group = split_line[1].strip()
                value = split_line[2].strip()
                
                if group == 'flags':
                    value = [v.strip() for v in value.split(',')]
                
                
                
                
                
                #####################################################################
                #####################################################################
                #####################################################################
                
                if key in [u'Quality flags to flag', u'Parameter order']:
                    value = [val.strip() for val in value.split(u',')]
                else:
                    try:
                        if u'.' not in value:
                            value = int(value)
                    except:
                        pass
                if group not in self.keys():
                    self[group] = {}
                # Areas
                if group == u'map area':
                    min_lon, max_lon, min_lat, max_lat = value.split()
                    self[group][key] = {}
                    self[group][key][u'min_lon'] = min_lon
                    self[group][key][u'max_lon'] = max_lon
                    self[group][key][u'min_lat'] = min_lat
                    self[group][key][u'max_lat'] = max_lat
                # directory
                elif group in [u'directory', u'shapefile']:
                    # Replace "root" with root directory
                    if value.startswith(u'root/'):
                        if not self.root_directory:
                            raise GTBExceptionMissingAttribute('"root" keyword found in settings file but root_directory is not given')
                        value = value.replace(u'root/', self.root_directory.replace(u'\\',u'/') + u'/')
                        print('===', value)
                    # shapefile
                    if group == u'shapefile':
                        coordinate_system = split_line[3].strip()
                        self[group][key] = (value, coordinate_system)
                    else:
                        self[group][key] = value 
#                 elif group == u'screening colors':
#                     value = value.replace(u' ', u'').split(u',')
                    
#                     if len(value) == 1:
#                         value = value[0]
#                     else:
#                         value = map(float, value)
#                     self[group][key] = value
                elif u'page' in group:
                    self[group][key] = {}
                    self[group][key]['value'] = value
                    self[group][key]['value_list'] = None
                    self[group][key]['type'] = None
                    if len(split_line) == 4:
                        string = split_line[3].strip()
                        split = string.split(u';')
                        self[group][key]['type'] = split[0]
                        if len(split) == 2:
                            self[group][key]['value_list'] = eval(split[1])
                    else:
                        # if old values exist in settings.pkl len(split_line) might be 3 and not 4
                        pass
                    
                else:
                    self[group][key] = value
                self.settings_list.append(key)
        fid.close()
        
        # Save lists
        self.page_list = sorted([page for page in self if u'page' in page.lower()])
    
    
    #===========================================================================
    def _load_pkl_settings(self):
        fid = open(self.file_path, 'rb')
        loaded_dict = pickle.load(fid)
        fid.close()
        
        for category in loaded_dict:
            if category in self:
                try:
                    for key in loaded_dict[category]:
                        if key in self[category]:
                            
                            self[category][key] = loaded_dict[category][key]
                            
                            if key==u'Max distance to station (m)':
                                self[category][key][u'value'] = float(loaded_dict[category][key][u'value'])
                                
                            
                except:
                    self[key] = loaded_dict[key]
        
        
    #===========================================================================
    def save_settings(self):
        save_dict = {}
        print(self)
        for key in self.keys():
            save_dict[key] = self[key]
            if key == u'map area':
                print(self[key])
                print(save_dict[key])
                print(self[key] == save_dict[key])
        fid = open(self.file_path, 'wb')
        pickle.dump(save_dict, fid)
        fid.close()
        
    
    #===========================================================================
    def change_setting(self, group, key, value):
        if key not in self[group]:
            self[group][key] = u''
        old_value = self[group][key]
        if type(old_value) == str:
            value = str(value)
        elif type(old_value) == int:
            value = int(value)
        elif type(old_value) == float:
            value = float(value)
        elif type(old_value) == bool:
            if value == u'True':
                value = True
            elif value == u'False':
                value = False
        self[group][key] = value
        print(group, key, value)

    
    #===========================================================================
    def _load_unit_list(self):
        self.unit_list = ['ml/l', 'umol/l', 'mmol/l', 'deg', 'deg C', 'C', 'mg/l', 'psu']



class SettingsFiles(object):
    """
    Class hold
    """
    def __init__(self, settings_directory):
        """

        :param settings_files_path:
        """
        self.directory = settings_directory

        self.file_names = []
        self.files = []
        self.paths = []

        self._list_files()

    def _list_files(self):
        self.file_names = []
        self.files = []
        self.paths = []

        self.name_to_path = {}

        for file_name in sorted(os.listdir(self.directory)):
            self.file_names.append(file_name)
            name = file_name.split('.')[0]
            self.files.append(name)
            p = os.path.join(self.directory, file_name)
            self.paths.append(p)
            self.name_to_path[name] = p

    def get_list(self):
        return self.files

    def get_path(self, file):
        return self.name_to_path.get(file, '')

    def import_file(self, file_path):
        """
        Copies the given file to the settings directory and adds update the lists.
        :param file_path:
        :return:
        """
        file_name = os.path.basename(file_path)
        base, ext = os.path.splitext(file_name)
        target_file_path = os.path.join(self.directory, file_name)
        shutil.copy(file_path, target_file_path)
        self._list_files()


