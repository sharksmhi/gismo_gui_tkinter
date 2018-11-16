#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import numpy as np
import datetime
import pandas as pd
import codecs
import matplotlib.dates as dates

from .mapping import StationMapping, ParameterMapping
from .gismo import GISMOdata
from .gismo import GISMOmetadata

from .exceptions import *


class PluginFactory(object):
    """
    Created 20181003     
    Updated 20181004

    Class hold information about active classes in module.
    Also contains method to return an object of a mapped class.
    """
    def __init__(self):
        # Add key and class to dict if you want to activate it
        self.classes = {'Ferrybox CMEMS': FERRYBOXfile,
                        'Bouy CMEMS': BOUYfile,
                        'SHARK PhysicalChemical': SHARKfilePhysicalChemichal,
                        'SHARK CTD': CTDfile}

        gismo_requirements = ['data_file_path', 'settings_file_path', 'root_directory']
        self.required_arguments = {'ferrybox_cmems': gismo_requirements,
                                   'ctd_gismo': gismo_requirements}

    def get_list(self):
        return sorted(self.classes)

    def get_object(self, sampling_type, *args, **kwargs):
        if not self.classes.get(sampling_type):
            raise GISMOExceptionInvalidClass
        kwargs['sampling_type'] = sampling_type
        return self.classes.get(sampling_type)(*args, **kwargs)

    def get_requirements(self, sampling_type):
        """
        Created 20181005     

        Returns the required arguments needed for the initialisation of the object
        :param sampling_type:
        :param args:
        :param kwargs:
        :return:
        """
        if not self.classes.get(sampling_type):
            raise GISMOExceptionInvalidClass
        return self.required_arguments.get(sampling_type)

    # ==============================================================================


# ==============================================================================
class GISMOfile(GISMOdata):
    """
    Updated 20181005     

    Base class for a GISMO data file.
    A GISMO-file only has data from one sampling type.
    """
    # TODO: filter_data, flag_options, flag_data
    # ==========================================================================
    def __init__(self, data_file_path=None, settings_file_path=None, root_directory=None, **kwargs):

        super().__init__()

        self.file_path = data_file_path
        self.file_id, ending = os.path.splitext(os.path.basename(data_file_path))
        self.settings_file_path = settings_file_path
        self.export_df = None
        self.root_directory = root_directory

        self.comment_id = kwargs.get('comment_id', None)

        self.file_encoding = kwargs.get('file_encoding', 'cp1252')
        self.sampling_type = kwargs.get('sampling_type', '')

        self._load_settings_file()
        self._load_station_mapping()
        self._load_parameter_mapping()
        #        return
        self._load_data()
        self._do_import_changes()

        self.parameter_list = []

        # self.parameter_list = ['time', 'lat', 'lon', 'depth', 'visit_id', 'visit_depth_id'] + self.qpar_list
        self.parameter_list = ['time', 'lat', 'lon', 'depth'] + self.qpar_list
        self.filter_data_options = []
        self.flag_data_options = []
        self.mask_data_options = ['include_flags', 'exclude_flags']

        self.save_data_options = ['file_path', 'overwrite']

        self.valid_flags = self.settings.flag_list[:]

    # ==========================================================================
    def _load_settings_file(self):
        self.settings = SamplingTypeSettings(self.settings_file_path, root_directory=self.root_directory)

        self.missing_value = str(self.settings.info.missing_value)

        nr_decimals = self.settings.info.number_of_decimals_for_float
        if nr_decimals:
            self.nr_decimals = '%s.%sf' % ('%', nr_decimals)
        else:
            self.nr_decimals = None

    # ==========================================================================
    def _load_station_mapping(self):
        self.station_mapping = StationMapping(settings_object=self.settings)

    # ==========================================================================
    def _load_parameter_mapping(self):
        self.parameter_mapping = ParameterMapping(settings_object=self.settings)


    # ==========================================================================
    def _load_data(self, **kwargs):
        """
        Updated 20181005     

        All comment lines are stored in attribute metadata.

        :param kwargs:
        :return:
        """
        # Looping through the file seems to be faster then pd.read_csv regardless if there are comment lines or not.
        # Note that all values are of type str.

        metadata_raw = []
        header = []
        data = []
        with codecs.open(self.file_path, encoding=kwargs.get('encoding', 'cp1252')) as fid:
            for line in fid:
                if self.comment_id is not None and line.startswith(self.comment_id):
                    # We have comments and need to load all lines in file
                    metadata_raw.append(line)
                else:
                    split_line = line.strip('\n\r').split(kwargs.get('sep', '\t'))
                    if not header:
                        header = [item.strip() for item in split_line]
                    else:
                        data.append(split_line)

        self.original_columns = header[:]
        self.df = pd.DataFrame(data, columns=header)
        self.df.fillna('', inplace=True)


