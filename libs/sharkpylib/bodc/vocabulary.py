# -*- coding: utf-8 -*-
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
'''
Created on 30 jun 2016

@author: a001985
'''

import urllib
import numpy as np
#from openpyxl import Workbook
import codecs
import re
import pandas as pd
import os
import time 



        

"""
===============================================================================
===============================================================================
"""
class Vocabulary():
    """
    Class to handle vocabulary things.
    """
    
    #==========================================================================
    def __init__(self, **kwargs):
        self.vocab_list = []
        self.vocab_info = {}
        self.all_keys = set()
        if kwargs.get('vocab_list'):
            self.vocab_list = kwargs.get('vocab_list')


    def load_vocab_info(self, **kwargs):
        for vocab in self.vocab_list:
            info = get_vocab_code_info(vocab, **kwargs)
            self.vocab_info[vocab] = info
            self.all_keys.update(info.keys())
        print('DONE!')

    def write_vocab_info_to_file(self, file_path):
        # Prepare data
        data = []
        for code in self.vocab_info:
            data_line = []
            for key in sorted(self.all_keys):
                data_line.append(self.vocab_info[code].get(key, ''))
            data.append(data_line)

        df = pd.DataFrame(data, columns=sorted(self.all_keys))

        df.to_csv(file_path, sep='\t', index=False)

     
    # #==========================================================================
    # def write_vocab_info(self,
    #                      vocab='P01',
    #                      map_vocab='',
    #                      file_path=False,
    #                      show_progress=False,
    #                      update=True):
    #
    #
    #     if file_path:
    #         key = vocab + map_vocab
    #         if update or key not in self.vocab_mapping:
    #             self.get_vocab_info(vocab=vocab,
    #                                  map_vocab=map_vocab,
    #                                  show_progress=show_progress)
    #
    #         fid = codecs.open(file_path, 'w', encoding='cp1252')
    #         fid.write(u'\t'.join(self.vocab_header[key][:len(self.vocab_mapping[key])]))
    #         fid.write(u'\n')
    #         for k in range(len(self.vocab_code_lists[vocab])):
    #             line = u'\t'.join([str(self.vocab_mapping[key][item][k]) for item in self.vocab_header[key]])
    #             fid.write(u'%s\n' % line)
    #
    #         fid.close()

            
   
class PrefLabel(dict): 
    """
    Class to extract information from a prefered label string. 
    """
    def __init__(self, pref_label_string, bodc_code=None):  
        self.string = pref_label_string 
        self.bodc_code = bodc_code 
        
        curly = re.findall('\{.*?\}', self.string)  
        
        # Substance
        if curly:
            self._substance(curly[0])
        
        # Species
        if len(curly) >= 2 and 'WoRMS' in self.string:
            self._species(curly[1])
        
        # Unit  
        self._unit(self.string)
        
        # Matrix
        matrix_string = re.findall('\}.*?\{', self.string)
        if len(matrix_string): # Biota 
            self._matrix(matrix_string[0])
        else: 
            self._matrix(self.string) 
            self._method(self.string) # Method
        
        
    def _substance(self, string): 
        if 'CAS' not in string:
            return
        substance = string.strip('{}')
        sub = [item.strip() for item in substance.split('CAS')]
        if len(sub) > 0:
            self['substance_id'] = sub[0]
        if len(sub) > 1:
            self['substance_cas'] = sub[1]
        
    
    def _species(self, string):
        # print('SPECIES: ', string)
        if 'WoRMS' not in string:
            return
        species = string.strip('{}') 
        self['species_latin_name'] = species.split('(')[0].strip() 
        self['worms'] = re.findall('(?<=WoRMS )[0-9]*', species)[0] 
        self['itis'] = re.findall('(?<=ITIS: )[0-9]*', species)[0] 
        # Could use "join" here if not match found. Not sure if worms and/or ITIS is always given 
        
        
        
        characteristics = re.findall('\[.*?\]', string)
        if characteristics:
            self._characteristics(characteristics[0])

        
    def _characteristics(self, string): 
        parts = re.findall('[A-Z][a-z]*: [a-z\- 0-9]*', string) 

        for part in parts:
            what, info = part.split(':')
            what = what.lower()
            if what == 'size':
                pass
            else:
                self[what] = info.strip()
                
                
    def _unit(self, string): 
        string = string.strip(' {}')
        if 'wet weight' in string: 
            self['ww/dw'] = 'wet weight'
        elif 'dry weight' in string:
            self['ww/dw'] = 'dry weight' 
        else:
            self['ww/dw'] = 'unknown'
        
        
    def _matrix(self, string):
        # print(string)
        if 'biota' in string: 
            self['matrix'] = 'biota'
        elif 'suspended particulate material' in string: 
            self['matrix'] = 'water column'
        elif 'sediment' in string: 
            self['matrix'] = 'sediment'
        
        
    def _method(self, string): 
        self['method'] = string.split('by ')[-1]
        


