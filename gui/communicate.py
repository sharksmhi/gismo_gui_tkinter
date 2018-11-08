#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import numpy as np

import core


import libs.sharkpylib.gismo as gismo
import libs.sharkpylib.tklib.tkinter_widgets as tkw

import logging 

"""
================================================================================
================================================================================
================================================================================
""" 
def add_sample_data_to_plot(plot_object=None, 
                                par=None, 
                                sample_object=None, 
                                gismo_object=None, 
                                compare_widget=None, 
                                help_info_function=None): 
    """
    sample_object is the main GISMOfile. 
    gismo_object is the file where matching data will be extracted from 
    """
    print('add_sample_data_to_plot')
    if not core.Boxen().sample_index or compare_widget.values_are_updated:
        if help_info_function:
            help_info_function('Adding reference data...please wait...')
            
        if not all([sample_object, gismo_object]):
            help_info_function('Ferrybox and/or sample file not loaded. Could not compare data!')
            return
            
#        modulus = 1
        diffs = {}
        if compare_widget:
#            modulus = compare_widget.modulus
            diffs['time'] = compare_widget.time
            diffs['dist'] = compare_widget.dist
            diffs['depth'] = compare_widget.depth
            
        index = gismo.get_matching_sample_index(sample_object=sample_object, 
                                                       gismo_object=gismo_object, 
#                                                       modulus=modulus, 
                                                       diffs=diffs)
        core.Boxen().sample_index = index
    else:
        index = core.Boxen().sample_index
#    print 'index', index
    # Get data
    if not len(index):
        logging.debug('No matching data found')
        help_info_function('No matching data found!')
        core.Boxen().sample_index = []
        return
    par = sample_object.parameter_mapping.get_external(par)
    if par not in sample_object.df.columns:
        logging.debug('No parameter named "%s" in sample data file.' % par)
        help_info_function('No parameter named "%s" in sample data file.')
        return
#    qpar = sample_object.get_qf_par(par)
    time_list = np.array(sample_object.df.ix[index, 'time'])
    value_list = np.array(sample_object.df.ix[index, par])
#    qf_list = gismo_object.df.ix[index, qpar]
    core.Temp().time_list = time_list
    core.Temp().value_list = value_list
    
    print('matching data')
    plot_object.set_data(x=time_list, y=value_list, line_id='matching data', marker='x', color='black')
    
    if help_info_function:
        help_info_function('Done!')
        

"""
================================================================================
================================================================================
================================================================================
""" 
def add_sample_data_to_boxen(par=None, 
                                sample_object=None, 
                                gismo_object=None, 
                                compare_widget=None, 
                                help_info_function=None): 
    """
    UNDER CONSTRUCTON!
    sample_object is the main GISMOfile. 
    gismo_object is the file where matching data will be extracted from 
    """
    
    # Remove old data
    core.Boxen().sample_data = {}
    
    if not core.Boxen().sample_index or compare_widget.values_are_updated:
        if help_info_function:
            help_info_function('Adding reference data...please wait...')
            
        if not all([sample_object, gismo_object]):
            return
            
#        modulus = 1
        diffs = {}
        if compare_widget:
#            modulus = compare_widget.modulus
            diffs['time'] = compare_widget.time
            diffs['dist'] = compare_widget.dist
            diffs['depth'] = compare_widget.depth
            
        index = gismo.get_matching_sample_index(sample_object=sample_object, 
                                                       gismo_object=gismo_object, 
#                                                       modulus=modulus, 
                                                       diffs=diffs)
        core.Boxen().sample_index = index
    else:
        index = core.Boxen().sample_index
