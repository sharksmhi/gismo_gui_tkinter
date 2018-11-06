# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
'''
Created on 18 oct 2018

@author:
'''

import codecs

class AnalysisLogFile(dict):

    def __init__(self, file_path):
        self.file_path = file_path
        self.load_data()

    def load_data(self):

        with codecs.open(self.file_path, encoding='utf8') as fid:
            for line in fid:
                line = line.strip('\n\r')
                split_line = line.split('\t')
                if not split_line[0]:
                    continue

                edmo, cdi, file_name, info_type, info = split_line
                self.setdefault(edmo, {})
                self[edmo].setdefault(file_name, {})
                self[edmo][file_name]['cdi'] = cdi
                if not self[edmo][file_name].get('info'):
                    self[edmo][file_name]['info'] = []
                self[edmo][file_name]['info'].append(' '.join([info_type, info]))