class VocabularyXML(object):
    """
    Handles informtion in a xml dump for a specific vocabulary.
    """
    def __init__(self, file_path):
        self.file_path = file_path

        self.id_to_preflabel = {}
        self.preflabel_to_id = {}


    def create_vocab_dicts(self, **kwargs):
        """
        Saves self.id_to_preflabel and self.preflabel_to_id
        Finds labels <dc:identifier> and <skos:prefLabel

        <dc:identifier>SDN:P01::SAGEMSFM</dc:identifier>
        <dce:identifier>SDN:P01::SAGEMSFM</dce:identifier>
        <dc:date>2008-10-16 16:27:06.0</dc:date>
        <skos:notation>SDN:P01::SAGEMSFM</skos:notation>
        <skos:prefLabel xml:lang="en">14C age of Foraminiferida (ITIS: 44030: WoRMS 22528) [Subcomponent: tests] in sediment by picking and accelerator mass spectrometry</skos:prefLabel>

        :return:
        """
        self.id_to_preflabel = {}
        self.preflabel_to_id = {}

        current_id = None
        with codecs.open(self.file_path, encoding='utf8') as fid:
            for line in fid:
                if line.startswith('<skos:notation>'):
                    current_id = line.split('::')[1].split('<')[0]
                elif line.startswith('<skos:prefLabel xml:lang="en">'):
                    preflabel = re.findall('(?<=<skos:prefLabel xml:lang="en">).*(?=</skos:prefLabel>)', line)[0]

                    # preflabel = line.split('>')[1].split('</')[0]

                    if kwargs.get('no_method') and 'by' in preflabel:
                        continue

                    if kwargs.get('no_grain_size') and '<' in preflabel:
                        print(preflabel)
                        continue

                    if kwargs.get('no_length') and 'length' in preflabel:
                        continue

                    if kwargs.get('no_sex') and 'Sex:' in preflabel:
                        continue

                    if kwargs.get('no_stage') and 'Stage:' in preflabel:
                        continue

                    if kwargs.get('not_strings') and any([item in preflabel for item in kwargs.get('not_strings')]):
                        continue


                    self.id_to_preflabel[current_id] = preflabel
                    self.preflabel_to_id[preflabel] = current_id

                    # if kwargs.get('no_method') and 'by' in preflabel:
                    #     continue
                    # if self.id_to_preflabel.get(current_id):
                    #     self.id_to_preflabel[current_id] = '{};{}'.format(self.id_to_preflabel[current_id], preflabel)
                    # else:
                    #     self.id_to_preflabel[current_id] = preflabel
                    #
                    # if self.preflabel_to_id.get(preflabel):
                    #     self.preflabel_to_id[preflabel] = '{};{}'.format(self.preflabel_to_id[preflabel], current_id)
                    # else:
                    #     self.preflabel_to_id[preflabel] = current_id



    def find_id_for_vocab_search_string(self, vocab_search_string, **kwargs):
        """
        vocab_search_string contains % as wildcard
        :param vocab_search_string:
        :return:
        """
        search_string = vocab_search_string.replace('%', '.*')

        id_list = []
        pl_list = []
        for key, value in self.preflabel_to_id.items():
            if re.findall(search_string, key):
                id_list.append(value)
                pl_list.append(key)
        if kwargs.get('pref_label'):
            return ';'.join(pl_list)
        else:
            return ';'.join(id_list)



