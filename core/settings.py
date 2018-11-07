#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import codecs
import os
import pickle

        
"""
========================================================================
========================================================================
========================================================================
""" 
# @gtb_utils.singleton
class Settings(dict):

    def __init__(self,
                 default_settings_file_path=None,
                 root_directory=False):
        """
        Updated 20171002    by Magnus Wenzer
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
#    #===========================================================================
#    def _create_file_paths(self):
#        
#        # All directories/paths
#        for key in self['directory']:
#            
#            current_path = self['directory'][key]
#            
#
#        
#    #===========================================================================
#    def _fix_lists(self):
#        """
#        To split into list if given in settings.
#        """
#        for key in self['list'].keys():
#            made_list = [item.strip() for item in self['list'][key].split(',')]
#            self['list'][key] = made_list
#       
#    #===========================================================================
#    def create_fonts(self):
#        """
#        Method to create/change font style and size. 
#        For some reason the tkFont object works in Spyder but not in Eclipse
#        """
#        # TODO: Does not work in Eclipse
#        # Font 1
#        font1 = self['general']['Font 1']
#        size1 = self['general']['Font size 1']
#        weight1 = self['general']['Font weight 1']
#        slant1 = self['general']['Font slant 1']
#        print font1, size1, weight1, slant1
#        
#        # Font 2
#        font2 = self['general']['Font 2']
#        size2 = self['general']['Font size 2']
#        weight2 = self['general']['Font weight 2']
#        slant2 = self['general']['Font slant 2']
#            
#        try:    # If font attributes already exists
#            self.font_1.configure(family=font1, 
#                                            size=size1, 
#                                            weight=weight1, 
#                                            slant=slant1)
#            
#            self.font_2.configure(family=font2, 
#                                            size=size2, 
#                                            weight=weight2, 
#                                            slant=slant2)
#        except:
#            
#            font = (font1, size1, weight1, slant1)
#            self.font_1 = tkFont.Font(family=font1, 
#                                            size=size1, 
#                                            weight=weight1, 
#                                            slant=slant1)
#
#            self.font_2 = tkFont.Font(family=font2, 
#                                            size=size2, 
#                                            weight=weight2, 
#                                            slant=slant2)
   