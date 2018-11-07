# -*- coding: utf-8 -*-
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on Tue Sep 12 14:38:54 2017

@author: a001985
"""

import pandas as pd 
import numpy as np
import os
import shutil



"""
===============================================================================
===============================================================================
===============================================================================
"""
class ColumnFile: 
    """
    Hold a column based file using pandas. 
    """
    def __init__(self, file_path, **kwargs): 
        
        self.file_path = file_path
        self.kwarguments = {'sep': '\t', 
                       'encoding': 'cp1252'}
        self.kwarguments.update(kwargs)
        
        self.df = pd.load_csv(file_path, **self.kwarguments)
        
    #==========================================================================
    def get_mapping(self, par, **kwargs): 
        """
        Returns a list of values from parameter=par that matches the criteria 
        in kwargs. Only one value in the kwargs argument are alowed. 
        """
        boolean = np.array(np.ones(len(self.df)), dtype=bool)
        for key, value in kwargs.iteritems():
            boolean = boolean & (self.df[key]==value)
        
        values = self.df.loc[boolean, par].values
        return list(values)

class DirectoryContent(object):

    def __init__(self, dir_1, dir_2=None):

        self.dir_1 = dir_1
        self.dir_2 = dir_2

    def _list_files(self):
        self.dir_1_file_names = os.listdir(self.dir_1)
        self.dir_1_file_paths = [os.path.join(self.dir_1, file_name) for file_name in self.dir_1_file_names]

        if self.dir_2 is not None:
            self.dir_2_file_names = os.listdir(self.dir_2)
            self.dir_2_file_paths = [os.path.join(self.dir_2, file_name) for file_name in self.dir_2_file_names]

    def show_comparison(self, **kwargs):
        if self.dir_2 is None:
            return
        self._list_files()

        if kwargs.get('ignore_file_ending'):
            self.dir_1_file_names = [item.split('.')[0] for item in self.dir_1_file_names]
            self.dir_2_file_names = [item.split('.')[0] for item in self.dir_2_file_names]

        not_in_dir_2 = [f for f in self.dir_1_file_names if f not in self.dir_2_file_names]
        not_in_dir_1 = [f for f in self.dir_2_file_names if f not in self.dir_1_file_names]

        print()
        print('='*50)
        print('Nr files in {}: {}'.format(self.dir_1, len(self.dir_1_file_names)))
        print('Nr files in {}: {}'.format(self.dir_2, len(self.dir_2_file_names)))
        print('Nr {} files not in {}: {}'.format(self.dir_1, self.dir_2, len(not_in_dir_2)))
        print('Nr {} files not in {}: {}'.format(self.dir_2, self.dir_1, len(not_in_dir_1)))

        if kwargs.get('list_files'):
            print()
            print('Files not in {}:\n'.format(self.dir_2))
            print('\n'.join(not_in_dir_2))

            print()
            print('Files not in {}:\n'.format(self.dir_1))
            print('\n'.join(not_in_dir_1))

class Explorer(object):

    def __init__(self, directory):
        self.directory = os.path.abspath(directory)
        self.file_mapping = {}

    def load_file_location(self):
        for k, (root, dirs, files) in enumerate(os.walk(self.directory, topdown=True)):
            for name in files:
                path = os.path.join(root, name)
                self.file_mapping[name] = path

    def copy_files_in_list(self, file_list=[], to_directory=None, **kwargs):
        if not all([file_list, to_directory]):
            raise IOError
        if not os.path.exists(to_directory):
            os.mkdir(to_directory)
        copied = []
        not_copied = []
        for file_name in file_list:
            file_path = self.file_mapping.get(file_name, None)
            if file_path is None:
                not_copied.append(file_path)
            else:
                copied.append(file_name)
                to_file_path = os.path.join(to_directory, file_name)
                print(file_path)
                print(to_file_path)
                shutil.copy(file_path, to_file_path)

        print('{} files copied to directory {}'.format(len(copied), to_directory))
        print('{} files where NOT found!'.format(len(not_copied)))
        print()


def move_files_in_list(file_paths, to_directory, **kwargs):
    if not to_directory:
        raise ValueError
    if not os.path.exists(to_directory):
        os.mkdir(to_directory)

    if type(file_paths) == str:
        file_paths = [file_paths]

    nr_files_moved = 0
    for file_path in file_paths:
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            dest = os.path.join(to_directory, file_name)
            shutil.move(file_path, dest)
            nr_files_moved += 1
    print('{} files moved'.format(nr_files_moved))




    
