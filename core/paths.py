# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os


class Paths(object):
    """
    Class holds paths to all directories and files.
    """
    def __init__(self, app_directory):
        self.app_directory = app_directory

        self.directory_settings_files = os.path.join(self.app_directory, 'settings_files') 