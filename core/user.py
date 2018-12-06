# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
import os
import shutil
import json

from core.exceptions import *


class UserManager(object):
    def __init__(self, users_root_directory):
        self.users_root_directory = users_root_directory
        if not os.path.exists(self.users_root_directory):
            os.mkdir(self.users_root_directory)
        self.users = {}
        self.user = None # Is the current user
        for user in os.listdir(users_root_directory):
            self.users[user] = User(user, users_root_directory)

    def set_user(self, user_name, create_if_missing=False):
        if user_name not in self.users:
            if create_if_missing:
                self.add_user(user_name)
            else:
                raise GUIExceptionUserError('Invalid user name')
        self.user = self.users.get(user_name)

    def get_user_list(self):
        return sorted(self.users)

    def add_user(self, user_name, from_user=None):
        if user_name in self.users:
            raise GUIExceptionUserError('User already exists')
        if from_user:
            if from_user not in self.users:
                raise GUIExceptionUserError('Could not find source user')
            from_dir = os.path.join(self.users_root_directory, from_user)
            to_dir = os.path.join(self.users_root_directory, user_name)
            shutil.copytree(from_dir, to_dir)
        else:
            # New user
            pass
        self.users[user_name] = User(user_name, self.users_root_directory)

class User(object):
    def __init__(self, name, users_root_directory):
        self.name = name
        # print(self.name)
        self.user_directory = os.path.join(users_root_directory, self.name)
        if not os.path.exists(self.user_directory):
            os.mkdir(self.user_directory)

        self.range = UserSettingsParameter(self.user_directory, 'range')

        self.settingsfile = UserSettings(self.user_directory, 'settingsfile')

        self.flag_color = UserSettings(self.user_directory, 'flag_color')
        self.flag_markersize = UserSettings(self.user_directory, 'flag_markersize')

        self.match = UserSettings(self.user_directory, 'match')

        self.path = UserSettings(self.user_directory, 'path')

        # Save process information like warning for file size etc.
        self.process = UserSettings(self.user_directory, 'process')

        self.map_boundries = UserSettings(self.user_directory, 'map_boundries')

        self.parameter_colormap = UserSettings(self.user_directory, 'parameter_colormap')

        # layout includes matplotlib styles etc
        self.layout = UserSettings(self.user_directory, 'layout')

        self.options = UserSettings(self.user_directory, 'options')

        self.map_prop = UserSettings(self.user_directory, 'map_prop')

        # Used for saving sampling depth.
        self.sampling_depth = UserSettings(self.user_directory, 'sampling_depth')




class UserSettings(object):
    """
    Baseclass for user settings.
    """
    def __init__(self, directory, settings_type):
        self.directory = directory
        self.settings_type = settings_type
        self.file_path = os.path.join(self.directory, '{}.json'.format(self.settings_type))

        self.data = {}

        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        if not os.path.exists(self.file_path):
            self._save()

        self._load()

    def _load(self):
        """
        Loads dict from json
        :return:
        """
        if os.path.exists(self.file_path):
            with open(self.file_path) as fid:
                self.data = json.load(fid)

    def _save(self):
        """
        Writes information to json file.
        :return:
        """
        with open(self.file_path, 'w') as fid:
            json.dump(self.data, fid)

    def get(self, key, if_missing=None):
        """

        :param key:
        :return:
        """
        return self.data.get(key, if_missing)

    def get_keys(self):
        return self.data.keys()

    def setdefault(self, key, value):
        """
        Works as setdefault for a dictionary. Should always be called with key and value.
        If data is set (key not in self.data) the dictionary is saved to json file.
        :param key:
        :param value:
        :return:
        """
        if self.data.get(key):
            return self.data.get(key)
        else:
            value = self.data.setdefault(key, value)
            self._save()
            return value

    def set(self, key, value):
        """
        Sets key to value
        :param key:
        :param value:
        :return:
        """
        if key not in self.data:
            self.data.setdefault(key, value)
        else:
            self.data[key] = value
        self._save()

    def get_settings(self):
        """
        Returns the whole dictionary self.data
        :return:
        """
        return self.data

    def remove(self, key):
        if key in self.data:
            self.data.pop(key)
            self._save()


class UserSettingsParameter(UserSettings):
    def __init__(self, directory, settings_type):
        UserSettings.__init__(self, directory, settings_type)

    def setdefault(self, par, key, value):
        """
        Works as setdefault for a dictionary. Should always be called with key and value.
        If data is set (key not in self.data) the dictionary is saved to json file.
        :param key:
        :param value:
        :return:
        """
        self.data.setdefault(par, {})
        value = self.data[par].setdefault(key, value)
        self._save()
        return value

    def set(self, par, key, value):
        """
        Sets key to value for parameter par
        :param par:
        :param key:
        :param value:
        :return:
        """
        self.data.setdefault(par, {})
        self.data[par].setdefault(key, value)
        self.data[par][key] = value
        self._save()

    def get(self, par, key):
        """

        :param par:
        :param key:
        :return:
        """
        return self.data.get(par, {}).get(key, None)