#    print 'index', index
    # Get data
    if not len(index):
        logging.debug('No matching data found')
        core.Boxen().sample_index = []
        return
    par = sample_object.parameter_mapping.get_external(par)
    if par not in sample_object.df.columns:
        logging.debug('No parameter named "%s" in sample data file.' % par)
        return


    time_list = sample_object.get_column('time')
    lat_list = sample_object.get_column('lat')
    lon_list = sample_object.get_column('lon')
    
    value_list = sample_object.get_column(par)
    
    if par == 'time':
        value_list = sample_object.get_column(par, time_as_datenum=True)
 
    else:
        value_list = sample_object.get_column(par)
    
    core.Boxen().set_sample_data(lat=lat_list[index], 
                                            lon=lon_list[index], 
                                            t=time_list[index], 
                                            values=value_list[index])
                                            
    if help_info_function:
        help_info_function('Done!')
    
"""
================================================================================
================================================================================
================================================================================
""" 
def get_flag_widget(parent=None, 
                    settings_object=None,
                    callback_flag_data=None, 
                    callback_update=None, 
                    callback_prop_change=None,
                    include_marker_size=True,
                    **kwargs):

    if settings_object:

        # Flags are sorted
        flags = settings_object.get_flag_list()
        descriptions = settings_object.get_flag_description_list()
        nr_flags = len(flags)
        # colors = settings_object.get_flag_color_list()
        # markersize = settings_object.get_flag_markersize_list()
    else:
        nr_flags = 6
        flags = list(range(nr_flags))
        descriptions = ['unknown']*nr_flags

    colors = ['red' if flags[i] in [4, 8] else 'black' for i in range(nr_flags)]
    markersize = [6] * nr_flags

    flag_widget = tkw.FlagWidget(parent, 
                                  flags=flags, 
                                  descriptions=descriptions, 
#                                              colors=set(colors),
                                  default_colors=colors, 
                                  markersize=markersize, 
                                  include_marker_size=include_marker_size, 
                                  callback_flag_data=callback_flag_data, 
                                  callback_update=callback_update, 
                                  callback_prop_change=callback_prop_change, 
                                  **kwargs) 
                                              
    return flag_widget
                                                  
"""
================================================================================
================================================================================
================================================================================
""" 
def flag_data_time_series(flag_widget=None, 
                          gismo_object=None, 
                          plot_object=None, 
                          par=None):
    """
    Flag data in the given gismo_object. 
    Takes limits from plot_object and 
    flag information from tkw.FlagWidget. 
    """
    selection = flag_widget.get_selection()
    flag_nr = selection.flag
    
    index = plot_object.get_marked_index()
    print('index[0]', index[0])
    gismo_object.flag_parameter_at_index(par=par, 
                                         index=index, 
                                         qflag=flag_nr) 
    # Flag dependent parameters
    dependent_list = gismo_object.get_dependent_parameters(par)
    if dependent_list:
        print('par', par)
        for sub_par in dependent_list:
            print('sub_par', sub_par)
            gismo_object.flag_parameter_at_index(par=sub_par, 
                                                 index=index, 
                                                 qflag=flag_nr) 
                                                                 
"""
================================================================================
================================================================================
================================================================================
""" 
def flag_data_profile(flag_widget=None, 
                      profile=None, 
                      plot_object=None, 
                      par=None):
    """
    Flag data in the given gismo_objects for profiles in profile_infos (keys). 
    Takes limits from plot_object and 
    flag information from tkw.FlagWidget. 
    """
    
    selection = flag_widget.get_selection()
    flag_nr = selection.flag
     
    index = plot_object.get_marked_index()

    profile.gismo_object.flag_parameter_at_profile_index(time_object=profile.time, 
                                                         par=par, 
                                                         index=index, 
                                                         qflag=flag_nr) 
#     # Flag dependent parameters
#     dependent_list = gismo_object.get_dependent_parameters(par)
#     if dependent_list:
#         print 'par', par
#         for sub_par in dependent_list:
#             print 'sub_par', sub_par
#             core.Boxen().current_ferrybox_object.flag_parameter_at_index(par=sub_par, 
#                                                                  index=index, 
#                                                                  qflag=flag_nr) 

"""
================================================================================
================================================================================
================================================================================
""" 

