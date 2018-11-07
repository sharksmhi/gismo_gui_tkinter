# -*- coding: utf-8 -*-

import os
import pandas as pd

class Codelist():
    """
    Created 20181010
    Hold information in EEA codelist document.
    https://www.eea.europa.eu/data-and-maps/data/waterbase-transitional-coastal-and-marine-waters-9#tab-additional-information

    """
    def __init__(self, file_path=None):
        self.file_path = file_path
        if not self.file_path:
            self.file_path = os.path.join(os.path.dirname(__file__), 'Waterbase_TCM_v12_codelists.xls')
        if not os.path.exists(self.file_path):
            raise FileNotFoundError

        self._load_file()

    def _load_file(self):
        excel_object = pd.ExcelFile(self.file_path)
        self.df = {sheetname: excel_object.parse(sheetname) for sheetname in excel_object.sheet_names}

    def get_columns(self, sheet):
        """
        Created 20181010    by Magnus

        Returns the columns of the given sheet.
        :param sheet:
        :return:
        """
        if not self.df.get(sheet):
            raise KeyError

        return sorted(self.df.get(sheet).columns)

    def get_definition(self, value, sheet=None):
        if sheet:
            sheets = [sheet]
        else:
            sheets = self.df.keys()

        for s in sheets:
            df = self.df[s]
            result = df.loc[df['Value'] == value, 'Definition']
            if len(result):
                return result.values[0]




class Tabledefinition():
    """
    Created 20181010    by Magnus

    Hold information in EEA tabledefinition document.
    https://www.eea.europa.eu/data-and-maps/data/waterbase-transitional-coastal-and-marine-waters-9#tab-additional-information

    """
    def __init__(self, file_path=None):
        self.file_path = file_path
        if not self.file_path:
            self.file_path = os.path.join(os.path.dirname(__file__), 'Waterbase_TCM_v12_tabledefinitions.xls')
        if not os.path.exists(self.file_path):
            raise FileNotFoundError

        self._load_file()

    def _load_file(self):
        excel_object = pd.ExcelFile(self.file_path)
        self.df = {sheetname: excel_object.parse(sheetname) for sheetname in excel_object.sheet_names}


class StationMapping():
    """
    Hold information in EEA station information. Provided with every download of data at:
        https://www.eea.europa.eu/data-and-maps/data/waterbase-transitional-coastal-and-marine-waters-11

    """
    def __init__(self, file_paths=[]):
        if file_paths and type(file_paths) != list:
            file_paths = [file_paths]
        self.file_paths = file_paths
        if not self.file_paths:
            self.file_paths = [os.path.join(os.path.dirname(__file__), 'Waterbase_tcm_v12_Stations_Conventions.csv'),
                               os.path.join(os.path.dirname(__file__), 'Waterbase_tcm_v12_Stations_EIONET.csv'),
                               os.path.join(os.path.dirname(__file__), 'Waterbase_tcm_v12_Stations_Flux.csv')]
        for file_path in self.file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError

        self._load_file()

    def _load_file(self):
        self.df = []
        self.dfs = {}
        for file_path in self.file_paths:
            df = pd.read_csv(file_path, sep=',')
            if 'Latitude' not in df.columns:
                df['Latitude'] = df['Latitude_min']
                df['Longitude'] = df['Longitude_min']
            self.dfs[os.path.basename(file_path)] = df.copy(deep=True)
            df['source'] = os.path.basename(file_path)
            if not len(self.df):
                self.df = df.copy()
            else:
                self.df = self.df.append(df, sort=True)

        self.df['NationalStationID_lower'] = self.df['NationalStationID'].apply(lambda x: x.lower())


    def get_position(self, national_station_id, nr_str_digits=None):
        position = self.df.loc[self.df['NationalStationID_lower'] == national_station_id.lower(), ['Latitude', 'Longitude']].values
        if not len(position):
            print('national_station_id:', national_station_id)
            raise KeyError
        position = list(position[0])
        if nr_str_digits:
            position = [item[:nr_str_digits] for item in position]

        return position

    def get_lat(self, national_station_id, nr_str_digits=None):
        position = self.df.loc[self.df['NationalStationID_lower'] == national_station_id.lower(), 'Latitude'].values
        if not len(position):
            print('national_station_id:', national_station_id)
            raise KeyError
        position = position[0]
        if nr_str_digits:
            position = position[:nr_str_digits]
        return position

    def get_lon(self, national_station_id, nr_str_digits=None):
        position = self.df.loc[self.df['NationalStationID_lower'] == national_station_id.lower(), 'Longitude'].values
        if not len(position):
            raise KeyError
        position = position[0]
        if nr_str_digits:
            position = position[:nr_str_digits]
        return position

