#        metadata_raw = []
#        if kwargs.get('comment_id'):
#            with codecs.open(self.file_path, encoding=kwargs.get('encoding', 'cp1252')) as fid:
#                for line in fid:
#                    if line.startswith(kwargs.get('comment_id')):
#                        metadata_raw.append(line.strip())  # remove newline
#                    else:
#                        # No more comments
#                        break
#
#        self.df = pd.read_csv(self.file_path, sep='\t', skipinitialspace=True, dtype={0: str},
#                              encoding=self.file_encoding, comment=kwargs.get('comment_id', None))

        # Find station id (platform type)
        station = self.settings.column.station
        if 'index' in station:
            col = int(station.split('=')[-1].strip())
            self.external_station_name = self.df.columns[col]
            self.internal_station_name = self.station_mapping.get_internal(self.external_station_name)
        else:
            self.external_station_name = 'Unknown'
            self.internal_station_name = 'Unknown'

        #        self.platform_type = self.station_mapping.get_platform_type(self.external_station_name)

        # Save parameters
        self.parameters_external = [external for external in self.df.columns if 'Unnamed' not in external]
        self.parameters_internal = [self.parameter_mapping.get_internal(external) for external in
                                    self.parameters_external]

        self.internal_to_external = dict(zip(self.parameters_internal, self.parameters_external))
        self.external_to_internal = dict(zip(self.parameters_external, self.parameters_internal))

        self.qpar_list = sorted([par for par in self.parameters_external if self._get_qf_par(par) not in [None, False]])
        self.mapped_parameters = [self.parameter_mapping.get_internal(par) for par in self.qpar_list]

        # Set type of flags to str