#===========================================================================
def update_range_selection_widget(plot_object=None, 
                                  range_selection_widget=None):
    """
    Updates entries in range_selection_widget. 
    This is to get live update from the plot when "mark range" is active.
    line_id='current_flags' indicates that alla flags that are ploted are taken into consideration. 
    """
    logging.debug('IN: update_range_selection_widget')
    min_value = None
    min_value = None
    
    min_value = plot_object.get_mark_from_value(ax='first')
    max_value = plot_object.get_mark_to_value(ax='first')
    
    if min_value > max_value:
        min_value = None
        max_value = None

    # For time series plot
    
    
    # Set range in entries
    if min_value != None:
        range_selection_widget.set_min(min_value)
#        range_selection_widget.stringvar_min.set(min_value)
    else:
        range_selection_widget.set_min(None)
#        range_selection_widget.stringvar_min.set(u'')
    
    
    if max_value != None:
        range_selection_widget.set_max(max_value)
#        range_selection_widget.stringvar_max.set(max_value)
    else:
        range_selection_widget.set_max(None)
#        range_selection_widget.stringvar_max.set(u'')
        
        
"""
================================================================================
================================================================================
================================================================================
""" 
def update_profile_plot(profiles=None, 
                        par=None, 
                        plot_object=None, 
                        flag_widget=None, 
                        help_info_function=None):
    """
    Updates the plot_object (profiles) using information from profiles, par and flag_widget.
    Keys in profile_infos is the ones 
    If help_info_function (updating tkText) is given text information is passed to the funktion. 
    """
    if help_info_function:
        help_info_function('Updating profile plot...please wait...')
    plot_object.reset_plot()
    
    for key in sorted(profiles):
        t = profiles[key].time
        gismo_object = profiles[key].gismo_object
        display_name = profiles[key].display_name
#         depth = gismo_object.get_profile(t, 'depth')
#         parameter = gismo_object.get_profile(t, par)
     
        settings = gismo_object.settings
        selection = flag_widget.get_selection()
        
    
        # Plot individual flags
        for k, flag in enumerate(selection.selected_flags):
             
            depth = gismo_object.get_profile(t, 'depth')
            parameter = gismo_object.get_profile(t, par, qf_list=flag)
#             print 'len(depth)', len(depth)
#             print 'len(parameter)', len(parameter)
             
            if all(np.isnan(parameter)):
    #            print 'No data for flag "%s", will not plot.' % flag
                continue
            prop = settings.get_flag_prop_dict(flag)
            prop.update(selection.get_prop(flag)) # Is empty if no settings file is added while loading data
            prop.update({'linestyle':''})
            plot_object.set_data(x=parameter, y=-depth, line_id='_'.join([display_name, flag]), call_targets=False, **prop)
        
    plot_object.call_targets()
    
    if help_info_function:
        help_info_function('Done!')
        
 
"""
================================================================================
================================================================================
================================================================================
""" 
def update_highlighted_profile_in_plot(profile=None, 
                                        par=None, 
                                        plot_object=None, 
                                        flag_widget=None, 
                                        help_info_function=None):
    
    
    selection = flag_widget.get_selection()
    
    t = profile.time
    gismo_object = profile.gismo_object
    settings = gismo_object.settings
    
    
    if par:
        depth = gismo_object.get_profile(t, 'depth')
        parameter = gismo_object.get_profile(t, par, qf_list=selection.selected_flags)
    else:
        depth = np.array([])
        parameter = np.array([])
    
    prop = {'linestyle': '', 
            'marker': None,}
    plot_object.set_data(x=parameter, y=-depth, line_id='current_flags', call_targets=False, **prop)
   
    # Plot individual flags
    for k, flag in enumerate(selection.selected_flags):
        
        if par:
            depth = gismo_object.get_profile(t, 'depth')
            parameter = gismo_object.get_profile(t, par, qf_list=flag)
        else:
            depth = np.array([])
            parameter = np.array([])

        if parameter.size and all(np.isnan(parameter)):
