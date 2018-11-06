# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on Wed Dec 10 17:37:24 2014

@author:
"""

"""
This module contains classes that handles ODV history files. 

"""
import os 
import codecs
import pandas as pd
import re

#==============================================================================
#==============================================================================
class HistoryFlagFile(object): 
    """
    Created:    20180525
    Updated:    20180529
        
    Handles History files only containing the tag "EDITFLAGS". 
    Data will be filtered for ""EDITFLAGS
    """
    
    def __init__(self, file_path): 
        self.file_path = file_path 
        self._load_file()
        
    #==========================================================================
    def _load_file(self):
        header = ['info', 'time', 'user', 'type', 'comment']
        self.df = pd.read_csv(self.file_path, sep='\t', encoding='cp1252', header=None)
        self.df.columns = header
    
        self.df['local_cdi_id'] = self.df['info'].apply(self._add_local_cdi_id_column_from_info)
        self.df['edmo'] = self.df['info'].apply(self._add_edmo_column_from_info)
        self.df['QF'] = self.df[['type', 'comment']].apply(self._add_flag_column, axis=1)
        self.df['par'] = self.df['comment'].apply(self._add_par_column)
        self.df['flag_depth'] = self.df['comment'].apply(self._add_flag_depth_column)
    
        self.df.sort_values(['local_cdi_id', 'par'], inplace=True)
        
        
    #==========================================================================
    def _add_local_cdi_id_column_from_info(self, x): 
        return x.split(':')[1].strip().split(' ')[0] 

    
    #==========================================================================
    def _add_edmo_column_from_info(self, x): 
        return x.split(':')[1].strip().split(' ')[-1][:-1]
    
    
    #==========================================================================
    def _add_flag_column(self, x): 
        if x[0] == 'EDITFLAGS':
            return x[1][-1]
        else:
            return ''
            
    
    #==========================================================================
    def _add_par_column(self, x): 
        return x.split('@')[0].strip()
    
    
    #==========================================================================
    def _add_flag_depth_column(self, x): 
        return x.split('=')[1].strip()
    
    
    #==========================================================================
    def _add_from_flag_column(self, x):
        from_flag = re.findall('(?<=\d:)\d*', x)
        return ';'.join(from_flag)
    
    
    #==========================================================================
    def _add_to_flag_column(self, x):
        return x[-1]
    
    
    #==========================================================================
    def _get_boolean_from_kwargs(self, **kwargs): 
        boolean = ()
        for key, item in kwargs.items():
            if not len(boolean):
                boolean = self.df[key] == item
            else:
                boolean = boolean & (self.df[key] == item)
        return boolean
    
    
    #==========================================================================
    def add_from_flag_column(self):
        self.df['from_flag'] = self.df['flag_depth'].apply(self._add_from_flag_column)
    
    
    #==========================================================================
    def add_to_flag_column(self):
        self.df['to_flag'] = self.df['flag_depth'].apply(self._add_to_flag_column)
    
    
    #==========================================================================
    def get_local_cdi_list(self, unique=False, **kwargs):
        
        boolean = self._get_boolean_from_kwargs(**kwargs) 
        
        if len(boolean):
            df = self.df.loc[boolean, :]
        else:
            df = self.df
            
        if unique:
            return sorted(set(df['local_cdi_id']))
        else:
            return sorted(df['local_cdi_id'])
        
    
    #==========================================================================
    def get_unique_par_list(self):
        return sorted(set(self.df['par']))
        
        
    #==========================================================================
    def write_to_file(self, file_path, columns=[], sep='\t', include_odv_cdi_list=False, **kwargs):
        
        boolean = self._get_boolean_from_kwargs(**kwargs)

        if not columns:
            columns = self.df.columns
        if len(boolean):
            self.df.loc[boolean, :].to_csv(file_path, columns=columns, sep=sep, index=False)
        else:
            self.df.to_csv(file_path, columns=columns, sep=sep, index=False)
        
        if include_odv_cdi_list:
            cdi_list = self.get_local_cdi_list(unique=True, **kwargs) 
            with codecs.open(file_path, 'a') as fid:
                fid.write(' || '.join(cdi_list))
        
        
    #==========================================================================
    def write_flags_for_all_local_cdi_id(self, directory, exclude_par='', not_in_flag_depth='', additional_columns=[], **kwargs): 
        
        pars = ['local_cdi_id', 'par', 'flag_depth' ]
        pars.extend(additional_columns)
#        print(pars)
        all_cdi_id = set()
        for cdi in self.get_local_cdi_list(unique=True): 
            df = self.df.copy()
            boolean = self._get_boolean_from_kwargs(**kwargs)
            
            if len(boolean):
                df = df.loc[boolean, :]
            
            df = df.loc[df['local_cdi_id']==cdi, pars]
            
            
            
            if not_in_flag_depth: 
                df = df.loc[~df['flag_depth'].str.contains(not_in_flag_depth)]
            
            if not len(df):
                continue
            
            set_par = list(set(df['par'].values))

            if len(set_par)==1 and set_par[0] == exclude_par:
                continue 
            else:
                file_path = os.path.join(directory, 'flags_for_local_cdi_id_{}.txt'.format(cdi)) 
                df.to_csv(file_path, sep='\t', index=False, encoding='cp1252')
                all_cdi_id.add(cdi)
        
        with codecs.open(os.path.join(directory, 'all_flagged_local_cdi_id_odv_style.txt'), 'w') as fid: 
            fid.write(' || '.join(sorted(all_cdi_id)))
        
    #==========================================================================
    def write_local_cdi_id_list_to_file(self, file_path, for_odv=False, mode='w', **kwargs): 
        directory = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        
        if for_odv: 
            new_file_path = '{}/local_cdi_list_odv_{}'.format(directory, file_name)
            sep = ' || '
        else:
            new_file_path = '{}/local_cdi_list_{}'.format(directory, file_name)
            sep = '\n'
        
        
        
        cdi_list = self.get_local_cdi_list(unique=True, **kwargs) 
        with codecs.open(new_file_path, mode) as fid:
            fid.write(sep.join(cdi_list))
    
    
    #==========================================================================
    def write_list_per_local_cdi_id(self): 
        pass
    
    
#==============================================================================
#==============================================================================
class StationClass(object):
    
    def __init__(self, local_cdi_id, acc_nr):
        self.local_cdi_id = local_cdi_id
        self.acc_nr = acc_nr
        self.import_lines = []
        
    def add_import(self, import_line):
        self.import_lines.append(import_line)
        
        
#==============================================================================
#==============================================================================
class HistoryLine(object):
    
    def __init__(self, line):
        
        splited_line = line.split()
        self.line = line
        self.acc_nr = splited_line[0][1:-1]
        self.local_cdi_id = splited_line[1]
        self.edmo = splited_line[2][:-1]
        self.time.append(splited_line[3])
        self.who.append(splited_line[4])
        self.action.append(splited_line[5])
        if 'ADD' in line:
            i = 7
        else:
            i = 6
            
        self.allinfo = ' '.join(splited_line[i:])


#==============================================================================
#==============================================================================
class HistoryFile(object):
    
    #==========================================================================
    def __init__(self, file_name):
        
        self.nr = []
        self.ID = []
        self.EDMO = []
        self.date = []
        self.who = []
        self.action = []
        self.allinfo = []
        self.editflags = {}
        
        f = open(file_name,'r')
        
        for line in f:
            splited_line = line.split()
            nr = splited_line[0][1:-1]
            self.nr.append(nr)
            ID = splited_line[1]
            self.ID.append(ID)
            edmo = splited_line[2][:-1]
            self.EDMO.append(edmo)
            self.date.append(splited_line[3])
            self.who.append(splited_line[4])
            self.action.append(splited_line[5])
            
            allinfo = ' '.join(splited_line[6:])
            self.allinfo.append(allinfo)
            
            if 'EDITFLAGS' in line:
                par, flag_all = [item.strip() for item in allinfo.split('@')]
                slask, rest = [item.strip() for item in flag_all.split(' = ')]
                to_flag = rest[-1]
                rest = rest[1:-6]
                pair = rest.split(' ')
                for p in pair:
                    d,fl = p.split(':')
                
                if edmo not in self.editflags:
                    self.editflags[edmo] = {}
                if par not in self.editflags[edmo]:
                    self.editflags[edmo][par] = {}
                if ID not in self.editflags[edmo][par]:
                    self.editflags[edmo][par][ID] = {}
                    self.editflags[edmo][par][ID][u'Accession Number'] = nr
                    self.editflags[edmo][par][ID][u'All_flags'] = []
                
                if flag_all not in self.editflags[edmo][par][ID]:
                    self.editflags[edmo][par][ID][u'All_flags'].append(flag_all)
 
        f.close()
        
    #==========================================================================
    def print_flags(self):
        nr_signs = 100
        print('%'*nr_signs)
        print('%'*nr_signs)
        for edmo in sorted(self.editflags):
            print('='*nr_signs)
            for par in self.editflags[edmo]:
                print('-'*nr_signs)
                for ID in self.editflags[edmo][par]:
                    for flag in self.editflags[edmo][par][ID][u'All_flags']:
                        print(ID, self.editflags[edmo][par][ID][u'Accession Number'], flag)
                        
            
            
            
        print('%'*nr_signs)
        print('%'*nr_signs)
            
            
    #==========================================================================
    def get_local_cdi_id_list(self, include_par=[], exclude_par=[], only_to_flag=[], edmo_code=None):
        """ 
        Returns a list of all LOCAL_CDI_IDs that has been flagged. 
        Options can be given. 
        """
        only_to_flag = map(str, only_to_flag)
        output_list = []
        for edmo in sorted(self.editflags, key=int):
            if edmo_code and edmo != edmo_code:
                continue
            for par in sorted(self.editflags[edmo]):
                if par in exclude_par:
                    continue
                if not include_par or par in include_par:
                    for ID in sorted(self.editflags[edmo][par]):
                        for flag_string in self.editflags[edmo][par][ID][u'All_flags']:
                            flag = flag_string.strip()[-1]
                            if only_to_flag:
                                if flag in only_to_flag:
                                    if ID not in output_list:
                                        output_list.append(ID)
                            else:
                                output_list.append(ID)
                    
        return output_list
        
        
    #==========================================================================
    def write_flagged_local_cdi_id_by_edmo_and_par(self, directory=u''):
        
        for edmo in self.editflags:
            fid = codecs.open(directory + u'/flagged_%s.txt' % edmo, 'w')
            fid.write(u'LOCAL_CDI_ID that has been flagged for EDMO: %s\n' % edmo)
            for par in sorted(self.editflags[edmo]):
                fid.write(u'%s\n' % par)
                cdi_list = self.get_local_cdi_id_list(include_par=[par], edmo_code=edmo)
                for ID in sorted(cdi_list):
                    fid.write(u'%s\t%s\t%s\n' % (ID, 
                                             self.editflags[edmo][par][ID][u'Accession Number'], 
                                             u';'.join(self.editflags[edmo][par][ID][u'All_flags'])))
                    
            
            fid.close()
        

    #==========================================================================
    def write_flags_to_file(self, file_path):
        
        fid = codecs.open(file_path, 'w', encoding='cp1252')
        header = [u'Accession Number', u'EDMO_code', u'LOCAL_CDI_ID', u'Parameter', u'Depths flagged']
        
        fid.write(u'\t'.join(header) + u'\n')
        
        for edmo in sorted(self.editflags, key=int):
            for par in sorted(self.editflags[edmo]):
                for ID in sorted(self.editflags[edmo][par]):
                    for flag in sorted(self.editflags[edmo][par][ID]['All_flags']):            
                        fid.write(u'\t'.join([ID, edmo, self.editflags[edmo][par][ID][u'Accession Number'], par, flag]) + u'\n')
            
        fid.close()
            