#        for qpar in self.qpar_list:
#            self.df[qpar] = self.df[qpar].astype(str)

    # ==========================================================================
    def _do_import_changes(self):

        self._add_columns()

        if self.missing_value:
            self.missing_value = float(self.missing_value)
        self.df.replace(self.missing_value, np.nan, inplace=True)

    # ==========================================================================
    def _prepare_export(self):
        # Make a copy to be used for export
        self.export_df = self.df[self.original_columns].copy()
        self.export_df.replace(np.nan, float(self.missing_value), inplace=True)

    def _get_argument_list(self, arg):
        """
        Updated 20181004     

        Returns a list. If type(arg) != list/array/tuple, [arg] is returned
        :param arg:
        :return: list
        """
        if type(arg) in [list, tuple, np.array, np.ndarray]:
            return list(arg)
        else:
            return [arg]

    def _get_pandas_series(self, value):
        """
        Created 20181005     

        :param value: boolean or value
        :return: a  pandas series of length len(self.df) with the given value.
        """
        if type(value) == bool:
            if value:
                return pd.Series(np.ones(len(self.df), dtype=bool))
            else:
                return pd.Series(np.zeros(len(self.df), dtype=bool))
        else:
            return pd.Series([value]*len(self.df))


    # ==========================================================================
    def _add_columns(self):
        """
        Add columns for time, lat, lon and depth.
        Information about parameter name should be in settings.
        """
        #         print '='*30
        #         for c in sorted(self.df.columns):
        #             print c
        #         print '-'*30
        # ----------------------------------------------------------------------
        # Time
        time_formats = ['%Y%m%d%H%M',
                        '%Y%m%d%H:%M',
                        '%Y%m%d%H.%M',
                        '%Y-%m-%d%H%M',
                        '%Y-%m-%d%H:%M',
                        '%Y-%m-%d%H.%M']
        self.time_format = None
        datetime_list = []
        time_par = self.settings.column.time

        if 'index' in time_par:
            # At this moment mainly for CMEMS-files
            time_par = self.df.columns[int(time_par.split('=')[-1].strip())]
            print('time_par', time_par)
            self.df['time'] = pd.to_datetime(self.df[time_par], format=self.time_format)
        else:
            time_pars = self.settings.column.get_list('time')

            self.df['time'] = self.df[time_pars].apply(apply_datetime_object_to_df, axis=1)
            # print(time_pars)
            # for i in range(len(self.df)):
            #     # First look in settings and combine
            #     value_list = []
            #     for par in time_pars:
            #         value_list.append(self.df.ix[i, par])
            #
            #     value_str = ''.join(value_list)
            #
            #     if not self.time_format:
            #         for tf in time_formats:
            #             try:
            #                 datetime.datetime.strptime(value_str, tf)
            #                 self.time_format = tf
            #                 break
            #             except:
            #                 pass
            #
            #     datetime_list.append(datetime.datetime.strptime(value_str, self.time_format))
            #
            # self.df['time'] = pd.Series(datetime_list)

        # ----------------------------------------------------------------------
        # Position
        lat_par = self.parameter_mapping.get_external(self.settings.column.lat)
        lon_par = self.parameter_mapping.get_external(self.settings.column.lon)

        self.df['lat'] = self.df[lat_par]
        self.df['lon'] = self.df[lon_par]

        # ----------------------------------------------------------------------
        # Depth
        depth_par = self.parameter_mapping.get_external(self.settings.column.depth)
        self.df['depth'] = self.df[depth_par]

        # ----------------------------------------------------------------------
        # Station ID
        self.df['visit_id'] = self.df['lat'].astype(str) + self.df['lon'].astype(str) + self.df['time'].astype(str)
        self.df['visit_depth_id'] = self.df['lat'].astype(str) + self.df['lon'].astype(str) + self.df['time'].astype(str) + self.df['depth'].astype(str)


    def flag_data(self, flag, *args, **kwargs):
        """
        Created 20181005     

        :param flag: The flag you want to set for the parameter
        :param args: parameters that you want to flag.
        :param kwargs: conditions for flagging. Options are listed in self.flag_data_options
        :return: None
        """
        flag = str(flag)
        if not flag or flag not in self.valid_flags:
            raise GISMOExceptionInvalidFlag('"{}", valid flags are "{}"'.format(flag, ', '.join(self.valid_flags)))

        # Check dependent parameters
        all_args = []
        for arg in args:
            all_args.append(arg)
            all_args.extend(self.get_dependent_parameters(arg))

        # Work on external column names
        args = [self.internal_to_external.get(arg, arg) for arg in args]
        # args = dict((self.internal_to_external.get(key, key), key) for key in args)

        if not all([arg in self.df.columns for arg in args]):
            raise GISMOExceptionInvalidInputArgument



        # kwargs contains conditions for flagging. Options are listed in self.flag_data_options.
        boolean = self._get_pandas_series(True)

        for key, value in kwargs.items():
            # Check valid option
            if key not in self.flag_data_options:
                raise GISMOExceptionInvalidOption
            if key == 'time':
                value_list = self._get_argument_list(value)
                print('type(value_list[0])', type(value_list[0]))
                print(type(self.df.time.values[0]))
                boolean = boolean & (self.df.time.isin(value_list))
            elif key == 'time_start':
                boolean = boolean & (self.df.time >= value)
            elif key == 'time_end':
                boolean = boolean & (self.df.time <= value)

        # Flag data
        for par in args:
            qf_par = self._get_qf_par(par)
            if not qf_par:
                raise GISMOExceptionMissingQualityParameter('for parameter "{}"'.format(par))
            self.df.loc[boolean, qf_par] = flag

    # ==========================================================================
    def old_get_boolean_for_time_span(self, start_time=None, end_time=None, invert=False):
        """

        :param start_time:
        :param end_time:
        :param invert:
        :return:
        """

        if start_time and end_time:
            boolean_array = np.array((self.df.time >= start_time) & (self.df.time <= end_time))
        elif start_time:
            boolean_array = np.array(self.df.time >= start_time)
        elif end_time:
            boolean_array = np.array(self.df.time <= end_time)
        else:
            boolean_array = np.ones(len(self.df.time), dtype=bool)

        if invert:
            return np.invert(boolean_array)
        else:
            return boolean_array

    def get_data(self, *args, **kwargs):
        """
        Created 20181024
        Updated 20181106

        :param args: parameters that you want to have data for.
        :param kwargs: specify filter. For example profile_id=<something>. Only = if implemented at the moment.
        :return: dict with args as keys and list(s) as values.
        """
        # Always return type float if possible
        kw = {'type_float': True}
        kw.update(kwargs)
        return self._get_data(*args, **kw)

    # ===========================================================================
    def _get_data(self, *args, **kwargs):
        """
        Created 20181004     
        Updated 20181024

        :param args: parameters that you want to have data for.
        :param kwargs: specify filter. For example profile_id=<something>. Only = if implemented at the moment.
        :return: dict with args as keys and list(s) as values.
        """
        if not args:
            raise GISMOExceptionMissingInputArgument

        # Work on external column names
        args = dict((self.internal_to_external.get(key, key), key) for key in args)

        for arg in args:
            if arg not in self.df.columns:
                raise GISMOExceptionInvalidInputArgument(arg)
            elif arg not in self.parameter_list:
                raise GISMOExceptionInvalidInputArgument(arg)


        # Create filter boolean
        boolean = self._get_pandas_series(True)
        for key, value in kwargs.get('filter_options', {}).items():
            if key not in self.filter_data_options:
                raise GISMOExceptionInvalidOption('{} not in {}'.format(key, self.filter_data_options))
            if key == 'time':
                value_list = self._get_argument_list(value)
                boolean = boolean & (self.df.time.isin(value_list))
            elif key == 'time_start':
                boolean = boolean & (self.df.time >= value)
            elif key == 'time_end':
                boolean = boolean & (self.df.time <= value)
            elif key == 'visit_depth_id':
                value_list = self._get_argument_list(value)
                boolean = boolean & (self.df.visit_depth_id.isin(value_list))
            elif key == 'visit_id':
                value_list = self._get_argument_list(value)
                boolean = boolean & (self.df.visit_id.isin(value_list))

        # Extract filtered dataframe
        # filtered_df = self.df.loc[boolean, sorted(args)].copy(deep=True)
        filtered_df = self.df.loc[boolean].copy(deep=True)

        mask_options = kwargs.get('mask_options', {})
        # Create return dict and return
        return_dict = {}
        for par in args:
            par_array = filtered_df[par].values
            # if par == 'time':
            #     par_array = filtered_df[par].values
            # elif
            # try:
            #     par_array = filtered_df[par].astype(float).values
            # except:


            # Check mask options
            for opt, value in mask_options.items():
                if opt not in self.mask_data_options:
                    raise GISMOExceptionInvalidOption
                if opt == 'include_flags':
                    qf_par = self._get_qf_par(par)
                    if not qf_par:
                        continue
                    # print('\n'.join(sorted(filtered_df.columns)))
                    keep_boolean = filtered_df[qf_par].astype(str).isin([str(v) for v in value])
                    par_array[~keep_boolean] = ''
                elif opt == 'exclude_flags':
                    qf_par = self._get_qf_par(par)
                    if not qf_par:
                        continue
                    nan_boolean = filtered_df[qf_par].astype(str).isin([str(v) for v in value])
                    par_array[nan_boolean] = ''

            # Check output type
            if par == 'time':
                pass
            elif kwargs.get('type_float') is True or par in kwargs.get('type_float', []):
                float_par_list = []
                for value in par_array:
                    try:
                        if value:
                            float_par_list.append(float(value))
                        else:
                            float_par_list.append(np.nan)
                    except:
                        float_par_list.append(value)
                        #raise ValueError
                par_array = np.array(float_par_list)

            elif kwargs.get('type_int') is True or par in kwargs.get('type_int', []):
                float_par_list = []
                for value in par_array:
                    try:
                        if value:
                            float_par_list.append(float(value))
                        else:
                            float_par_list.append(np.nan)
                    except:
                        float_par_list.append(value)
                        # raise ValueError
                par_array = np.array(float_par_list)

            # Map to given column name
            return_dict[args[par]] = par_array
        return return_dict

    # ==========================================================================
    def get_dependent_parameters(self, par):

        if not self.settings:
            return None

        par = self.parameter_mapping.get_external(par)
        return self.settings['dependencies'].get(par, [])

    def get_parameter_list(self, **kwargs):
        if kwargs.get('external'):
            par_list = sorted(self.parameter_list)
        else:
            par_list = sorted([self.parameter_mapping.get_internal(par) for par in self.parameter_list])

        return par_list

    # ==========================================================================
    def _get_qf_par(self, par):
        """
        Updated 20181004
        :param par:
        :return:
        """
        prefix = self.settings.parameter_mapping.qf_prefix
        suffix = self.settings.parameter_mapping.qf_suffix
        # First check if prefix and/or suffix is given
        if not any([prefix, suffix]):
            print('No prefix or suffix given to this QF parameter')
            return

        if par in self.parameters_internal:
            par = self.internal_to_external[par]

        #         print 'par=', par
        if self.settings.parameter_mapping.unit_starts_with:
            par = par.split(self.settings.parameter_mapping.unit_starts_with)[0].strip()
        #             print 'par-', par

        # QF parameter is found whenever prefix or suffix matches the given par.
        # This means that if prefix="QF_" and par="TEMP", not only "QF_TEMP" is recognised but also "QF_TEMP (C)"
        for ext_par in self.parameters_external:
            if par in ext_par and ext_par.startswith(prefix) and ext_par.endswith(suffix):
                if ext_par != par:
                    #                     print 'ext_par', ext_par, par, prefix, suffix
                    return ext_par

        return False

    # ==========================================================================
    def _get_extended_qf_list(self, qf_list):
        """
        The pandas datafram may contain both str and int value in the qf-columns.
        This method adds both str and int versions of the given qf_list.
        """

        if not type(qf_list) == list:
            qf_list = [qf_list]

        # Add both int ans str versions of the flags
        extended_qf_list = []
        for qf in qf_list:
            extended_qf_list.append(qf)
            if type(qf) == int:
                extended_qf_list.append(str(qf))
            elif qf.isdigit():
                extended_qf_list.append(int(qf))

        return extended_qf_list

    # ===========================================================================
    def save_file(self, **kwargs):
        file_path = kwargs.get('file_path', None)
        if not file_path:
            file_path = self.file_path
        if os.path.exists(file_path) and not kwargs.get('overwrite', False):
            raise GISMOExceptionFileExcists(file_path)

        write_kwargs = {'index_label': False,
                        'index': False,
                        'sep': '\t',
                        'float_format': self.nr_decimals,
                        'decimal': '.'}

        write_kwargs.update(kwargs)

        self._prepare_export()

        data_dict = self.export_df.to_dict('split')

        sep = kwargs.get('sep', '\t')
        encoding = kwargs.get('encoding', 'cp1252')

        with codecs.open(file_path, 'w', encoding=encoding) as fid:
            if self.metadata.has_data:
                pass
            # Write column header
            fid.write(sep.join(data_dict['columns']))
            fid.write('\n')
            for line in data_dict['data']:
                fid.write(sep.join(line))
                fid.write('\n')

