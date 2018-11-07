# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
@author:
"""

import os
import codecs


class ModifyODVfile(object):

    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise IOError
        self.file_path = file_path


    def convert_to_time_series(self, **kwargs):
        """
        Converts the file to a time series by adding the column "time_ISO8601" as first and primary variable
        //<subject>SDN:LOCAL:time_ISO8601</subject><object>SDN:P01::DTUT8601</object><units>SDN:P06::TISO</units>

        New file is save in sub directory "as_timeseries"

        :return:
        """

        primary_par = 'time_ISO8601'
        primary_semantic = '//<subject>SDN:LOCAL:time_ISO8601</subject><object>SDN:P01::DTUT8601</object><units>SDN:P06::TISO</units>\n'

        output_directory = os.path.join(os.path.dirname(self.file_path), 'as_timeseries')
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        output_file_path = os.path.join(output_directory, os.path.basename(self.file_path))

        semantic_added = False
        with codecs.open(output_file_path, 'w', encoding=kwargs.get('encoding_out', kwargs.get('encoding', 'utf8'))) as fid_out:
            with codecs.open(self.file_path, encoding=kwargs.get('encoding_in', kwargs.get('encoding', 'utf8'))) as fid_in:
                for line in fid_in:
                    if not line.strip():
                        continue
                    if line.startswith('//'):
                        if line.startswith('//<subject>'):
                            if not semantic_added:
                                fid_out.write(primary_semantic)
                                semantic_added = True
                        fid_out.write(line)
                    elif line.startswith('Cruise'):
                        split_line = line.split('\t')
                        header = split_line
                        new_header = []
                        for c, col in enumerate(header):
                            new_header.append(col)
                            if 'yyyy-mm-dd' in col:
                                time_col = c
                            elif 'bot' in col.lower() and 'depth' in col.lower():
                                primary_col = c+1
                                new_header.append(primary_par)
                        fid_out.write('\t'.join(new_header))
                    else:
                        split_line = line.split('\t')
                        new_split_line = []
                        for c, item in enumerate(split_line):
                            if c == primary_col:
                                new_split_line.append(split_line[time_col])
                            new_split_line.append(item)
                        fid_out.write('\t'.join(new_split_line))

    def remove_whitespace_in_parameters(self, **kwargs):
        """
        Created to remove whitespace in header and semantic header to ensure match. Example:
        '<  63_SIVUB_F2_NDT'
        '< 63_SIVUB_F2_NDT'

        :param kwargs:
        :return:
        """

        new_lines = []
        with codecs.open(self.file_path, encoding=kwargs.get('encoding_in', kwargs.get('encoding', 'utf8'))) as fid_in:
            for line in fid_in:
                line = line.strip('\n\r')
                if line.startswith('//<subject>SDN:LOCAL:'):
                    line = line.replace(' ', '')
                elif line.startswith('Cruise'):
                    split_line = [par.strip() for par in line.split('\t')]
                    new_split_line = []
                    for item in split_line:
                        split_item = item.split('[')
                        if split_item[0].strip() not in ['Bot. Depth']:
                            split_item[0] = split_item[0].replace(' ', '')
                            item = ' ['.join(split_item)

                        new_split_line.append(item)
                    line = '\t'.join(new_split_line)
                new_lines.append(line)

        file_path = kwargs.get('save_file_path', self.file_path)
        with codecs.open(file_path, 'w', encoding=kwargs.get('encoding_out', kwargs.get('encoding', 'utf8'))) as fid_out:
            fid_out.write('\n'.join(new_lines))




