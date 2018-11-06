#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import shutil

from .gismo import GISMOqc
from .exceptions import *

from . import IOCFTP_QC

"""
========================================================================
========================================================================
"""
class PluginFactory(object):
    """
    Created 20181003     

    Class hold information about active classes in module.
    Also contains method to return an object of a mapped class.

    New class in module is activated by adding class name to self.classes.

    Also make sure to add required input arguments (for __init__) to self.required_arguments.

    """
    def __init__(self):
        # Add key and class to dict if you want to activate it
        self.classes = {'iocftp_qc0': QCiocftp,
                        'ferrybox_test': TestQCFerrybox}

        self.required_arguments = {'iocftp_qc0': [],
                                   'ferrybox_test': ['local_config_directory',
                                                     'source_config_directory']}

    def get_list(self):
        return sorted(self.classes)

    def get_object(self, routine, *args, **kwargs):
        """

        :param routine:
        :param args:
        :param kwargs:
        :return:
        """
        if not self.classes.get(routine):
            raise GISMOExceptionInvalidClass
        return self.classes.get(routine)(*args, **kwargs)

    def get_requirements(self, routine):
        """
        Created 20181005     

        Returns the required arguments needed for the initialisation of the object
        :param routine:
        :param args:
        :param kwargs:
        :return:
        """
        if not self.classes.get(routine):
            raise GISMOExceptionInvalidClass
        return self.required_arguments.get(routine)


class TestQCFerrybox(GISMOqc):
    """
    Created 20181005     

    Class to perform QC on gismo ferrybox data
    """
    def __init__(self,
                 local_config_directory=None,
                 source_config_directory=None,):
        pass

    def update_config_files(self):
        """ Call to update config files needed to run qc """
        pass

    def run_qc(self, gismo_object):
        """ Call to run qc on GISMO-object """
        pass


class QCiocftp(GISMOqc):
    """
    Created 20180928     
    Updated 20181001

    Class handles quality control based on QC from IOCFTP.
    """

    def __init__(self,
                 local_config_directory=None,
                 source_config_directory=None,
                 log_directory=None,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        if not local_config_directory:
            raise GISMOExceptionMissingPath('Local directory for qc not given.')
        if not log_directory:
            raise GISMOExceptionMissingPath('Log directory for qc not given.')

        self.local_config_directory = local_config_directory
        self.source_config_directory = source_config_directory
        self.log_directory = log_directory

        if not os.path.exists(self.local_config_directory):
            os.mkdir(self.local_config_directory)

    def update_config_files(self):
        """ Call to update config files needed to run qc """
        pass

    def run_qc(self, gismo_object):
        """ Call to run qc on GISMO-object """
        pass

    # ==================================================================
    def copy_config_files(self, **kwargs):
        """
        Created 20181001     

        Copies qc config files from source to local directory.
        """
        if not self.local_config_directory:
            raise GISMOExceptionMissingPath('Local directory for qc not given.')

        if not self.source_config_directory:
            raise GISMOExceptionMissingPath('Source directories not given for qc config and/or scripts.')

        if not os.path.exists(self.source_config_directory):
            raise GISMOExceptionInvalidPath

        try:
            for file_name in os.listdir(self.source_config_directory):
                source_path = os.path.join(self.source_config_directory, file_name)
                local_path = os.path.join(self.local_config_directory, file_name)
                shutil.copy(source_path, local_path)
        except:
            raise GISMOExceptionCopyFiles('Could not copy all qc config files from source "{}" to local "{}"'.format(self.source_config_directory,
                                                                                                                     self.local_config_directory))
        # Set global path to config files
        IOCFTP_QC.set_config_path(self.local_config_directory)

    # ==================================================================
    def run_qc(self, gismo_object):
        """
        Created 20181001     

        Copies qc config files from source to local directory.
        """
        print('QC_FILE_PATH', IOCFTP_QC.QC_FILE_PATH)
        print('CFG_FILE_PATH', IOCFTP_QC.CFG_FILE_PATH)


        if gismo_object.sameling_type != 'ferrybox':
            return