# ==============================================================================
# ==============================================================================
class FERRYBOXfile(GISMOfile):
    """
    A GISMO-file only has data from one platform.
    """

    # ==========================================================================
    def __init__(self, data_file_path=None, settings_file_path=None, root_directory=None, **kwargs):
        """
        Updated 20181005     

        :param data_file_path:
        :param settings_file_path:
        :param root_directory:
        :param kwargs:
        """
        kwargs.update(dict(data_file_path=data_file_path,
                           settings_file_path=settings_file_path,
                           root_directory=root_directory))
        GISMOfile.__init__(self, **kwargs)

        self.flag_data_options = self.flag_data_options + ['time', 'time_start', 'time_end']
        self.mask_data_options = self.mask_data_options + []


# ==============================================================================
class BOUYfile(GISMOfile):
    """
    A GISMO-file only has data from one platform.
    """

    # ==========================================================================
    def __init__(self, data_file_path=None, settings_file_path=None, root_directory=None, **kwargs):
        """
        Updated 20181022
        B

        :param data_file_path:
        :param settings_file_path:
        :param root_directory:
        :param kwargs:
        """
        kwargs.update(dict(data_file_path=data_file_path,
                           settings_file_path=settings_file_path,
                           root_directory=root_directory))
        GISMOfile.__init__(self, **kwargs)

        self.filter_data_options = self.filter_data_options + ['time', 'time_start', 'time_end']
        self.flag_data_options = self.flag_data_options + ['time', 'time_start', 'time_end']
        self.mask_data_options = self.mask_data_options + []


