# -*- coding: utf-8 -*-
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on Tue Mar 07 11:48:49 2017

@author:
"""
import pandas as pd

import numpy as np

from gismo.exceptions import *


import pickle


# ==============================================================================
# ==============================================================================
class GISMOdataManager(object):
    """
    Created 20181003     

    Class manager to handle qc of GISMO-objects.
    """

    def __init__(self, factory, *args, **kwargs):
        self.factory = factory
        self.sampling_type_list = factory.get_list()
        self.objects = {}
        self.objects_by_sampling_type = dict((item, {}) for item in self.sampling_type_list)

        self.match_objects = {}


    def _check_file_id(self, file_id):
        """
        Raises GISMOExceptionInvalidFileId if file_id not in loaded data.
        :param file_id:
        :return: None
        """
        if file_id not in self.objects:
            raise GISMOExceptionInvalidFileId(file_id)

    def add_file(self, sampling_type='', **kwargs):

        if sampling_type not in self.sampling_type_list:
            raise GISMOExceptionInvalidSamplingType
            # This might not be necessary if pkl file is loaded

        # Check if we should load pkl file
        if kwargs.get('load_pkl') and kwargs.get('pkl_file_path'):
            with open(kwargs.get('pkl_file_path'), "rb") as fid:
                gismo_object = pickle.load(fid)
        else:
            gismo_object = self.factory.get_object(sampling_type=sampling_type, **kwargs)
            if kwargs.get('save_pkl') and kwargs.get('pkl_file_path'):
                # Save pkl file of the object
                with open(kwargs.get('pkl_file_path'), "wb") as fid:
                    pickle.dump(gismo_object, fid)

        self.objects[gismo_object.file_id] = gismo_object
        self.objects_by_sampling_type[sampling_type][gismo_object.file_id] = gismo_object

    def flag_data(self, file_id, flag, *args, **kwargs):
        """
        Created 20181004     

        Flags data in file_id.
        :param file_id:
        :param args:
        :param kwargs:
        :return:
        """
        self._check_file_id(file_id)
        gismo_object = self.objects.get(file_id)

        flag = str(flag)
        if not flag or flag not in gismo_object.valid_flags:
            raise GISMOExceptionInvalidFlag('"{}", valid flags are "{}"'.format(flag, ', '.join(gismo_object.valid_flags)))

        # Check if valid options
        for key in kwargs:
            if key not in gismo_object.flag_data_options:
                raise GISMOExceptionInvalidOption('{} is not a valid filter option'.format(key))

        return self.objects.get(file_id).flag_data(flag, *args, **kwargs)

    def get_data_object(self, file_id, *args, **kwargs):
        """ Should not be used """
        self._check_file_id(file_id)
        return self.objects.get(file_id)

    def get_filter_options(self, file_id, **kwargs):
        """
        Created 20181004     

        :return: list of filter options
        """
        self._check_file_id(file_id)
        return self.objects.get(file_id).filter_data_options

    def get_flag_options(self, file_id, **kwargs):
        """

        :param file_id:
        :param kwargs:
        :return:
        """
        self._check_file_id(file_id)
        return self.objects.get(file_id).flag_data_options

    def get_mask_options(self, file_id, **kwargs):
        """

        :param file_id:
        :param kwargs:
        :return:
        """
        self._check_file_id(file_id)
        return self.objects.get(file_id).mask_data_options

    def get_match_data(self, main_file_id, match_file_id, *args, **kwargs):
        self._check_file_id(main_file_id)
        self._check_file_id(match_file_id)
        if not self.match_objects.get(main_file_id) or not self.match_objects.get(main_file_id).get(match_file_id):
            raise GISMOExceptionInvalidInputArgument

        match_object = self.match_objects.get(main_file_id).get(match_file_id)
        return match_object.get_match_data(*args, **kwargs)


    def get_data(self, file_id, *args, **kwargs):
        """
        Created 20181004     
        Updated 20181005     

        :param file_id: file name minus the extension
        :param args:
        :param options:
        :param kwargs: specify filter. For example profile_id=<something>
        :return:
        """
        self._check_file_id(file_id)
        gismo_object = self.objects.get(file_id)

        # Check if valid options
        for key in kwargs.get('filter_options', {}):
            if key not in gismo_object.filter_data_options:
                raise GISMOExceptionInvalidOption('{} is not a valid filter option'.format(key))

        for key in kwargs.get('flag_options', {}):
            if key not in gismo_object.flag_data_options:
                raise GISMOExceptionInvalidOption('{} is not a valid flag option'.format(key))

        for key in kwargs.get('mask_options', {}):
            if key not in gismo_object.mask_data_options:
                raise GISMOExceptionInvalidOption('{} is not a valid mask option'.format(key))

        return gismo_object.get_data(*args, **kwargs)

    def get_parameter_list(self, file_id, **kwargs):
        self._check_file_id(file_id)
        return self.objects.get(file_id).get_parameter_list(**kwargs)

    def match_files(self, main_file_id, match_file_id, **kwargs):
        if not all([self.objects.get(main_file_id), self.objects.get(match_file_id)]):
            raise GISMOExceptionInvalidInputArgument

        self.match_objects.setdefault(main_file_id, {})
        self.match_objects[main_file_id][match_file_id] = MatchGISMOdata(self.objects.get(main_file_id), self.objects.get(match_file_id), **kwargs)



# ==============================================================================
# ==============================================================================
class GISMOdata(object):
    """
    Created 20181003     
    Updated 20181005     

    Base class for a GISMO data file.
    A GISMO-file only has data from one sampling type.
    """

    def __init__(self, *args, **kwargs):
        self.file_id = ''
        self.metadata = GISMOmetadata()

        self.parameter_list = []        # Valid data parameters
        self.filter_data_options = []   # Options for data filter (what to return in def get_data)
        self.flag_data_options = []     # Options for flagging data (where should data be flagged)
        self.mask_data_options = []     # Options for masking data (replaced by "missing value"

        self.valid_flags = []

    def flag_data(self, flag, *args, **kwargs):
        """
        Created 20181004     

        :param flag: The flag you want to set for the parameter
        :param args: parameters that you want to flag.
        :param kwargs: conditions for flagging. Options are listed in self.flag_data_options
        :return: None
        """
        raise GISMOExceptionMethodNotImplemented

    def get_data(self, *args, **kwargs):
        """
        Created 20181004     

        :param args: parameters that you want to have data for.
        :param kwargs: specify filter. For example profile_id=<something>.
        :return: dict. each argument in args should be a key in the dict. Value are lists or arrays representing that key.
        """
        raise GISMOExceptionMethodNotImplemented

    def get_parameter_list(self, *args, **kwargs):
        """
        Created 20181022

        :return: list of available data parameters. Parameters that have quality flags.
        """
        raise GISMOExceptionMethodNotImplemented



# ==============================================================================
# ==============================================================================
class GISMOmetadata(object):
    """
    Created 20181003     

    Base class for GISMO metadata
    Class holds metadata information of a GISMO file.
    """
    def __init__(self, *args, **kwargs):
        pass


            


"""
========================================================================
========================================================================
"""


class GISMOqcManager(object):
    """
    Created 20181002     

    Class manager to handle qc of GISMO-objects.
    """

    def __init__(self, factory, *args, **kwargs):
        """
        Created 20181005     

        :param factory:
        :param args:
        :param kwargs:
        """
        self.factory = factory
        self.qc_routine_list = factory.get_list()
        self.objects = {}
        self.objects_by_qc_routine = dict((item, {}) for item in self.qc_routine_list)

    def add_qc_routine(self, routine, **kwargs):
        routine = self.factory.get_object(sampling_type=routine, **kwargs)

    def run_qc(self):
        pass




"""
========================================================================
========================================================================
"""
class GISMOqc(object):
    """
    Created 20181002     

    Base class to handle quality control of GISMO-objects.
    """

    def __init__(self, *args, **kwargs):
        self.qc_routines = []

    def update_config_files(self):
        """
        Call to update config files needed to run qc
        :return:
        """
        raise GISMOExceptionMethodNotImplemented

    def run_qc(self, gismo_object, *args):
        """
        Created 20181005     

        Data is a pandas dataframe that can be reach under gismo_object.df
        :param gismo_object:
        :param args: qc routines that you want to run
        :return:
        """
        raise GISMOExceptionMethodNotImplemented


class MatchGISMOdata(object):
    """
    Class to maths data from two GISMOdata objects.
    """
    def __init__(self,
                 main_gismo_object,
                 match_gismo_object,
                 tolerance_dist=1,  # distance in deg
                 tolerance_depth=1, # distance in meters
                 tolerance_hour=0,
                 **kwargs):

        self.main_object = main_gismo_object
        self.match_object = match_gismo_object

        # Save tolearances
        # self.dist_multiple = 1000
        # self.tolerance_dist = int(kwargs.get('dist', tolerance_dist)*self.dist_multiple)
        self.tolerance_dist = kwargs.get('dist', tolerance_dist)

        self.tolerance_depth = int(kwargs.get('depth', tolerance_depth))
        self.tolerance_time = pd.Timedelta(days=kwargs.get('days', 0), hours=kwargs.get('hours', tolerance_hour))

        print(self.tolerance_dist)
        print(self.tolerance_depth)
        print(self.tolerance_time)

        # Run steps
        self._limit_data_scope()
        self._find_match()


    def _limit_data_scope(self):
        """
        Narrow the data scope. Data outside the the tollerance is removed.
        :return:
        """

        main_df = self.main_object.df
        match_df = self.match_object.df

        # Time
        main_time_boolean = (main_df['time'] >= (min(match_df['time']) - self.tolerance_time)) & (
                main_df['time'] <= (max(match_df['time']) + self.tolerance_time))

        match_time_boolean = (match_df['time'] >= (min(main_df['time']) - self.tolerance_time)) & (
                match_df['time'] <= (max(main_df['time']) + self.tolerance_time))



        # Pos
        main_data = self.main_object.get_data('lat', 'lon', 'depth', type_float=True)
        match_data = self.match_object.get_data('lat', 'lon', 'depth', type_float=True)

        main_lat_boolean = (main_data['lat'] >= (min(match_data['lat']) - self.tolerance_dist)) & (
                main_data['lat'] <= (max(match_data['lat']) + self.tolerance_dist))
        main_lon_boolean = (main_data['lon'] >= (min(match_data['lon']) - self.tolerance_dist)) & (
                main_data['lon'] <= (max(match_data['lon']) + self.tolerance_dist))

        match_lat_boolean = (match_data['lat'] >= (min(main_data['lat']) - self.tolerance_dist)) & (
                match_data['lat'] <= (max(main_data['lat']) + self.tolerance_dist))
        match_lon_boolean = (match_data['lon'] >= (min(main_data['lon']) - self.tolerance_dist)) & (
                match_data['lon'] <= (max(main_data['lon']) + self.tolerance_dist))

        # Depth
        main_depth_boolean = (main_data['depth'] >= (min(match_data['depth']) - self.tolerance_depth)) & (
                main_data['depth'] <= (max(match_data['depth']) + self.tolerance_depth))

        match_depth_boolean = (match_data['depth'] >= (min(main_data['depth']) - self.tolerance_depth)) & (
                match_data['depth'] <= (max(main_data['depth']) + self.tolerance_depth))

        # self.main_time_boolean = main_time_boolean
        # self.main_lat_boolean = main_lat_boolean
        # self.main_lon_boolean = main_lon_boolean
        # self.main_depth_boolean = main_depth_boolean
        #
        # self.match_time_boolean = match_time_boolean
        # self.match_lat_boolean = match_lat_boolean
        # self.match_lon_boolean = match_lon_boolean
        # self.match_depth_boolean = match_depth_boolean

        # Extract limited scope
        self.main_df = main_df.loc[main_time_boolean & main_lat_boolean & main_lon_boolean & main_depth_boolean].copy()
        self.match_df = match_df.loc[match_time_boolean & match_lat_boolean & match_lon_boolean & match_depth_boolean].copy()
        # self.main_df.columns = [item + '_main' for item in self.main_df.columns]
        # self.match_df.columns = [item + '_match' for item in self.match_df.columns]


    def _find_match(self):
        """
        Look for match for all rows in seld.match_df
        :return:
        """
        main_lat_array = self.main_df['lat'].astype(float)
        main_lon_array = self.main_df['lon'].astype(float)
        main_depth_array = self.main_df['depth'].astype(float)


        print('Finding match...')
        self.matching_main_id_set = set()       # All matches in main frame
        self.matching_match_id_list = []        # All matches in match frame
        self.matching_main_id_for_match_id = {}
        for time, lat, lon, depth, id in zip(self.match_df['time'],
                                             self.match_df['lat'].astype(float),
                                             self.match_df['lon'].astype(float),
                                             self.match_df['depth'].astype(float),
                                             self.match_df['visit_depth_id']):

            # Time
            time_boolean = (self.main_df['time'] >= (time-self.tolerance_time)) & (
                    self.main_df['time'] <= (time+self.tolerance_time))

            # Distance
            # lat_array = np.array([float(item) if item else np.nan for item in self.main_df['lat']])
            # lon_array = np.array([float(item) if item else np.nan for item in self.main_df['lon']])

            dist_array = latlon_distance_array(lat, lon, main_lat_array, main_lon_array)
            dist_boolean = (dist_array <= self.tolerance_dist)

            # Depth
            depth_boolean = (main_depth_array >= (depth - self.tolerance_depth)) & (
                    main_depth_array <= (depth + self.tolerance_depth))


            m_df = self.main_df.loc[time_boolean & dist_boolean & depth_boolean]
            if len(m_df):
                self.matching_match_id_list.append(id)
                self.matching_main_id_set.update(m_df['visit_depth_id'].values)
                self.matching_main_id_for_match_id[id] = m_df['visit_depth_id'].values


    def get_match_data(self, *args, **kwargs):
        filter_options = kwargs.get('filter_options', {})
        filter_options['visit_depth_id'] = self.matching_match_id_list
        kwargs['filter_options'] = filter_options
        return self.match_object.get_data(*args, **kwargs)

    def get_main_id_for_match_id(self, match_id):
        return self.matching_main_id_for_match_id.get(match_id)


# ==============================================================================
def latlon_distance_array(lat_point, lon_point, lat_array, lon_array):
    '''
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    '''

    # convert decimal degrees to radians
    lat_point = np.radians(lat_point)
    lon_point = np.radians(lon_point)
    lat_array = np.radians(lat_array)
    lon_array = np.radians(lon_array)

    # haversine formula
    dlat = lat_array - lat_point
    dlon = lon_array - lon_point
    a = np.sin(dlat / 2.) ** 2 + np.cos(lat_point) * np.cos(lat_array) * np.sin(dlon / 2.) ** 2

    c = 2 * np.arcsin(np.sqrt(a))
    # km = 6367 * c
    km = 6363 * c  # Earth radius at around 57 degrees North
    return km



    
    
    
    
    
    
    
    
    
    