# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
import os
import json


class User(object):
    def __init__(self, name, user_root_directory):
        self.name = name

        self.user_directory = os.path.join(user_root_directory, self.name)
        if not os.path.exists(self.user_directory):
            os.mkdir(self.user_directory)

        self.range = UserSettingsParameter(self.user_directory, 'range')
        self.settingsfile = UserSettings(self.user_directory, 'settingsfile')

        self.flag_color = UserSettings(self.user_directory, 'flag_color')
        self.flag_markersize = UserSettings(self.user_directory, 'flag_markersize')


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

    def get(self, key):
        """

        :param key:
        :return:
        """
        return self.data.get(key, None)

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
        return self.data[par].get(key, None)