# ==============================================================================
# ==============================================================================
class CTDfile(GISMOfile):
    """
    A DATA-file has data from several platforms. Like SHARKweb Physical/Chemical columns.
    """

    # ==========================================================================
    def __init__(self, file_path=None, settings_file_path=None, root_directory=None, **kwargs):
        """
        Updated 20181005     

        :param file_path:
        :param settings_file_path:
        :param root_directory:
        :param kwargs:
        """

        kwargs.update(dict(file_path=file_path,
                           settings_file_path=settings_file_path,
                           root_directory=root_directory,
                           comment_id='//'))
        GISMOfile.__init__(self, **kwargs)

        self.filter_data_options = self.filter_data_options + ['visit_id', 'depth', 'from_depth', 'to_depth']
        self.flag_data_options = self.flag_data_options + ['depth', 'from_depth', 'to_depth']
        self.mask_data_options = self.mask_data_options + []

        self.metadata = GISMOmetadata(**kwargs)

        self._create_profile_info_dict()

    #         self._add_unique_profile_id() # Not implemented. Usefull?

    #     #==========================================================================
    #     def _load_data(self):
    #         self.df = pd.read_csv(self.file_path, sep='\t', skipinitialspace=True, dtype={0:str})
    #
    #         # Save parameters
    #         self.parameters_external = [external for external in self.df.columns if 'Unnamed' not in external]
    #         self.parameters_internal = [self.parameter_mapping.get_internal(external) for external in self.parameters_external]
    #
    #         self.internal_to_external = dict(zip(self.parameters_internal, self.parameters_external))
    #         self.external_to_internal = dict(zip(self.parameters_external, self.parameters_internal))
    #
    #         self.qpar_list = sorted([par for par in self.parameters_external if self._get_qf_par(par) != False])
    #         self.mapped_parameters = [self.parameter_mapping.get_internal(par) for par in self.qpar_list]

    # ==========================================================================
    def _create_profile_info_dict(self):
        """
        Creats a dict with display name as key and information about the profile in an object.
        Prolfile is defined by unique time.
        """
        print('_create_profile_info_dict')

        # ======================================================================
        class ProfileInfo():
            def __init__(self, display_name):
                self.display_name = display_name

        # ======================================================================
        if 'index' in self.settings.column.station:
            statn = self.internal_station_name
        else:
            statn = None

        self.profile_info = {}

        unique_dates = sorted(set(self.df.time))
        for unique_date in unique_dates:
            df = self.df.ix[self.df.time == unique_date, :]
            self.dfdf = df
            # Create display name used as key
            if statn:
                station_name = statn
            else:
                # Station is individual for each profile (or just one profile in file)
                station_column = self.parameter_mapping.get_external(self.settings.column.station)
                station_name = df.ix[0, station_column]
            display_name = ' - '.join([station_name, str(unique_date)])

            self.profile_info[display_name] = ProfileInfo(display_name)
            self.profile_info[display_name].gismo_object = self
            self.profile_info[display_name].file_path = self.file_path
            self.profile_info[display_name].disp_name = display_name
            self.profile_info[display_name].time = unique_date
            self.profile_info[display_name].lat = df.lat.values[0]
            self.profile_info[display_name].lon = df.lon.values[0]



