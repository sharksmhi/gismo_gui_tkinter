# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on Tue Mar 07 11:48:49 2017

@author:
"""

from .exceptions import *

from .gismo import GISMOdataManager
from .gismo import GISMOqcManager

from . import gismo

import os 
import json 
import pickle
import shutil


#==============================================================================
#==============================================================================
class FileInfo(dict):
    """
    Created 20180628       
    Updated 20180713       
    
    Holds file information. Source file and pkl file.
    """
    def __init__(self, 
                 file_path='', 
                 pkl_directory=''): 
        
        self.file_path = file_path 
        self.pkl_directory = pkl_directory
        
        file_name = os.path.basename(file_path) 
        name, ending = os.path.splitext(file_name)
        directory = os.path.dirname(file_path)
        pkl_file_path = os.path.join(pkl_directory, '{}.pkl'.format(name))
        
        self['file_id'] = name
        self['directory'] = directory 
        self['file_path'] = file_path 
        self['pkl_file_path'] = pkl_file_path
        
    

#==============================================================================
#==============================================================================
class UserInfo():
    """
    Created 20180627       
    """
    #==========================================================================
    def __init__(self, 
                 user='', 
                 user_directory=''): 
        """
        Created 20180627        
        Updated 20180627       
        
        Loads the json info file. 
        If non existing the file is created. 
        If existing the fields are updated with "update_data".
        The fields must be initiated here. No "creations" of keys are made in 
        this or other scripts. 
        
        The json info file will hold the following information: 
            user name
            loaded files and there origin 
            
        """
        assert all([user, user_directory])
        
        self.user = user 
        self.user_directory = user_directory
        self.pkl_directory = os.path.join(self.user_directory, 'pkl_files')

        update_data = {'user': self.user, 
                       'loaded_files': {}}
        
        self.file_id_sampling_type_mapping = {}

        if not os.path.exists(self.user_directory):
            os.makedirs(self.user_directory)
            
        if not os.path.exists(self.pkl_directory):
            os.makedirs(self.pkl_directory)
            
        self.info_file_path = os.path.join(self.user_directory, 'user_info.json') 
        
        self.content = {}
        # Load info file if existing
        if os.path.exists(self.info_file_path): 
            with open(self.info_file_path, "r") as fid:
                self.content = json.load(fid)
        
        # Update content with possibly new fields
        self.content.update(update_data)
        
        # Save info file
        self._save_file()
        
    
    #==========================================================================
    def _save_file(self):
        """
        Created 20180627        
        
        Save self to json file
        """  
        with open(self.info_file_path, "w") as fid: 
            json.dump(self.content, fid)
    
    
    #==========================================================================
    def add_file(self, 
                 sampling_type='', 
                 file_path='', 
                 settings_file_path=''): 
        """
        Created 20180627       
        Updated 20180713       
        
        Information to be added when adding a file. 
        returns a "file name dict" containing information about data file and settings file: 
            directory 
            file_path 
            pkl_file_path
        """
        assert all([sampling_type, file_path]) 
        
        
#        file_name = os.path.basename(file_path) 
#        name, ending = os.path.splitext(file_name)
#        directory = os.path.dirname(file_path)
#        pkl_file_path = os.path.join(self.pkl_directory, '{}.pkl'.format(name))
#        
#        info_dict = {file_name: {'directory': directory, 
#                                 'file_path': file_path}, 
#                                 'pkl_file_path': pkl_file_path} 
                
        self.content.setdefault('loaded_files', {}).setdefault(sampling_type, {})
        
        info_data = FileInfo(file_path=file_path, 
                             pkl_directory=self.pkl_directory)
        
        info_settings = FileInfo(file_path=settings_file_path, 
                                 pkl_directory=self.pkl_directory)
        
        file_id = info_data.get('file_id')
        self.content['loaded_files'][sampling_type][file_id] = {}
        self.content['loaded_files'][sampling_type][file_id]['file_id'] = file_id
        self.content['loaded_files'][sampling_type][file_id]['data_file'] = info_data
        
#        print('settings_file_path', settings_file_path)
        self.content['loaded_files'][sampling_type][file_id]['settings_file'] = info_settings
        
        self.file_id_sampling_type_mapping[file_id] = sampling_type
        
        self._save_file()
        
        return self.content['loaded_files'][sampling_type][file_id]

    
    #==========================================================================
    def delete_file(self, 
                    sampling_type='', 
                    file_id=''): 
        """
        Created 20180628        
        Updated 20180713       
        
        Deletes information about a file. 
        
        """
        files_dict = self.content['loaded_files'].get(sampling_type, {}) 
        if file_id in files_dict: 
            files_dict.pop(file_id)
            self.file_id_sampling_type_mapping.pop(file_id)
        return True 
        
    
    #==========================================================================
    def get_sampling_type_for_file_id(self, file_id):
        """
        Created 20180713        
        """
        return self.file_id_sampling_type_mapping.get(file_id, None)
    
    
    #==========================================================================
    def get_file_id_list(self, sampling_type):
        """
        Created 20180713       
        Updated 
        
        Returns a list of the loaded files (file_id) for the given sampling type. 
        """ 
        return sorted(self.content['loaded_files'].get(sampling_type, {}).keys())
        
    
#==============================================================================
#==============================================================================        
class GISMOsession(object):
    """
    Created 20180625       
    """
    #==========================================================================
    def __init__(self,
                 root_directory='',
                 users_directory='',
                 log_directory='',
                 user='default',
                 sampling_types_factory=None,
                 qc_routines_factory=None,
                 **kwargs):

        """
        Created 20180625       
        Updated 20181003       

        root_directory is optional but needs to be provided if "root" is in the settings files.

        kwargs can include:
            save_pkl
        """
        if not all([users_directory, user, sampling_types_factory]):
            raise GISMOExceptionMissingInputArgument

        self.root_directory = root_directory
        self.users_directory = users_directory
        self.log_directory = log_directory
        self.save_pkl = kwargs.get('save_pkl', False)

        self.sampling_types_factory = sampling_types_factory
        self.qc_routines_factory = qc_routines_factory

        self.user = user
        self.user_directory = os.path.join(self.users_directory, self.user)

        self.data_manager = GISMOdataManager(factory=self.sampling_types_factory)
        self.qc_manager = GISMOqcManager(factory=self.qc_routines_factory)

        self.compare_objects = {}

        
        self._startup_session()

    
    # ==========================================================================
    def _startup_session(self):
        """
        Created 20180625       
        Updated 20180713       
        """

        # Create and load json info file
        self.user_info = UserInfo(self.user,
                                  self.user_directory)


        # # Initate Boxen that will hold all data
        # self.boxen = gtb_core.Boxen(controller=self,
        #                             root_directory=self.root_directory)

    def add_compare_object(self, main_file_id, compare_file_id, **kwargs):
        pass

    def flag_data(self, file_id, flag, *args, **kwargs):
        """
        Created 20181005       

        :param file_id:
        :param flag:
        :param args:
        :param kwargs:
        :return: None
        """
        self.data_manager.flag_data(file_id, flag, *args, **kwargs)


    # ==========================================================================
    def get_sampling_types(self):
        return self.sampling_types_factory.get_list()

    # ==========================================================================
    def get_qc_routines(self):
        return self.qc_routines_factory.get_list()

    # ==========================================================================
    def get_sampling_type_requirements(self, sampling_type):
        return self.sampling_types_factory.get_requirements(sampling_type)

    # ==========================================================================
    def get_qc_routine_requirements(self, routine):
        return self.qc_routines_factory.get_requirements(routine)

    def get_filter_options(self, file_id, **kwargs):
        """
        Created 20181004       

        :param file_id:
        :param kwargs:
        :return: list of filter options
        """
        return self.data_manager.get_filter_options(file_id, **kwargs)

    def get_flag_options(self, file_id, **kwargs):
        """
        Created 20181005       

        :param file_id:
        :param kwargs:
        :return: list of flag options
        """
        return self.data_manager.get_flag_options(file_id, **kwargs)

    def get_mask_options(self, file_id, **kwargs):
        """
        Created 20181005

        :param file_id:
        :param kwargs:
        :return: list of mask options
        """
        return self.data_manager.get_mask_options(file_id, **kwargs)

    def get_save_data_options(self, file_id, **kwargs):
        """
        Created 20181106

        :param file_id:
        :param kwargs:
        :return: list of mask options
        """
        return self.data_manager.get_save_data_options(file_id, **kwargs)

    def get_data(self, file_id, *args, **kwargs):
        """
        Created 20181004       

        :param file_id:
        :param args:
        :param kwargs:
        :return: data as list/array (if one args) or list of lists/arrays (if several args)
        """
        return self.data_manager.get_data(file_id, *args, **kwargs)

    def get_match_data(self, main_file_id, match_file_id, *args, **kwargs):
        return self.data_manager.get_match_data(main_file_id, match_file_id, *args, **kwargs)

    def match_files(self, main_file_id, match_file_id, **kwargs):
        self.data_manager.match_files(main_file_id, match_file_id, **kwargs)

    # ==========================================================================
    def load_file(self,
                 sampling_type='',
                 file_path='',
                 settings_file_path='', 
                 reload=False, 
                 **kwargs):
        """
        Created 20180628       
        Updated 20181004       

        If reload==True the original file is reloaded regardless if a pkl file excists. 
        sampling_type refers to SMTYP in SMHI codelist
        
        kwargs can be:
            file_encoding
        """
        if not all([sampling_type, file_path, settings_file_path]):
            raise GISMOExceptionMissingInputArgument
        
        if not all([os.path.exists(file_path), os.path.exists(settings_file_path)]):
            raise GISMOExceptionInvalidPath

        # Add file path to user info 
        file_path = os.path.abspath(file_path)
        settings_file_path = os.path.abspath(settings_file_path)
        file_paths = self.user_info.add_file(sampling_type=sampling_type, 
                                             file_path=file_path,
                                             settings_file_path=settings_file_path)
        
        # Get file paths         
        data_file_path = file_paths.get('data_file', {}).get('file_path', '')
        data_file_path_pkl = file_paths.get('data_file', {}).get('pkl_file_path', '')
        data_file_path_settings = file_paths.get('settings_file', {}).get('file_path', '')

        # Get file_id
        file_id = file_paths.get('data_file', {}).get('file_id', '')
        if not file_id:
            raise GISMOExceptionMissingKey
        
        # Check type of file and load
        if reload or not os.path.exists(data_file_path_pkl): 
            # Load original file 
            self.data_manager.load_file(data_file_path=data_file_path,
                                       sampling_type=sampling_type,
                                       settings_file_path=data_file_path_settings,
                                       root_directory=self.root_directory,
                                       save_pkl=self.save_pkl,
                                       pkl_file_path=data_file_path_pkl)

        else:
            # Check if sampling_type is correct 
            # file_name = os.path.basename(file_path)
            # expected_sampling_type = self.user_info.get_sampling_type_for_file_id(file_id)
            # if expected_sampling_type != sampling_type:
            #     return False
            
            # Load buffer pickle file
            self.data_manager.load_file(sampling_type=sampling_type,
                                       load_pkl=self.save_pkl,
                                       pkl_file_path=data_file_path_pkl)

        return file_id
    
    #==========================================================================
    def _load_pickle_file(self, data_file_path_pkl):
        """
        Created 20180828        

        Loads a pickle file that contains data and settings information. 
        Returns a gismo object.
        """
        with open(data_file_path_pkl, "rb") as fid: 
            gismo_object = pickle.load(fid)
    
        return gismo_object

    # ==========================================================================
    def old_load_qc_object(self,
                       local_config_directory=None,
                       source_config_directory=None):
        """
        Created 20181001       

        Loads a GISMOqc object.
        """
        self.qc = GISMOqc(local_config_directory=local_config_directory,
                          source_config_directory=source_config_directory)

    # ==========================================================================
    def old_update_qc_files(self, **kwargs):
        """
        Created 20181001       

        Updated qc files in qc object (self.qc) if loaded.
        """
        if not self.qc:
            raise GISMOException('No QC object loaded. Run load_qc_object and try again.')
        self.qc.copy_config_files(**kwargs)

    def save_file(self, file_id, **kwargs):
        """
        Created 20181106

        :param file_id:
        :param kwargs:
        :return: None
        """
        self.data_manager.save_file(file_id, **kwargs)

    #==========================================================================
    def old_save_file(self,
                  file_path='', 
                  sampling_type='', 
                  file_id=None,
                  overwrite=False):
        """
        Created 20180628        
        Updated 20180713       
        
        If file_id is not given the file_path basename without ending is used 
        as key to identify the gismo object. 
        
        Set overwirte=True to allow overwriting existing file
        """ 
        if not file_id:
            file_name = os.path.basename(file_path) 
            file_id, ending = os.path.splitext(file_name) 
            
        gismo_object = self.get_gismo_object(file_id=file_id, 
                                             sampling_type=sampling_type)
        
        if gismo_object is False:
            return False 

        if not os.path.exists(file_path) or overwrite==True:
            if file_path[-4:] == '.pkl':
                with open(file_path, "wb") as fid:
                    pickle.dump(gismo_object, fid)
            else:
                gismo_object.write_to_file(file_path)
            return True
        return False

    # ==========================================================================
    def get_file_id_list(self, sampling_type):
        """
        Created 20180713       
        Updated 
        
        Returns a list of the loaded files (file_id) for the given sampling type. 
        """ 
        return self.user_info.get_file_id_list(sampling_type)

    # ==========================================================================
    def get_gismo_object(self, file_id=''):
        """
        Created 20180713       
        Updated 20181022
        
        Returns a the gismo object marked with the given file_id
        """
        if not file_id:
            raise GISMOExceptionMissingInputArgument

        return self.data_manager.get_data_object(file_id)

    # ==========================================================================
    def get_parameter_list(self, file_id='', **kwargs):
        if not file_id:
            raise GISMOExceptionMissingInputArgument

        return self.data_manager.get_parameter_list(file_id, **kwargs)

    # ==========================================================================
    def print_list_of_gismo_objects(self):
        """
        Created 20180926       
        Updated 20180927     

        Prints a list of all loaded gismo object. sorted by sampling_type.
        """
        for st in sorted(self.gismo_objects):
            print('Sampling type:', st)
            for file_id in sorted(self.gismo_objects[st]):
                print('   {}'.format(file_id))