#            print 'No data for flag "%s", will not plot.' % flag
            continue
        prop = settings.get_flag_prop_dict(flag)
        prop.update(selection.get_prop(flag)) # Is empty if no settings file is added while loading data
        markersize = prop['markersize']
        prop.update({'linestyle':'', 
                     'markersize': markersize+5})
        plot_object.set_data(x=parameter, y=-depth, line_id='_'.join(['heighlighted', profile.display_name, flag]), call_targets=False, **prop)
        
    plot_object.call_targets()
    
    if help_info_function:
        help_info_function('Done!')
    
"""
================================================================================
================================================================================
================================================================================
""" 
def update_time_series_plot(gismo_object=None, 
                            par=None, 
                            plot_object=None, 
                            flag_widget=None, 
                            help_info_function=None):
    """
    Updates the plot_object (time series) using information from gismo_object, par and flag_widget.
    If help_info_function (updating tkText) is given text information is passed to the funktion. 
    """
    
    if help_info_function:
        help_info_function('Updating time series plot...please wait...')
    
    settings = gismo_object.settings
    selection = flag_widget.get_selection()

    
    # Clear old data from plot
    plot_object.reset_plot()
    
    # Plot all flags combined
    time_vector, values = gismo_object.get_time_series(par=par, qf_list=selection.selected_flags)
    
#     print 'time_vector', time_vector
#     print 'values', values
    prop = {'linestyle': '', 
             'marker': None}
    plot_object.set_data(x=time_vector, y=values, line_id='current_flags', **prop)
    
    
    # Plot individual flags
    for k, flag in enumerate(selection.selected_flags):
        
        time_vector, values = gismo_object.get_time_series(par=par, qf_list=flag)
        
        if all(np.isnan(values)):
#            print 'No data for flag "%s", will not plot.' % flag
            continue
        prop = settings.get_flag_prop_dict(flag)
        prop.update(selection.get_prop(flag)) # Is empty if no settings file is added while loading data
        prop.update({'linestyle':''})
        plot_object.set_data(x=time_vector, y=values, line_id=flag, **prop)
        
    if help_info_function:
        help_info_function('Done!')
        
"""
================================================================================
================================================================================
================================================================================
""" 
def update_scatter_route_map(gismo_object=None, 
                             par=None, 
                             map_object=None, 
                             flag_widget=None, 
                             time_widget=None, 
                             help_info_function=None):
    """
    Updates the plot_object (time series) using information from gismo_object, par and flag_widget.
    If help_info_function (updating tkText) is given text information is passed to the funktion. 
    """
    
    if help_info_function:
        help_info_function('Updating plot...please wait...')
    
    
    selection = flag_widget.get_selection()
    
    # Get info from time_widget
    start_time, end_time = time_widget.get_time_limits()
#    print 'start_time', start_time
#    print 'end_time', end_time
    
    # Clear old data from plot
    map_object.reset_map()
    
    # Plot all flags combined
#    if current_par == 'time':
#        qf_list = []
#    else:
#        qf_list = selection.selected_flags
        
    time_vector, values = gismo_object.get_time_series(par=par, 
                                                       qf_list=selection.selected_flags, 
                                                       start_time=start_time, 
                                                       end_time=end_time)
    
    lat = core.Boxen().current_ferrybox_object.get_column('lat')
    lon = core.Boxen().current_ferrybox_object.get_column('lon')
    # TODO: These should be given as arguments
    
    # Add additional points. 
    if core.Boxen().sample_data:
        for la, lo, val, t in zip(core.Boxen().sample_data['lat'], 
                                   core.Boxen().sample_data['lon'], 
                                   core.Boxen().sample_data['values'],
                                    core.Boxen().sample_data['time']):