# ==============================================================================
# ==============================================================================
class CTDmetadata(GISMOmetadata):
    """
    Created 20180928     
    Updated 20181003     

    Class holds metadata information of a GISMO file.
    """

    class Meatadata(object):
        """ Class to handle the METADATA """
        def __init__(self, **kwargs):
            self.has_data = False
            self.metadata_string = 'METADATA'
            self.data = {}
            self.column_sep = kwargs.get('column_sep', ';')
            self.metadata_id = '{}METADATA'.format(kwargs.get('comment_id', '/')*kwargs.get('nr_comment_id', '/'))

        def add(self, item_list, **kwargs):
            """
            item is expected to be a list of length 2:
                item_list[0] = metadata variable
                item_list[1] = value of the metadata variable
            """
            if item_list[0] != self.metadata_id:
                raise GISMOExceptionMetadataError('Non matching metadata string')
            self.data[item_list[1]] = item_list[2]
            self.has_data = True

        def set(self, **kwargs):
            for key, value in kwargs.items():
                self.data[key] = value


        def get_rows(self):
            return_list = []
            for key in sorted(self.data):
                line_list = [self.metadata_id, key, self.data[key]]
                return_list.append(self.column_sep.join(line_list))

            return return_list

    class Unhandled(object):
        """
        Updated 20181003     

        Class to handle the metadata that id not handled and should be as is
        """
        def __init__(self, **kwargs):
            self.data = []

        def add(self, metadata_string):
            """

            """
            self.data.append(metadata_string)

        def set(self, **kwargs):
            pass

        def get_rows(self):
            return sorted(self.data)


    # ==========================================================================
    def __init__(self, metadara_raw_lines, **kwargs):
        super().__init__()
        self.metadata_raw_lines = metadara_raw_lines
        self._load_meatadata()
        self.column_sep = kwargs.get('metadata_column_sep', ';')
        self.comment_id = kwargs.get('comment_id', '/')
        self.nr_comment_id = kwargs.get('nr_comment_id', 2)


    # ==========================================================================
    def _load_meatadata(self):
        """
        Updated 20181003     
        """
        kw = dict(column_sep=self.column_sep,
                  comment_id=self.comment_id,
                  nr_comment_id=self.nr_comment_id)

        self.data = {'METADATA': self.Meatadata(**kw),
                     'unhandled': self.Unhandled(**kw)}

        for k, line in enumerate(self.metadata_raw_lines):
            line = line.strip()

            # First line is FORMAT id line
            if k == 0:
                if 'FORMAT' not in line:
                    raise GISMOExceptionMetadataError
                self.format_line = line
                self.format = line.split('=')[-1]

            else:
                split_line = line.split(self.column_sep)
                metadata_type = split_line[0].strip(self.comment_id)

            if self.data.get(metadata_type):
                self.data[metadata_type].add(split_line)
            else:
                self.data['unhandled'].add(line)

            # ==============================================================================


