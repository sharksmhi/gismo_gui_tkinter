# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).



def data_file_selected(**kwargs):
    user = ''
    if kwargs.get('username'):
        user = ' ({})'.format(kwargs.get('username'))
    text = """
           You have just selected a data file. "Settings file" and "Sampling type" have automatically been changed to 
           the current user{} default settings. MAKE SURE YOU select the correct settings each time you select a datafile. 
           By changing the two options you also change the default settings. 
           """.format(user)
    return text

def flag_widget_help_text(**kwargs):
    text = 'Flag data by selecting a range under tab "Selects data to flag". ' \
           'Then choose a flag in the left column below and press "Flag selected data". ' \
           'In the second column below you can decide which flags to show by clicking the boxes and then ' \
           'press "Update flags to show". You can also choose color and marker size for the different flags.'
    return text





def about():
    text = """
           GISMOtoolbox is a ...
           """
    return text