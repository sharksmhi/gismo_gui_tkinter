# -*- coding: utf-8 -*-
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import sys
import pandas as pd
import numpy as np

from . import mapping

lib_path = os.path.dirname(os.path.dirname(__file__))
if lib_path not in sys.path:
    sys.path.append(lib_path)

import mapping_lib


class HazardSubstances(object):
    """
    Created 20181010

    Contains and handled information on EEA hazard substances data.
    https://www.eea.europa.eu/data-and-maps/data/waterbase-transitional-coastal-and-marine-waters-11

    kwargs can contain paths to mapping files:
        tabledefinition_file_path
        codelist_file_path
        station_mapping_file_path

    """
    def __init__(self, file_path, only_swedish_data=True, **kwargs):
        self.file_path = file_path

        print('Loading: Tabledefinition')
        self.table_def = mapping.Tabledefinition(kwargs.get('tabledefinition_file_path', None))
        print('Loading: Codelist')
        self.codelist = mapping.Codelist(kwargs.get('codelist_file_path', None))
        print('Loading: StationMapping')
        self.station_mapping = mapping.StationMapping(kwargs.get('station_mapping_file_path', None))

        print('Loading: datafile...')
        self._load_file(only_swedish_data=only_swedish_data)

        print('Adding columns...')
        self._add_columns(**kwargs)

        print('DONE!')

    def _load_file(self, **kwargs):
        self.row_df = pd.read_csv(self.file_path, sep=',', dtype=str)

        # Fill nan
        self.row_df.fillna('', inplace=True)

        if kwargs.get('only_swedish_data'):
            self.row_df = self.row_df.loc[self.row_df['DataProvider'] == 'SE', :]
            # self.row_df.reset_index(inplace=True)

    def _add_columns(self, **kwargs):
        for statn in set(self.row_df['NationalStationID']):
            lat, lon = '', ''
            try:
                lat, lon = self.station_mapping.get_position(statn)
                lat = mapping_lib.to_decmin(lat)
                lon = mapping_lib.to_decmin(lon)

                # self.row_df['LATIT'] = mapping_lib.to_decmin(lat)
                # self.row_df['LONGI'] = mapping_lib.to_decmin(lon)
            except:
                lat, lon = '', ''
                # lat, lon = self.station_mapping.get_position(statn)
                # print('No station mapping for:', statn, lat, lon)
                # self.row_df['LATIT'] = mapping_lib.to_decmin(lat)
                # self.row_df['LATIT'] = ''
                # self.row_df['LONGI'] = ''
            self.row_df.loc[self.row_df['NationalStationID'] == statn, 'LATIT'] = lat
            self.row_df.loc[self.row_df['NationalStationID'] == statn, 'LONGI'] = lon

        self.row_df['STATN'] = self.row_df['NationalStationID']

        # Check Basis. List 20181003:
        # D - Dry weight (biota, sediment)
        # L - Lipid (fat) weight (biota)
        # W - Wet weight (biota, sediment)
        basis_set = set(self.row_df['Basis'])
        # print('\nBasis')
        for b in basis_set:
            if str(b) == 'nan':
                self.row_df.loc[self.row_df['Basis'] == b, 'Basis'] = ''
            else:
                # print(b)
                definition = self.codelist.get_definition(b.upper(), sheet='Basis')
                # print(b, 'definition', definition)
                if definition:
                    definition = definition.split('(')[0].strip().lower()
                else:
                    definition = b
                self.row_df.loc[self.row_df['Basis'] == b, 'Basis'] = definition

        if 'Tissue' in self.row_df.columns:
            # Tissue
            tissue_set = set(self.row_df['Tissue'])
            # print('\nTissue')
            for t in tissue_set:
                if str(t) == 'nan':
                    self.row_df.loc[self.row_df['Tissue'] == t, 'Tissue'] = ''
                else:
                    # print(t)
                    definition = self.codelist.get_definition(t.upper(), sheet='Tissue')
                    # print(t, 'definition', definition)
                    if definition:
                        if definition == 'Soft body':
                            definition = 'flesh'
                        definition = definition.split('(')[0].strip().lower()
                    else:
                        definition = t
                    self.row_df.loc[self.row_df['Tissue'] == t, 'Tissue'] = definition

            self.row_df['matrix'] = 'biota'
        else:
            self.row_df['matrix'] = 'sediment'


        print('Adding id-column...')
        # No time in dataset
        self.row_df['id'] = self.row_df['Year'].astype(str) + '-' + \
                            self.row_df['Month'].astype(str).apply(lambda x: x.zfill(2)) + '-' + \
                            self.row_df['Day'].astype(str).apply(lambda x: x.zfill(2)) + '_' + \
                            self.row_df['LATIT'].apply(lambda x: str(x)[:kwargs.get('id_pos_precision', 6)]) + '_' + \
                            self.row_df['LONGI'].apply(lambda x: str(x)[:kwargs.get('id_pos_precision', 6)])

        self.row_df['station_id'] = self.row_df['Year'].astype(str) + '-' + \
                                    self.row_df['Month'].astype(str).apply(lambda x: x.zfill(2)) + '-' + \
                                    self.row_df['Day'].astype(str).apply(lambda x: x.zfill(2)) + '_' + \
                                    self.row_df['NationalStationID']





    def get_vocab_search_string_list(self, file_path=None):
        """
        Checks the self.row_df dataframe for unique combinations of:

        :return:
        """
        if 'Species' in self.row_df.columns:
            include_pars = ['Determinand_HazSubs', 'CASNumber', 'Basis', 'Species', 'Tissue', 'matrix']
            p01_id_pars = ['CASNumber', 'Basis', 'Species', 'Tissue']
        else:
            include_pars = ['Determinand_HazSubs', 'CASNumber', 'Basis', 'matrix']
            p01_id_pars = ['CASNumber', 'Basis', 'matrix']

        df = self.row_df[include_pars].drop_duplicates()
        df['vocab_search_string'] = df[p01_id_pars].apply(lambda x: '%'.join([str(item) for item in x]), axis=1)

        if file_path:
            df.to_csv(file_path, sep='\t', index=False)

        return df