# ==============================================================================
# ==============================================================================
class SamplingTypeSettings(dict):
    """
    Reads and stores information from a "GISMO" Settings file.
    """

    # ==========================================================================
    # ==========================================================================
    class MappingObject():
        def __init__(self, data, root_directory=None):
            for line in data:
                split_line = [item.strip() for item in line.split('\t')]
                if len(split_line) == 1:
                    header = split_line[0]
                    value = ''
                else:
                    header, value = split_line[:2]
                header = header.lower().replace(' ', '_')

                if 'root' in value:
                    if not root_directory:
                        raise GISMOExceptionMissingPath('Must provide root_directory')
                    value = value.replace('root', root_directory)
                    if not os.path.exists(value):
                        raise GISMOExceptionMissingPath(value)

                if ';' in value:
                    value = [item.strip() for item in value.split(';')]

                setattr(self, header, value)

        # ======================================================================
        def get_list(self, item):
            value = getattr(self, item)
            if not isinstance(value, list):
                value = [value]
            return value

    # ==========================================================================
    def __init__(self, file_path=None, root_directory=None):
        self.file_path = file_path
        self.root_directory = root_directory
        dict.__init__(self)
        if self.file_path:
            self._load_file()
            self._save_data()

    # ==========================================================================
    def _load_file(self):

        self.data = {}
        current_header = None
        fid = codecs.open(self.file_path, 'r', encoding='cp1252')

        for line in fid:
            line = line.strip()
            # Balnk line or comment line
            if not line or line.startswith('#'):
                continue

            # Find header
            if line.startswith('='):
                current_header = line.strip('= ')
                self.data[current_header] = []
            else:
                self.data[current_header].append(line)

        fid.close()

    # ==========================================================================
    def _save_data(self):
        for key in self.data:
            # ------------------------------------------------------------------
            if key.lower() == 'flags':
                self['flags'] = {}
                self.description_to_flag = {}
                for i, line in enumerate(self.data[key]):
                    split_line = [item.strip() for item in line.split(u'\t')]
                    if i == 0:
                        header = [item.lower() for item in split_line]
                    else:
                        qf = split_line[header.index('qf')]
                        self['flags'][qf] = {}
                        for par, item in zip(header, split_line):
                            if par == 'markersize':
                                item = int(item)
                            elif par == 'description':
                                self.description_to_flag[item] = qf

                            self['flags'][qf][par] = item

                self.flag_list = sorted(self['flags'])

            # ------------------------------------------------------------------
            elif key.lower() == 'dependent parameters':
                self['dependencies'] = {}
                for line in self.data[key]:
                    split_line = [item.strip() for item in line.split(';')]
                    #                    # Map parameters
                    #                    split_line = [CMEMSparameters().get_smhi_code(par) for par in split_line]

                    self['dependencies'][split_line[0]] = split_line[1:]

            # ------------------------------------------------------------------
            elif key.lower() == 'ranges':
                self['ranges'] = {}
                for i, line in enumerate(self.data[key]):
                    split_line = [item.strip() for item in line.split(u'\t')]
                    if i == 0:
                        header = [item.lower() for item in split_line]
                    else:
                        limit_dict = dict(zip(header, split_line))
                        par = split_line[header.index('parameter')]
                        self['ranges'][par] = {}
                        #                        print header
                        for limit in [item for item in header if item != 'parameter']:
                            if limit_dict[limit]:
                                value = float(limit_dict[limit])
                                self['ranges'][par][limit] = value

            # ------------------------------------------------------------------
            elif key.lower() == 'parameter mapping':
                self.parameter_mapping = self.MappingObject(self.data[key], self.root_directory)

            # ------------------------------------------------------------------
            elif key.lower() == 'station mapping':
                self.station_mapping = self.MappingObject(self.data[key], self.root_directory)
            # ------------------------------------------------------------------
            elif key.lower() == 'info':
                self.info = self.MappingObject(self.data[key], self.root_directory)

            # ------------------------------------------------------------------
            elif key.lower() == 'column':
                self.column = self.MappingObject(self.data[key], self.root_directory)

            # ------------------------------------------------------------------
            elif key.lower() == 'matching criteria':
                self.matching_criteria = self.MappingObject(self.data[key], self.root_directory)

            # ------------------------------------------------------------------
            elif key.lower() == 'map':
                self.map = self.MappingObject(self.data[key], self.root_directory)

    # ==================================================================
    def get_flag_list(self):
        return self.flag_list

    # ==================================================================
    def get_flag_description(self, flag):
        return self['flags'][flag]['description']

    # ==================================================================
    def get_flag_description_list(self):
        return [self.get_flag_description(flag) for flag in self.flag_list]

    # ==================================================================
    def get_flag_color(self, flag):
        return self['flags'][flag]['color']

    # ==================================================================
    def get_flag_color_list(self):
        return [self.get_flag_color(flag) for flag in self.flag_list]

    # ==================================================================
    def get_flag_markersize(self, flag):
        return self['flags'][flag]['markersize']

    # ==================================================================
    def get_flag_markersize_list(self):
        return [self.get_flag_markersize(flag) for flag in self.flag_list]

    # ==================================================================
    def get_flag_marker(self, flag):
        return self['flags'][flag]['marker']

    # ==================================================================
    def get_flag_marker_list(self):
        return [self.get_flag_marker(flag) for flag in self.flag_list]

    # ==================================================================
    def get_flag_from_description(self, description):
        return self.description_to_flag[description]

    # ==================================================================
    def get_flag_prop_dict(self, flag):
        flag = str(flag)
        if self:
            dont_include = ['qf', 'description']
            # print('='*50)
            # print(self['flags'][flag])
            # print('=' * 50)
            return {par: item for par, item in self['flags'][flag].items() if par not in dont_include}
        else:
            return {}

    # ==================================================================
    def _get_default_dict(self):
        pass


# ==============================================================================
# ==============================================================================
class SHARKfilePhysicalChemichal(GISMOfile):
    """
    Class to hold data from SHARK (Svenskt HAvsaRKiv).
    """

    # ==========================================================================
    def __init__(self, data_file_path=None, settings_file_path=None, root_directory=None, **kwargs):
        """
        Updated 20181005

        :param data_file_path:
        :param settings_file_path:
        :param root_directory:
        :param kwargs:
        """
        kwargs.update(dict(data_file_path=data_file_path,
                           settings_file_path=settings_file_path,
                           root_directory=root_directory))
        GISMOfile.__init__(self, **kwargs)

        self.filter_data_options = self.filter_data_options + ['time', 'time_start', 'time_end', 'visit_id', 'visit_depth_id']
        self.flag_data_options = []
        self.mask_data_options = self.mask_data_options + []


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