#             print '='*30
#             print t, type(t)
#             print start_time, type(start_time)
#             print end_time, type(end_time)
            if t >= start_time and t <= end_time:
                lat = np.append(lat, la)
                lon = np.append(lon, lo)
                values = np.append(values, val)
    
    # Plot scatter
    marker_name = map_object.add_scatter(lat=lat, 
                                        lon=lon, 
                                        values=values, 
                                        divide=[], 
                                        index=[], 
                                        marker_size=50, 
                                        color_map='RdYlGn', 
                                        marker_type='o', 
                                        labels=None, 
                                        edge_color=None, 
                                        line_width=1, 
                                        marker_id='ferrybox', 
                                        legend_nr=1)
    
    for unit in core.Settings().unit_list:
        if unit in par.split()[-1]:
            title = unit
            break
    else:
        title = 'unknown'
    
    
    if par == 'time':
        title = None
        map_object.add_colorbar(marker_name, 
                                 title=title, 
                                 orientation=u'vertical', 
                                 position=[0.93, 0.02, 0.04, 0.3], 
                                 tick_side=u'left', 
                                 tick_size=6, 
                                 title_size=6, 
                                 nr_ticks=False,
                                 display_every=False, 
                                 time_format=True)
    else:
        map_object.add_colorbar(marker_name, 
                                 title=title, 
                                 orientation=u'vertical', 
                                 position=[0.93, 0.02, 0.04, 0.3], 
                                 tick_side=u'left', 
                                 tick_size=6, 
                                 title_size=6, 
                                 nr_ticks=False,
                                 display_every=False)
    
    # Set title
    map_object.set_title(par)
    
#    prop = {'linestyle': '', 
#             'marker': None}
#    plot_object.set_data(x=time_vector, y=values, line_id='current_flags', **prop)
    
    
#    # Plot individual flags
#    for k, flag in enumerate(selection.selected_flags):
#        
#        time_vector, values = gismo_object.get_time_series(par=current_par, qf_list=flag)
#        
#        if all(np.isnan(values)):
##            print 'No data for flag "%s", will not plot.' % flag
#            continue
#        prop = settings.get_flag_prop_dict(flag)
#        prop.update(selection.get_prop(flag)) # Is empty if no settings file is added while loading data
#        prop.update({'linestyle':''})
#        plot_object.set_data(x=time_vector, y=values, line_id=flag, **prop)
        
    if help_info_function:
        help_info_function('Done!')
        
"""
================================================================================
================================================================================
================================================================================
""" 
#===========================================================================
def update_plot_limits_from_settings(plot_object=None, 
                                     settings_object=None, 
                                     axis=None, 
                                     par=None, 
                                     call_targets_in_plot_object=False):
    """ 
    Updates limits in plot. Limits are taken from GISMOsettings object. 
    Idea is to always update limits via this method. 
    """
    
    
    if not all([settings_object, settings_object, axis, par]):
        return  
    
    min_value = settings_object['ranges'][par]['min'] 
    max_value = settings_object['ranges'][par]['max']
    
    if axis in ['x', 't']:
#        xmin = settings_object['ranges'][par]['xmin'] 
#        xmax = settings_object['ranges'][par]['xmax']
        plot_object.set_x_limits(limits=[min_value, max_value], call_targets=call_targets_in_plot_object)
        
    elif axis in ['y', 'z']:
#        ymin = settings_object['ranges'][par]['ymin'] 
#        ymax = settings_object['ranges'][par]['ymax']
        plot_object.set_y_limits(limits=[min_value, max_value], call_targets=call_targets_in_plot_object)
    
      
"""
================================================================================
================================================================================
================================================================================
""" 
def set_valid_time_in_time_axis(gismo_object=None, 
                                time_axis_widget=None, 
                                sample_object=None):
    """
    Takes information from the plot_object and sets valid tame range in the axis_widget
    """
    time_array = gismo_object.get_time_series()
    if sample_object:
        time_array = np.append(time_array, sample_object.get_time_series())
        
    time_axis_widget.set_valid_time_span_from_list(time_array)
    
    
"""
================================================================================
================================================================================
================================================================================
""" 
def update_limits_in_axis_time_widget(settings_object=None, 
                                      axis_time_widget=None, 
                                      plot_object=None, 
                                      par=None, 
                                      axis=None):
    """
    Takes information from settings_object and updates the Axiscore.SettingsTimeWidget. 
    If parameter not present in settings limits are taken from the current plot_object. 
    if no information is avalable full range is set. 
    """
    