def add_P01_to_P01_mapping_file(P01_mapping_file_path, vocabulary_xml_file_path=None, **kwargs):
    """
    Adds column P01 to a P01_mapping_file. Maps the "p01_search_string" columns in the P01_mapping file.
    Saves the file after mapping.

    :param P01_mappinf_file_path:
    :param vocabulary_xml_file_path:
    :return:
    """
    vxml = VocabularyXML(vocabulary_xml_file_path)
    vxml.create_vocab_dicts(**kwargs)

    df = pd.read_csv(P01_mapping_file_path, sep='\t')
    df['P01'] = df['vocab_search_string'].apply(vxml.find_id_for_vocab_search_string)
    df['prefLabel'] = df['vocab_search_string'].apply(lambda x: vxml.find_id_for_vocab_search_string(x, pref_label=True))

    df.to_csv(P01_mapping_file_path, sep='\t', index=False)



def get_vocab_code_info(code, from_vocab='', to_vocab='', **kwargs):

    if not from_vocab:
        raise AttributeError
    from_vocab = from_vocab.upper()
    mapping = {'definition': ['<skos:definition xml:lang="en">', '</skos:definition>'],
               'preflabel': ['<skos:prefLabel xml:lang="en">', '</skos:prefLabel>']}
    # mapping = {'definition': ['<skos:definition xml:lang="en">', '</skos:definition>'],
    #            'preflabel': ['<skos:prefLabel xml:lang="en">', '</skos:prefLabel>'],
    #            'to_vocab': ['http://vocab.nerc.ac.uk/collection/{}/current/'.format(to_vocab)]}

    url_path = 'http://vocab.nerc.ac.uk/collection/{}/current/{}/'.format(from_vocab, code)
    print(url_path)
    url = urllib.request.urlopen(url_path)
    text = str(url.read())

    result = {}
    # First check to_vocab. Can be several
    if to_vocab:
        if type(to_vocab) == str:
            to_vocab = [to_vocab]
        for v in to_vocab:
            v = v.upper()
            c = 'http://vocab.nerc.ac.uk/collection/{}/current/'.format(v)
            re_string = '(?<={})[A-Z0-9]+(?=/+?)'.format(c)
            res = re.findall(re_string, str(text))
            if not res:
                continue
            vr = get_vocab_code_info(res[0], v)
            for r in vr:
                result[r] = vr[r]

    result[from_vocab] = code

    # if kwargs.get('show_progress'):
    #     print('Searching information for {} code {}'.format(from_vocab, code))
    if kwargs.get('show_progress'):
        print('Will look for information for {} code {}'.format(from_vocab, code))

    for key, value in mapping.items():

        re_string = '(?<={}).+(?={})'.format(value[0], value[1])
        r = re.findall(re_string, str(text))

        if r:
            r = r[0]
            # if kwargs.get('show_progress'):
            #     print('Information for {} code {}\tOK!'.format(from_vocab, code))
        else:
            r = ''
            # if kwargs.get('show_progress'):
            #     print('Information for {} code {}\tNOT FOUND!'.format(from_vocab, code))

        result['{}_{}'.format(from_vocab, key)] = r

        # Handle prefLabel
        if 'preflabel' in key and kwargs.get('decompose_preflabel'):
            pref = PrefLabel(r)
            for p in pref:
                result['{}_{}'.format(from_vocab, p)] = pref[p]

    return result




"""
===============================================================================
===============================================================================
===============================================================================
===============================================================================
"""  
if __name__ == "__main__":
        
    if 1:
        pref_label_string = 'Concentration of lead {Pb CAS 7439-92-1} per unit wet weight of biota {Limanda limanda (ITIS: 172881: WoRMS 127139) [Sex: female Size: length 200-249mm Subcomponent: liver]}' 
        pref_label_string = "Concentration of cadmium {Cd CAS 7440-43-9} per unit dry weight of suspended particulate material by inductively-coupled plasma mass spectrometry and normalisation to organic carbon and lutum content (RIKZ 'standard sediment')"
#         pref_label_string = 'Concentration of lead {Pb CAS 7439-92-1} per unit wet weight of biota {Chelidonichthys kumu (ITIS: 167052: WoRMS 218122) [Subcomponent: muscle tissue]}'
        p = PrefLabel(pref_label_string)
        
        
        
        
            
            
            
            
            
            