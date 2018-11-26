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