#    if not all([settings_object, par, axis]):
#        return
    
    min_value = None 
    max_value = None
    
    if par in settings_object['ranges']:
        min_value = settings_object['ranges'][par]['min']
        max_value = settings_object['ranges'][par]['max']
#        if axis in ['x', 't']:
#            min_value = settings_object['ranges'][par]['xmin']
#            max_value = settings_object['ranges'][par]['xmax']
#        elif axis in ['y', 'z']:
#            min_value = settings_object['ranges'][par]['ymin']
#            max_value = settings_object['ranges'][par]['ymax']
    else:
        # Parameter not in settings. Values are taken from current plot_object
        if plot_object:
            if axis in ['x', 't']:
                min_value, max_value = plot_object.get_xlim(ax='first')
                
            elif axis in ['y', 'z']:
                min_value, max_value = plot_object.get_ylim(ax='first') 

            # Save limits
            save_limits_from_axis_time_widget(settings_object=settings_object, 
                                              axis_time_widget=axis_time_widget, 
                                              par=par, 
                                              axis=axis)
        
            
            
    print('min_value', min_value)
    if min_value:
        axis_time_widget.time_widget_from.set_time(datenumber=min_value)
        axis_time_widget.time_widget_to.set_time(datenumber=max_value)
    else:
        axis_time_widget.time_widget_from.set_time(first=True)
        axis_time_widget.time_widget_to.set_time(last=True)


"""
================================================================================
================================================================================
================================================================================
"""
def update_limits_in_axis_float_widget(settings_object=None, 
                                       axis_float_widget=None, 
                                       plot_object=None, 
                                       par=None, 
                                       axis=None):
    """
    Takes information from settings_object and updates the Axiscore.SettingsFloatWidget. 
    If parameter not present in settings limits are taken from the current plot_object. 
    """

    if not all([settings_object, par, axis]):
        return
    
    min_value = None 
    max_value = None
    
    if par in settings_object['ranges']:
        min_value = settings_object['ranges'][par]['min']
        max_value = settings_object['ranges'][par]['max']
#        if axis in ['x', 't']:
#            min_value = settings_object['ranges'][par]['xmin']
#            max_value = settings_object['ranges'][par]['xmax']
#        elif axis in ['y', 'z']:
#            min_value = settings_object['ranges'][par]['ymin']
#            max_value = settings_object['ranges'][par]['ymax']
    else:
        # Parameter not in settings. Values are taken from current plot_object
        if plot_object:
            if axis in ['x', 't']:
                min_value, max_value = plot_object.get_xlim(ax='first')
                
            elif axis in ['y', 'z']:
                min_value, max_value = plot_object.get_ylim(ax='first') 
            
            # Save limits
            save_limits_from_axis_float_widget(settings_object=settings_object, 
                                              axis_float_widget=axis_float_widget, 
                                              par=par, 
                                              axis=axis)
    if min_value:
        axis_float_widget.stringvar_min.set(str(min_value))
        axis_float_widget.stringvar_max.set(str(max_value))
       
"""
================================================================================
================================================================================
================================================================================
"""
def update_compare_widget(compare_widget=None, 
                          settings_object=None): 
    """
    core.Settings object is the gismo settings
    """
    
    compare_widget.set_data(time=settings_object['compare']['time'],
                             dist=settings_object['compare']['distance'],
                             depth=settings_object['compare']['depth'])
            
"""
================================================================================
================================================================================
================================================================================
"""
def save_limits_from_axis_time_widget(settings_object=None, 
                                      axis_time_widget=None, 
                                      par=None):
    """
    Takes informatioen from a Axiscore.SettingsTimeWidget object and store them in given gismo settings object. 
    """
    
    if not settings_object:
        # Cant save if no settings_object is active. 
        return
    
    if not par:
        return
    
    min_value = axis_time_widget.time_widget_from.get_time_number()
    max_value = axis_time_widget.time_widget_to.get_time_number()
    
    if par not in settings_object['ranges']:
        settings_object['ranges'][par] = {}
    
    settings_object['ranges'][par]['min'] = float(min_value)
    settings_object['ranges'][par]['max'] = float(max_value)
