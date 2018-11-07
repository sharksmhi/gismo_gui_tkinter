# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
@author:
"""
import os
import codecs
import pandas as pd


class DataFile(object):
    """
    DataFile is the data.csv file with metadata that is included in the buffer dataset.
    """
    def __init__(self, file_path):

        self.file_path = file_path
        self.df = pd.read_csv(self.file_path, sep=',')

    def get_cdi_record_id(self, local_cdi_id, **kwargs):
        """
        Returns a str of the CDI-record id corresponding to the local_cdi_id

        :param from_column:
        :return:
        """
        if type(local_cdi_id) == str:
            result = self.df.loc[self.df['LOCAL_CDI_ID']==local_cdi_id, 'CDI-record id'].values

        result = str(result[0])

        if kwargs.get('as_file_names'):
            result = '{}_ODV.txt'.format(result.zfill(8))
            if kwargs.get('directory'):
                result = '/'.join([kwargs.get('directory'), result])
        return result

    def load_cdi_record_id_mapping(self, local_cdi_id, **kwargs):
        """

        :return:
        """
        self.record_id_to_cdi = {}
        self.cdi_to_record_id = {}

        if type(local_cdi_id) == str:
            local_cdi_id = [local_cdi_id]

        for cdi in local_cdi_id:
            record_id = self.get_cdi_record_id(cdi, **kwargs)
            self.record_id_to_cdi[record_id] = cdi
            self.cdi_to_record_id[cdi] = record_id

    def get_record_id_list(self):
        return sorted(self.record_id_to_cdi)

    def save_cdi_record_mapping(self, file_path):
        df = pd.DataFrame.from_dict(self.cdi_to_record_id)
        df.to_csv(file_path, sep='\t', index=False)