# ==============================================================================
# ==============================================================================
def latlon_distance(origin, destination):
    '''
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    from math import radians, cos, sin, asin, sqrt
    lat1, lon1 = origin
    lat2, lon2 = destination
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2.) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2.) ** 2
    c = 2 * asin(sqrt(a))
    # km = 6367 * c
    km = 6363 * c  # Earth radius at around 57 degrees North
    return km


# ==============================================================================
# ==============================================================================
def old_get_matching_sample_index(sample_object=None,
                                  gismo_object=None,
                                  modulus=None,
                                  diffs=None):
    if not all([sample_object, gismo_object]):
        return

    time_diff = diffs['time']
    dist_diff = diffs['dist']
    depth_diff = diffs['depth']

    # First reduce gismo dataframe.
    # This can be done by only inluding data that is close enough to the sample stations.
    #    unique_positions

    all_index = []
    # Loop values
    for i, [t, la, lo, d] in enumerate(zip(gismo_object.df.time,
                                           gismo_object.df.lat,
                                           gismo_object.df.lon,
                                           gismo_object.df.depth)):
        #        if i < 20:
        #            continue
        if modulus and i % modulus:
            continue

        #        print i

        # Depth: Get index for matching depth criteria to reduce loop length
        df = sample_object.df.ix[(sample_object.df.depth >= d - depth_diff) & \
                                 (sample_object.df.depth <= d + depth_diff), :]

        #        index_list = np.array(df.index)
        #        print 'len(df)', len(df)

        # Loop index and and save index
        for index in df.index:
            if index in all_index:
                #                print 'Index already added'
                continue

            time = df.ix[index, 'time']
            lat = df.ix[index, 'lat']
            lon = df.ix[index, 'lon']
            #            print abs((time-t).total_seconds() / 60)
            #            print time_diff
            #            print abs((time-t).total_seconds() / 60) > time_diff
            if abs((time - t).total_seconds() / 60) > time_diff:
                # Continue if no match
                #                print 'No match for time'
                continue

            if (latlon_distance([la, lo], [lat, lon]) * 1000) > dist_diff:
                # Continue if no match
                #                print 'No match for distance'
                continue

            # If this line i reached we have a match. Add this to all_index
            print('Match for index:', index)
            all_index.append(index)

    return sorted(all_index)


# ==============================================================================
# ==============================================================================
def old_get_matching_sample_index(sample_object=None,
                              gismo_object=None,
                              diffs=None):
    if not all([sample_object, gismo_object]):
        return

    time_diff = diffs['time']
    dist_diff = diffs['dist']
    depth_diff = diffs['depth']

    # --------------------------------------------------------------------------
    # First reduce sample dataframe.
    # Make new column in sample dataframe to get position string
    df = sample_object.df

    df['pos_str'] = df['lat'].map(str) + df['lon'].map(str)
    pos_list = list(set(df['pos_str']))

    all_index = []

    # Loop position list
    for pos in pos_list:
        pos_df = df.ix[df.pos_str == pos, :]
        pos_index = pos_df.index[0]
        la = pos_df.ix[pos_index, 'lat']
        lo = pos_df.ix[pos_index, 'lon']
        t = pos_df.ix[pos_index, 'time']

        # Check distanse to all points in gismo_object.df
        distance = latlon_distance_array(la, lo, gismo_object.df.lat, gismo_object.df.lon) * 1000

        # Get boolean index for valid distance
        boolean_distance = distance <= dist_diff

        # Check if any point in distance is within reach
        if not np.any(boolean_distance):
            continue

        ### Getting this far garantees that staton is within distance.

        # Check time to all points in gismo_object.df
        time_delta = np.array(map(datetime.timedelta.total_seconds, np.abs(gismo_object.df.time - t))) / 60

        # Get boolean index for valid time
        boolean_time = time_delta <= time_diff

        # Check if any point in time is within reach
        if not np.any(boolean_time):
            continue

        ### If we gotten this far we have match for both time and distance.
        ### But it migth not be the same match. Check this now.

        boolean_dist_time = boolean_distance & boolean_time

        # Check if any point match in both time and distance
        if not np.any(boolean_dist_time):
            continue

        ### We have a match for both time and distance
        ### Now we check agains depth

        for i, d in pos_df.depth.iteritems():
            depth_difference = abs(gismo_object.df.depth - d)
            boolean_depth = depth_difference <= depth_diff

            # Save index if any match for depth
            if np.any(boolean_depth):
                if i not in all_index:
                    all_index.append(i)

    return sorted(all_index)


def apply_datetime_object_to_df(x):
    """
    Used to apply datetime object to a pandas dataframe.
    :param x:
    :return:
    """
    time_formats = ['%Y%m%d%H%M',
                    '%Y%m%d%H:%M',
                    '%Y%m%d%H.%M',
                    '%Y-%m-%d%H%M',
                    '%Y-%m-%d%H:%M',
                    '%Y-%m-%d%H.%M',
                    '%Y%m%d',
                    '%Y-%m-%d']
    if type(x) == str:
        x = [x]
    time_string = ''.join([str(item) for item in x])
    d_obj = None
    for tf in time_formats:
        try:
            d_obj = datetime.datetime.strptime(time_string, tf)
            return d_obj
        except:
            pass

    raise GISMOExceptionInvalidTimeFormat('Could not find matching time format for "{}"'.format(time_string))