#    if axis in ['x', 't']:
#        settings_object['ranges'][par]['xmin'] = float(min_value)
#        settings_object['ranges'][par]['xmax'] = float(max_value)
#    elif axis in ['y', 'z']:
#        settings_object['ranges'][par]['ymin'] = float(min_value)
#        settings_object['ranges'][par]['ymax'] = float(max_value)
        

"""
================================================================================
================================================================================
================================================================================
"""
def save_limits_from_axis_float_widget(settings_object=None, 
                                       axis_float_widget=None, 
                                       par=None):
    """
    Takes informatioen from a AxisSettingsTimeWidget object and store them in given gismo settings object. 
    """
    
    if not settings_object:
        # Cant save if no settings_object is active. 
        return
    
    if not par:
        return
    
    min_value = axis_float_widget.stringvar_min.get()
    max_value = axis_float_widget.stringvar_max.get()
    
    
    if par not in settings_object['ranges']:
        settings_object['ranges'][par] = {}
        
    settings_object['ranges'][par]['min'] = float(min_value)
    settings_object['ranges'][par]['max'] = float(max_value)
    
#    if axis in ['x', 't']:
#        settings_object['ranges'][par]['xmin'] = float(min_value)
#        settings_object['ranges'][par]['xmax'] = float(max_value)
#    elif axis in ['y', 'z']:
#        settings_object['ranges'][par]['ymin'] = float(min_value)
#        settings_object['ranges'][par]['ymax'] = float(max_value)     
 
"""
================================================================================
================================================================================
================================================================================
""" 
def save_limits_from_plot_object(plot_object=None, 
                                 settings_object=None,
                                 par=None, 
                                 axis=None, 
                                 use_plot_limits=False):
    """
    Saves limits in in given settings_object from plot_object if limit not already in settings_object. 
    If use_plot_limits==True limits are overwritten bu the limits in plot_object.
    """    
    
    if not all([plot_object, settings_object, par, axis]):
        return
    
    if axis in ['x', 't']:
        min_value, max_value = plot_object.get_xlim()
    elif axis in ['y', 'z']:
        min_value, max_value = plot_object.get_ylim()
    
    if par not in settings_object['ranges']:
        settings_object['ranges'][par] = {}
        use_plot_limits = True
    
    if use_plot_limits:
        settings_object['ranges'][par]['min'] = float(min_value)
        settings_object['ranges'][par]['max'] = float(max_value)
        
#        if axis in ['x', 't']:
#            settings_object['ranges'][par]['xmin'] = float(xmin)
#            settings_object['ranges'][par]['xmax'] = float(xmax)
#        elif axis in ['y', 'z']:
#            settings_object['ranges'][par]['ymin'] = float(ymin)
#            settings_object['ranges'][par]['ymax'] = float(ymax)
    else:
        for key, value in zip(['min', 'max'], [min_value, max_value]):
            if key not in settings_object['ranges'][par]:
                settings_object['ranges'][par][key] = float(value)
            elif settings_object['ranges'][par][key] == None:
                settings_object['ranges'][par][key] = float(value)
        
        print(par)
        print(settings_object['ranges'][par])
#        if axis in ['x', 't']:
#            for key, value in zip(['xmin', 'xmax'], [xmin, xmax]):
#                if key not in settings_object['ranges'][par]:
#                    settings_object['ranges'][par][key] = float(value)
#                elif not settings_object['ranges'][par][key]:
#                    settings_object['ranges'][par][key] = float(value)
#                    
#        elif axis in ['y', 'z']:
#            for key, value in zip(['ymin', 'ymax'], [ymin, ymax]):
#                if key not in settings_object['ranges'][par]:
#                    settings_object['ranges'][par][key] = float(value)
#                elif not settings_object['ranges'][par][key]:
#                    settings_object['ranges'][par][key] = float(value)