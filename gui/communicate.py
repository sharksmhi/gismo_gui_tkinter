#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import numpy as np
import os
import shutil

import pandas as pd
import datetime

import core
import gui
from libs.sharkpylib import utils

import matplotlib.dates as dates
import libs.sharkpylib.gismo as gismo
import libs.sharkpylib.tklib.tkinter_widgets as tkw

from core.exceptions import *

from libs.sharkpylib.gismo.exceptions import *
from tkinter import messagebox

import logging 


def add_compare_to_timeseries_plot(plot_object=None,
                                   session=None,
                                   file_id=None,
                                   ref_file_id=None,
                                   par=None,
                                   help_info_function=None,
                                   user=None):

    """
    sample_object is the main GISMOfile. 
    gismo_object is the file where matching data will be extracted from 
    """

    help_info_function('Adding reference data...please wait...')

    # diffs = {}
    # diffs['hours'] = compare_widget.time
    # diffs['dist'] = compare_widget.dist
    # diffs['depth'] = compare_widget.depth
    # diffs['main_sampling_depth'] = compare_widget.sampling_depth
    # session.match_files(main_file_id, sample_file_id, **diffs)
    #
    # par = compare_widget.get_parameter()
    #
    match_data = session.get_match_data(file_id, ref_file_id, 'time', 'lat', 'lon', par)
    print('='*50)
    print('match_data')
    print(match_data)
    if not len(np.where(~np.isnan(np.array(match_data[par])))):
        help_info_function('No matching data!', bg='red')
        return

    plot_object.set_data(x=match_data['time'],
                         y=match_data[par],
                         line_id='ref_data',
                         marker=user.plot_time_series_ref.setdefault('marker', '*'),
                         markersize=user.plot_time_series_ref.setdefault('markersize', 10),
                         color=user.plot_time_series_ref.setdefault('color', 'red'),
                         linestyle='None')

    help_info_function('Reference data for parameter {} added!'.format(par), bg='green')

    return match_data


# """
# ================================================================================
# ================================================================================
# ================================================================================
# """
# def add_sample_data_to_boxen(par=None,
#                                 sample_object=None,
#                                 gismo_object=None,
#                                 compare_widget=None,
#                                 help_info_function=None):
#     """
#     UNDER CONSTRUCTON!
#     sample_object is the main GISMOfile.
#     gismo_object is the file where matching data will be extracted from
#     """
#
#     # Remove old data
#     core.Boxen().sample_data = {}
#
#     if not core.Boxen().sample_index or compare_widget.values_are_updated:
#         if help_info_function:
#             help_info_function('Adding reference data...please wait...')
#
#         if not all([sample_object, gismo_object]):
#             return
#
# #        modulus = 1
#         diffs = {}
#         if compare_widget:
# #            modulus = compare_widget.modulus
#             diffs['time'] = compare_widget.time
#             diffs['dist'] = compare_widget.dist
#             diffs['depth'] = compare_widget.depth
#
#         index = gismo.get_matching_sample_index(sample_object=sample_object,
#                                                        gismo_object=gismo_object,
# #                                                       modulus=modulus,
#                                                        diffs=diffs)
#         core.Boxen().sample_index = index
#     else:
#         index = core.Boxen().sample_index
# #    print 'index', index
#     # Get data
#     if not len(index):
#         logging.debug('No matching data found')
#         core.Boxen().sample_index = []
#         return
#     par = sample_object.parameter_mapping.get_external(par)
#     if par not in sample_object.df.columns:
#         logging.debug('No parameter named "%s" in sample data file.' % par)
#         return
#
#
#     time_list = sample_object.get_column('time')
#     lat_list = sample_object.get_column('lat')
#     lon_list = sample_object.get_column('lon')
#
#     value_list = sample_object.get_column(par)
#
#     if par == 'time':
#         value_list = sample_object.get_column(par, time_as_datenum=True)
#
#     else:
#         value_list = sample_object.get_column(par)
#
#     core.Boxen().set_sample_data(lat=lat_list[index],
#                                             lon=lon_list[index],
#                                             t=time_list[index],
#                                             values=value_list[index])
#
#     if help_info_function:
#         help_info_function('Done!')
    
"""
================================================================================
================================================================================
================================================================================
""" 
def get_flag_widget(parent=None, 
                    settings_object=None,
                    user_object=None,
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

    color_list = []
    markersize_list = []

    all_colors = utils.ColorsList()

    for f in flags:
        f = str(f)
        if f in '48BS':
            color_list.append(user_object.flag_color.setdefault(f, 'red'))
        else:
            color_list.append(user_object.flag_color.setdefault(f, 'black'))

        markersize_list.append(user_object.flag_markersize.setdefault(f, 6))
    flag_widget = tkw.FlagWidget(parent, 
                                  flags=flags, 
                                  descriptions=descriptions, 
                                  colors=all_colors,
                                  default_colors=color_list,
                                  markersize=markersize_list,
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
    active_flags = selection.selected_flags

    mark_from = plot_object.get_mark_from_value()
    mark_to = plot_object.get_mark_to_value()

    if not all([mark_from, mark_to]):
        raise GUIExceptionNoRangeSelection

    # print(mark_from, type(mark_from))

    import pandas as pd
    if plot_object.mark_range_orientation == 'vertical':
        time_from, time_to = plot_object.get_xlim()
        time_from = dates.num2date(time_from)
        time_to = dates.num2date(time_to)

        time_from = pd.Timestamp.tz_localize(pd.to_datetime(time_from), None)
        time_to = pd.Timestamp.tz_localize(pd.to_datetime(time_to), None)


        data = gismo_object.get_data('time', par)
        time_array = np.array([pd.to_datetime(item) for item in data['time']])
        # print("time_array[0]", time_array[0], type(time_array[0]))
        # print('time_from', time_from, type(time_from))
        # print('time_to', time_to, type(time_to))
        # print('mark_from', mark_from)
        # print('mark_to', mark_to)

        (time_array >= time_from)
        (time_array <= time_to)
        (data[par] >= mark_from)
        (data[par] <= mark_to)

        boolean = (time_array >= time_from) & \
                  (time_array <= time_to) & \
                  (data[par] >= mark_from) & \
                  (data[par] <= mark_to)
        times_to_flag = time_array[boolean]

        # Flag data
        gismo_object.flag_data(flag_nr, par, time=times_to_flag, flags=active_flags)
        # Flag dependent parameters
        # dependent_list = gismo_object.get_dependent_parameters(par)
        # if dependent_list:
        #     print('par', par)
        #     for sub_par in dependent_list:
        #         print('sub_par', sub_par)
        #         gismo_object.flag_data(flag_nr, sub_par, time=times_to_flag)

    else:
        time_start = dates.num2date(mark_from)
        time_end = dates.num2date(mark_to)

        time_start = pd.Timestamp.tz_localize(pd.to_datetime(time_start), None)
        time_end = pd.Timestamp.tz_localize(pd.to_datetime(time_end), None)

        # Flag data
        gismo_object.flag_data(flag_nr, par, time_start=time_start, time_end=time_end, flags=active_flags)
        # Flag dependent parameters
        # dependent_list = gismo_object.get_dependent_parameters(par)
        # if dependent_list:
        #     print('par', par)
        #     for sub_par in dependent_list:
        #         print('sub_par', sub_par)
        #         gismo_object.flag_data(flag_nr, sub_par, time_start=time_start, time_end=time_end)

def run_automatic_qc(controller, automatic_qc_widget):
    qc_routine_list = automatic_qc_widget.get_checked_item_list()
    nr_routines = len(qc_routine_list)
    if nr_routines == 0:
        gui.show_information('Run QC', 'No QC routines selected!')
        return False

    if nr_routines == 1:
        text = 'You are about to run 1 automatic quality control. ' \
               'This might take some time. ' \
               'Do you want to continue?'
    else:
        text = 'You are about tu run {} automatic quality controles. ' \
               'This might take some time. ' \
               'Do you want to continue?'.format(nr_routines)

    if not messagebox.askyesno('Run QC', text):
        return False

    controller.session.run_automatic_qc(controller.current_file_id, qc_routines=qc_routine_list)

    # controller.controller.run_progress(lambda: controller.session.run_automatic_qc(controller.current_file_id,
    #                                    qc_routines=qc_routine_list),
    #                                    'Running qc on file: {}'.format(controller.current_file_id))
    return qc_routine_list

def save_user_info_from_flag_widget(flag_widget, user_object):
    """
    Saves color and marker size to user profile (user_object)
    :param flag_widget:
    :param user_object:
    :return:
    """
    prop = flag_widget.get_selection()
    for flag, color in prop.colors.items():
        user_object.flag_color.set(flag, color)
        user_object.flag_markersize.set(flag, prop.markersize[flag])

    # for f, c, ms in zip(flag_widget.flags, flag_widget.default_colors, flag_widget.markersize):
    #     print('f, c, ms', f, c, ms)
    #     user_object.flag_color.set(f, c)
    #     user_object.flag_markersize.set(f, ms)

def save_file(controller, gismo_object, save_widget):
    """
    Saves the given gismo_object using the information in save_widget
    save_widget is a gui.SaweWidget object

    :param controller:
    :param save_widget:
    :return:
    """
    if not controller.current_file_id:
        gui.show_information('No file loaded', 'Cant save file, no file loaded.')
        return

    directory = save_widget.stringvar_directory.get().strip()
    file_name = save_widget.stringvar_file_name.get().strip()

    if not all([directory, file_name]):
        gui.show_information('Invalid directory or filename', 'Cant save plot! Invalid directory or filename.')
        return
    original_file_path = os.path.realpath(gismo_object.file_path)
    if not file_name.endswith('.txt'):
        file_name = file_name + '.txt'
    output_file_path = os.path.join(directory, file_name)
    print(output_file_path)
    print(original_file_path)
    if not os.path.samefile(output_file_path, original_file_path):
        try:
            gismo_object.save_file(file_path=output_file_path)
            gui.show_information('File saved', 'File saved to:\n{}'.format(output_file_path))
            return
        except GISMOExceptionFileExcists:
            if not messagebox.askyesno('Overwrite file!',
                                       'The given file already exists. Do you want to replace the existing file?'):
                return
    else:
        if not messagebox.askyesno('Overwrite file!', 'Do you want to replace the original file?'):
            return
    print('CONTINUE!!!')

    # Create temporary file and then overwrite by changing the name. This is so that the process don't get interrupted.
    if not os.path.exists(directory):
        os.makedirs(directory)
    temp_file_path = directory + '/temp_%s' % file_name
    gismo_object.save_file(file_path=temp_file_path, overwrite=True)
    os.remove(output_file_path)
    shutil.copy2(temp_file_path, output_file_path)
    os.remove(temp_file_path)
    gui.show_information('File saved', 'File saved to:\n{}'.format(output_file_path))


def save_plot(controller, plot_object, save_directory_widget, in_file_name='plot', **kwargs):
    """
    Saves the plot plot_widget using the information in save_directory_widget
    save_widget is a gui.SaweWidget object

    :param plot_object:
    :param save_widget:
    :return:
    """
    if not controller.current_file_id:
        gui.show_information('No file loaded', 'Cant save plot, no file loaded.')
        return

    directory = save_directory_widget.get_directory()
    in_file_name = in_file_name.replace('/', '-').replace('\\', '-')
    file_name = '{}.{}'.format(in_file_name, kwargs.get('file_format', 'png'))

    if not all([directory, file_name]):
        gui.show_information('Invalid directory or filename', 'Cant save plot! Invalid directory or filename.')
        return

    if not os.path.exists(directory):
        if not messagebox.askyesno('Create directory', 'The given directory does not exist. Do you want to create it?'):
            return
        os.makedirs(directory)

    output_file_path = os.path.realpath('/'.join([directory, file_name]))
    if not os.path.exists(directory):
        os.makedirs(directory)

    plot_object.save_fig(output_file_path)


def save_html_plot(controller, save_widget_html, flag_widget=None, save_directory_widget=None):

    def get_par_list_by_file_id(parameter_list):
        """
        """
        return_dict = dict(main=set(['time']),
                           ref=set(['time']))
        for item in parameter_list:
            par, file_id = item.split('(')
            if file_id == 'main)':
                return_dict['main'].add(par.strip())
            elif file_id == 'ref)':
                return_dict['ref'].add(par.strip())

        return_dict['main'] = sorted(return_dict['main'])
        return_dict['ref'] = sorted(return_dict['ref'])
        return return_dict

    import libs.sharkpylib.plot.html_plot as html_plot

    selection = save_widget_html.get_selection()

    # Check selection
    export_combined_plots = selection.get('combined_plot')
    export_individual_plots = selection.get('individual_plots')
    export_individual_maps = selection.get('individual_maps')
    parameter_list = selection.get('parameters')
    directory = save_directory_widget.get_directory()

    # Check selection
    if not any([export_combined_plots, export_individual_plots, export_individual_maps, parameter_list]):
        gui.show_information('No selection', 'You need to select what type of plots/maps to export')

    # Check directory
    if not directory:
        gui.show_information('Missing directory', 'Could not save HTML maps and/or plots. No directory selected.')
        return
    if not os.path.exists(directory):
        create_dirs = messagebox.askyesno('Missing directory', 'Directory does not exist. Would you like to create a new directory?')
        if create_dirs:
            os.makedirs(directory)
        else:
            return

    # Create subdirectory
    date_string = datetime.datetime.now().strftime('%Y%m%d%H%M')
    subdir = 'html_exports_{}'.format(date_string)
    export_dir = os.path.join(directory, subdir)
    if not os.path.exists(export_dir):
        os.mkdir(export_dir)

    parameter_dict = get_par_list_by_file_id(parameter_list)

    # Check nr of parameters and warn if too many
    nr_par = len(parameter_dict['main']+parameter_dict['ref'])
    max_nr_par = controller.user.process.setdefault('warn_export_nr_parameters', 10)
    if nr_par > max_nr_par:
        ok_to_continue = messagebox.askyesno('Export plots/maps',
                                                'You have chosen to export {} parameters. '
                                                'This might take some time and MAY cause the program to crash. '
                                                'Do you wish to continue anyway? ')
        if not ok_to_continue:
            controller.update_help_information('Export aborted by user.')
            return

    main_data = {}
    ref_data = {}
    if controller.current_file_id and parameter_dict.get('main'):
        main_data = controller.session.get_data(controller.current_file_id, *parameter_dict.get('main'))
    if controller.current_ref_file_id and parameter_dict.get('ref'):
        ref_data = controller.session.get_data(controller.current_ref_file_id, *parameter_dict.get('ref'))

    if export_combined_plots:
        combined_plot_object = html_plot.PlotlyPlot()
        # Add Main data
        if main_data:
            for par in main_data:
                if par == 'time':
                    continue
                combined_plot_object.add_scatter_data(main_data['time'],
                                                      main_data[par],
                                                      name='{} (main)'.format(par),
                                                      mode='markers')
        if ref_data:
            for par in ref_data:
                if par == 'time':
                    continue
                combined_plot_object.add_scatter_data(ref_data['time'],
                                                      ref_data[par],
                                                      name='{} (ref)'.format(par),
                                                      mode='markers')
        combined_plot_object.plot_to_file(os.path.join(export_dir, 'plot_combined.html'))

    if export_individual_plots and flag_widget:
        flag_selection = flag_widget.get_selection()
        selected_flags = flag_selection.selected_flags
        selected_descriptions = flag_selection.selected_descriptions
        if main_data:
            for par in main_data:
                if par == 'time':
                    continue
                individual_plot_object = html_plot.PlotlyPlot(title='{} (main)'.format(par), yaxis_title='')
                for qf, des in zip(selected_flags, selected_descriptions):
                    data = controller.session.get_data(controller.current_file_id, 'time', par, mask_options={'include_flags': [qf]})
                    individual_plot_object.add_scatter_data(data['time'], data[par],
                                                            name='{} ({})'.format(qf, des),
                                                            mode='markers')
                individual_plot_object.plot_to_file(os.path.join(export_dir, 'plot_{}.html'.format(par.replace('/', '_'))))
        if ref_data:
            for par in ref_data:
                if par == 'time':
                    continue
                individual_plot_object = html_plot.PlotlyPlot(title='{} (ref)'.format(par), yaxis_title='')
                for qf, des in zip(selected_flags, selected_descriptions):
                    data = controller.session.get_data(controller.current_ref_file_id, 'time', par, mask_options={'include_flags': [qf]})
                    individual_plot_object.add_scatter_data(data['time'], data[par],
                                                            name='{} ({})'.format(qf, des),
                                                            mode='markers')
                individual_plot_object.plot_to_file(os.path.join(export_dir, 'plot_{}.html'.format(par.replace('/', '_'))))

def match_data(controller, compare_widget):
    """
    Match data from the active files. Only calculates if compare widget is updated.
    :return:
    """
    if not all([controller.current_file_id, controller.current_ref_file_id]):
        if not controller.current_file_id:
            gui.show_information('No data loaded', 'No main file loaded!')
        elif not controller.current_ref_file_id:
            gui.show_information('No data loaded', 'No reference file loaded!')
        raise GUIExceptionBreak
    elif controller.current_file_id == controller.current_ref_file_id:
        gui.show_information('Cant compare the same data', 'Cant compare with yourself!')
        raise GUIExceptionBreak

    diffs = dict()
    diffs['hours'] = compare_widget.time
    diffs['dist'] = compare_widget.dist
    diffs['depth'] = compare_widget.depth

    # TODO: Match data every time. CHANGE THIS
    controller.session.match_files(controller.current_file_id, controller.current_ref_file_id, **diffs)
    return True

def get_merge_data(controller, compare_widget, flag_widget, load_match_data=True):
    """
    Returns matching data for loaded information
    :param controller:
    :return:
    """
    # Try matching data
    if load_match_data:
        if not match_data(controller, compare_widget):
            return

    file_id = controller.current_file_id
    ref_file_id = controller.current_ref_file_id
    parameter = controller.current_parameter
    gismo_object = controller.current_gismo_object

    match_object = controller.session.get_match_object(file_id, ref_file_id)
    merge_df = controller.session.get_merge_data(file_id, ref_file_id)

    compare_parameter = compare_widget.get_parameter()

    # Find parameter names in merge df
    main_par_file_id = '{}_{}'.format(parameter, file_id)
    compare_par_file_id = '{}_{}'.format(compare_parameter, ref_file_id)
    depth_compare_file_id = '{}_{}'.format('depth', ref_file_id)

    main_par = match_object.get_merge_parameter(main_par_file_id)
    comp_par = match_object.get_merge_parameter(compare_par_file_id)
    depth_par = match_object.get_merge_parameter(depth_compare_file_id)

    # Get list of active visit_depth_id
    visit_depth_id_par = '{}_{}'.format('visit_depth_id', file_id)
    visit_depth_id_list = merge_df[visit_depth_id_par]

    # Handle flags
    selection = flag_widget.get_selection()

    # Build data
    all_values = []
    all_times = []

    data = {}
    data['flags'] = {}
    for flag in selection.selected_flags:
        masked_data = gismo_object.get_data('visit_depth_id', 'time', parameter,
                                     visit_depth_id_list=visit_depth_id_list,
                                     mask_options=dict(include_flags=[flag]))

        boolean = ~np.isnan(np.array(masked_data[parameter]))
        visit_depth_id_flag = masked_data['visit_depth_id'][boolean]
        all_times.extend(list(masked_data['time']))

        boolean = merge_df[visit_depth_id_par].isin(visit_depth_id_flag)

        data['flags'][flag] = {}
        data['flags'][flag]['x'] = [float(item) if item else np.nan for item in merge_df.loc[boolean, main_par]]
        data['flags'][flag]['y'] = [float(item) if item else np.nan for item in merge_df.loc[boolean, comp_par]]
        data['flags'][flag]['depth'] = [float(item) if item else np.nan for item in merge_df.loc[boolean, depth_par]]

        prop = gismo_object.settings.get_flag_prop_dict(flag)
        prop.update(selection.get_prop(flag))  # Is empty if no settings file is added while loading data
        prop.update({'linestyle': '',
                     'marker': '.'})

        data['flags'][flag]['prop'] = prop

        all_values.extend(data['flags'][flag]['x'])
        all_values.extend(data['flags'][flag]['y'])

        # print('LEN', len(all_values))

    data['min_value'] = np.nanmin(all_values)
    data['max_value'] = np.nanmax(all_values) * 1.05

    if data['min_value'] > 0:
        data['min_value'] = data['min_value'] * 0.95

    # Set title and labels
    data['time_from_str'] = pd.to_datetime(str(min(all_times))).strftime('%Y%m%d')
    data['time_to_str'] = pd.to_datetime(str(max(all_times))).strftime('%Y%m%d')

    data['main_par'] = main_par
    data['compare_par'] = comp_par

    data['main_par_file_id'] = main_par_file_id
    data['compare_par_file_id'] = compare_par_file_id

    return data

"""
================================================================================
================================================================================
================================================================================
""" 
def flag_data_profile(flag_widget=None,
                      gismo_object=None,
                      plot_object=None,
                      par=None):
    """
    Flag data in the given gismo_object. 
    Takes limits from plot_object and 
    flag information from tkw.FlagWidget.
    """
    print('PROFILE!!!!!!!!!')
    selection = flag_widget.get_selection()
    flag_nr = selection.flag
    active_flags = selection.selected_flags

    # if 'no flag' in active_flags:
    #     active_flags.pop('no flag')
    #     active_flags.append('')

    mark_from = plot_object.get_mark_from_value()
    mark_to = plot_object.get_mark_to_value()

    if not all([mark_from, mark_to]):
        raise GUIExceptionNoRangeSelection

    print('ORIENTATION', plot_object.mark_range_orientation)
    if plot_object.mark_range_orientation == 'horizontal':
        value_from, value_to = plot_object.get_xlim()
        par_from = float(value_from)
        par_to = float(value_to)

        data = gismo_object.get_data('depth', par)
        par_array = data[par]

        boolean = (par_array >= par_from) & \
                  (par_array <= par_to) & \
                  (data['depth'] >= mark_from) & \
                  (data['depth'] <= mark_to)
        depth_to_flag = -data['depth'][boolean]

        # Flag data
        gismo_object.flag_data(flag_nr, par, depth=depth_to_flag, flags=active_flags)

    else:
        depth_max = -float(mark_from)
        depth_min = -float(mark_to)

        print('depth_min', depth_min)
        print('depth_max', depth_max)
        # Flag data
        gismo_object.flag_data(flag_nr, par, depth_min=depth_min, depth_max=depth_max, flags=active_flags)

"""
================================================================================
================================================================================
================================================================================
""" 

#===========================================================================
def update_range_selection_widget(plot_object=None, 
                                  range_selection_widget=None,
                                  time_axis=False):
    """
    Updates entries in range_selection_widget. 
    This is to get live update from the plot when "mark range" is active.
    line_id='current_flags' indicates that alla flags that are ploted are taken into consideration. 
    """
    # TODO: Not sure "time_axis" is used here!
    logging.debug('IN: update_range_selection_widget')
    min_value = None
    min_value = None
    
    min_value = plot_object.get_mark_from_value(ax='first')
    max_value = plot_object.get_mark_to_value(ax='first')

    try:
        if min_value > max_value:
            min_value = None
            max_value = None
    except TypeError:
        return

    if not time_axis:
        try:
            min_value = round(min_value, 2)
        except:
            pass
        try:
            max_value = round(max_value, 2)
        except:
            pass

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

    if not time_axis:
        if plot_object.mark_range_orientation == 'vertical':
            plot_object.set_bottom_range(min_value)
            plot_object.set_top_range(max_value)
            # plot_object.mark_range_range(mark_bottom=min_value,
            #                              mark_top=max_value,
            #                              mark_left=None,
            #                              mark_right=None)
        else:
            plot_object.set_left_range(min_value)
            plot_object.set_right_range(max_value)
            # plot_object.mark_range_range(mark_bottom=None,
            #                              mark_top=None,
            #                              mark_left=min_value,
            #                              mark_right=max_value)
        
        
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
    """
    To be updated!

    :param profile:
    :param par:
    :param plot_object:
    :param flag_widget:
    :param help_info_function:
    :return:
    """
    
    
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
                            help_info_function=None,
                            call_targets=True):
    """
    Updates the plot_object (time series) using information from gismo_object, par and flag_widget.
    If help_info_function (updating tkText) is given text information is passed to the function.

    :param gismo_object:
    :param par:
    :param plot_object:
    :param flag_widget:
    :param help_info_function:
    :return:
    """

    
    if help_info_function:
        help_info_function('Updating time series plot...please wait...')
    
    settings = gismo_object.settings
    selection = flag_widget.get_selection()

    # Clear old data from plot
    plot_object.reset_plot()

    # Set labels
    plot_object.set_x_label('Date/Time')
    plot_object.set_y_label(par)

    # Check if data is available
    check_data = gismo_object.get_data(par)
    print(np.where(~np.isnan(check_data[par])))
    print('no', len(np.where(~np.isnan(check_data[par]))[0]))
    print('yes', len(np.where(np.isnan(check_data[par]))[0]))

    
    # Plot all flags combined. This is used for range selection.
    data = gismo_object.get_data('time', par, mask_options={'include_flags': selection.selected_flags})

    prop = {'linestyle': '', 
             'marker': None}

    print('=== par {} ==='.format(par))
    print(data['time'][0])
    print(data[par][0])
    print()
    plot_object.set_data(x=data['time'], y=data[par], line_id='current_flags', call_targets=call_targets, **prop)

    # if par in ['time', 'lat', 'lon']:
    #
    #     plot_object.set_data(x=data['time'], y=data[par], line_id='current_flags', **prop)
    #     if help_info_function:
    #         help_info_function('Done!')
    #     return

    # Plot individual flags
    for k, flag in enumerate(selection.selected_flags):

        data = gismo_object.get_data('time', par, mask_options={'include_flags': [flag]})


        if all(np.isnan(data[par])):
#            print 'No data for flag "%s", will not plot.' % flag
            continue
        prop = settings.get_flag_prop_dict(flag)
        prop.update(selection.get_prop(flag))  # Is empty if no settings file is added while loading data
        prop.update({'linestyle': '',
                     'marker': '.'})

        plot_object.set_data(x=data['time'], y=data[par], line_id=flag, call_targets=call_targets, **prop)

    try:
        plot_object.set_title(gismo_object.get_station_name())
    except GISMOExceptionMethodNotImplemented:
        pass

    if help_info_function:
        help_info_function('Done!')


"""
================================================================================
================================================================================
================================================================================
"""
def update_profile_plot_background(gismo_objects=[],
                                   par=None,
                                   plot_object=None,
                                   flag_widget=None,
                                   help_info_function=None,
                                   call_targets=False,
                                   clear_plot=True):
    """
    Updates the plot_object (profile) using information from gismo_object, par and flag_widget.
    If help_info_function (updating tkText) is given text information is passed to the function.

    :param gismo_object:
    :param par:
    :param plot_object:
    :param flag_widget:
    :param help_info_function:
    :return:
    """

    if help_info_function:
        help_info_function('Updating profile plot with background data...please wait...')

    # Clear old data from plot
    if clear_plot:
        plot_object.reset_plot()

    for gismo_object in gismo_objects:
        settings = gismo_object.settings
        selection = flag_widget.get_selection()

        # Set labels
        plot_object.set_x_label(par)
        plot_object.set_y_label('Depth')

        # Plot all flags combined. This is used for range selection.
        data = gismo_object.get_data('depth', par, mask_options={'include_flags': selection.selected_flags})

        prop = {'linestyle': '',
                'marker': None}

        # Plot individual flags
        for k, flag in enumerate(selection.selected_flags):

            data = gismo_object.get_data('depth', par, mask_options={'include_flags': [flag]})

            if all(np.isnan(data[par])):
                #            print 'No data for flag "%s", will not plot.' % flag
                continue
            prop = settings.get_flag_prop_dict(flag)
            prop.update(selection.get_prop(flag))  # Is empty if no settings file is added while loading data
            prop.update({'linestyle': '',
                         'marker': '.',
                         'alpha': 0.2})

            marker_id = '{}_{}'.format(gismo_object.file_id, flag)
            plot_object.delete_data(marker_id)
            plot_object.set_data(x=data[par], y=-data['depth'], line_id=marker_id, call_targets=call_targets, **prop)


def update_profile_plot(gismo_object=None,
                        par=None,
                        plot_object=None,
                        flag_widget=None,
                        help_info_function=None,
                        call_targets=True,
                        clear_plot=True):
    """
    Updates the plot_object (profile) using information from gismo_object, par and flag_widget.
    If help_info_function (updating tkText) is given text information is passed to the function.

    :param gismo_object:
    :param par:
    :param plot_object:
    :param flag_widget:
    :param help_info_function:
    :return:
    """

    if help_info_function:
        help_info_function('Updating profile plot...please wait...')

    settings = gismo_object.settings
    selection = flag_widget.get_selection()

    # Clear old data from plot
    if clear_plot:
        plot_object.reset_plot()

    # Set labels
    plot_object.set_x_label(par)
    plot_object.set_y_label('Depth')

    # Check if data is available
    # check_data = gismo_object.get_data(par)
    # print(np.where(~np.isnan(check_data[par])))
    # print('no', len(np.where(~np.isnan(check_data[par]))[0]))
    # print('yes', len(np.where(np.isnan(check_data[par]))[0]))

    # Plot all flags combined. This is used for range selection.
    data = gismo_object.get_data('depth', par, mask_options={'include_flags': selection.selected_flags})

    prop = {'linestyle': '',
            'marker': None}

    # print('=== par {} ==='.format(par))
    # print(data['time'][0])
    # print(data[par][0])
    # print()
    plot_object.delete_data('current_flags')
    plot_object.set_data(x=data[par], y=-data['depth'], line_id='current_flags', call_targets=call_targets, **prop)

    # if par in ['time', 'lat', 'lon']:
    #
    #     plot_object.set_data(x=data['time'], y=data[par], line_id='current_flags', **prop)
    #     if help_info_function:
    #         help_info_function('Done!')
    #     return

    # Plot individual flags
    for k, flag in enumerate(selection.selected_flags):

        data = gismo_object.get_data('depth', par, mask_options={'include_flags': [flag]})

        if all(np.isnan(data[par])):
            #            print 'No data for flag "%s", will not plot.' % flag
            continue
        prop = settings.get_flag_prop_dict(flag)
        prop.update(selection.get_prop(flag))  # Is empty if no settings file is added while loading data
        prop.update({'linestyle': '',
                     'marker': '.'})

        plot_object.delete_data(flag)
        plot_object.set_data(x=data[par], y=-data['depth'], line_id=flag, call_targets=call_targets, **prop)

    # print('STATION NAME:', gismo_object.get_station_name())
    try:
        plot_object.set_title(gismo_object.get_station_name())
    except GISMOExceptionMethodNotImplemented:
        pass

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
def sync_limits_in_plot_user_and_axis(plot_object=None,
                                      user_object=None,
                                      axis_widget=None,
                                      par=None,
                                      axis=None,
                                      call_targets=True,
                                      source=None,
                                      **kwargs):
    """
    Syncs plot, user and axis widgets. Takes information in source.
    Only on axis

    :param plot_object:
    :param user_object:
    :param axis_widget:
    :param par:
    :param call_targets:
    :param source: (plot, user och axis)
    :param kwargs:
    :return:
    """

    plot_min = None
    plot_max = None

    # If no info in user info is taken from plot. So we start by finding limits in plot
    if axis in ['x', 't']:
        plot_min, plot_max = plot_object.get_xlim()

    elif axis in ['y', 'z']:
        plot_min, plot_max = plot_object.get_ylim()

    if plot_min == None or plot_max == None:
        raise GUIExceptionBreak

    # Get limits from source
    if source in ['plot', 'plot_widget', 'plot_object']:
        min_value = plot_min
        max_value = plot_max
    elif source in ['user', 'user_object']:
        min_value = user_object.range.setdefault(par, 'min', plot_min)
        max_value = user_object.range.setdefault(par, 'max', plot_max)
    elif source in ['axis_widget', 'axis']:
        min_value, max_value = axis_widget.get_limits()

    if par != 'time':
        min_value = float(min_value)
        max_value = float(max_value)
    # print('=' * 60)
    # print('=' * 60)
    # print('SYNC')
    # print('-'*60)
    # print(source, axis, par)
    # print(min_value, type(min_value))
    # print(max_value, type(max_value))
    # print('=' * 60)
    # Set limits in plot
    if axis in ['x', 't']:
        plot_object.set_x_limits(limits=[min_value, max_value], call_targets=call_targets)

    elif axis in ['y', 'z']:
        plot_object.set_y_limits(limits=[min_value, max_value], call_targets=call_targets)

    # Set limits in user
    if par != 'time':
        user_object.range.set(par, 'min', min_value)
        user_object.range.set(par, 'max', max_value)

    # Set limits in axis widget
    axis_widget.set_limits(min_value, max_value)

#===========================================================================
def update_plot_limits_from_user(plot_object=None,
                                 user_object=None,
                                 axis=None,
                                 par=None,
                                 call_targets=False):
    """ 
    Updates limits in plot. Limits are taken from user_object.
    If limits not in user_object min and xas from plot_object is set.
    """

    if not all([user_object, axis, par]):
        return

    if axis in ['x', 't']:
        plot_min, plot_max = plot_object.get_xlim()
        min_value = user_object.range.setdefault(par, 'min', plot_min)
        max_value = user_object.range.setdefault(par, 'max', plot_max)
        plot_object.set_x_limits(limits=[min_value, max_value], call_targets=call_targets)
        
    elif axis in ['y', 'z']:
        plot_min, plot_max = plot_object.get_ylim()
        min_value = user_object.range.setdefault(par, 'min', plot_min)
        max_value = user_object.range.setdefault(par, 'max', plot_max)
        plot_object.set_y_limits(limits=[min_value, max_value], call_targets=call_targets)


def update_plot_limits_from_axis_widgets(plot_object=None,
                                         user_object=None,
                                         axis=None,
                                         par=None,
                                         call_targets=False):
    """
    Updates limits in plot. Limits are taken from the given axis_widgets.
    Idea is to always update limits via this method.
    """

    if not all([user_object, axis, par]):
        return

    if axis in ['x', 't']:
        plot_min, plot_max = plot_object.get_xlim()
        min_value = user_object.range.setdefault(par, 'min', plot_min)
        max_value = user_object.range.setdefault(par, 'max', plot_max)
        plot_object.set_x_limits(limits=[min_value, max_value], call_targets=call_targets)

    elif axis in ['y', 'z']:
        plot_min, plot_max = plot_object.get_ylim()
        min_value = user_object.range.setdefault(par, 'min', plot_min)
        max_value = user_object.range.setdefault(par, 'max', plot_max)
        plot_object.set_y_limits(limits=[min_value, max_value], call_targets=call_targets)

def set_valid_time_in_time_axis(gismo_object=None,
                                time_axis_widget=None, 
                                match_object=None):
    """
    Takes information from the plot_object and sets valid time range in the axis_widget
    """
    data = gismo_object.get_data('time')
    time_array = data['time']
    if match_object:
        match_data = gismo_object.get_data('time')
        match_time_array = match_data['time']
        time_array = np.append(time_array, match_time_array)
        
    time_axis_widget.set_valid_time_span_from_list(time_array)
    
    
"""
================================================================================
================================================================================
================================================================================
""" 
def old_update_limits_in_axis_time_widget(axis_time_widget=None,
                                      plot_object=None, 
                                      par=None, 
                                      axis=None):
    """
    Takes information from plot_object and updates the core.SettingsTimeWidget.
    if no information is available full range is set.
    """
    
#    if not all([settings_object, par, axis]):
#        return
    
    min_value = None 
    max_value = None

    if plot_object:
        if axis in ['x', 't']:
            min_value, max_value = plot_object.get_xlim(ax='first')

        elif axis in ['y', 'z']:
            min_value, max_value = plot_object.get_ylim(ax='first')

        # Save limits
        # print()
        # save_limits_from_axis_time_widget(user_object=user_object,
        #                                   axis_time_widget=axis_time_widget,
        #                                   par=par)

    if min_value:
        axis_time_widget.time_widget_from.set_time(datenumber=min_value)
        axis_time_widget.time_widget_to.set_time(datenumber=max_value)
    else:
        axis_time_widget.time_widget_from.set_time(first=True)
        axis_time_widget.time_widget_to.set_time(last=True)

    # user_object.range.setdefault(par, 'min', float(min_value))
    # user_object.range.setdefault(par, 'max', float(max_value))


def update_limits_in_axis_time_widget(axis_time_widget=None,
                                      plot_object=None,
                                      axis=None):
    """
    Takes information from plot_object and updates the core.SettingsTimeWidget.
    """

    if not all([plot_object, axis_time_widget, axis]):
        return

    min_value = None
    max_value = None

    if axis in ['x', 't']:
        min_value, max_value = plot_object.get_xlim(ax='first')

    elif axis in ['y', 'z']:
        min_value, max_value = plot_object.get_ylim(ax='first')


    if min_value:
        axis_time_widget.time_widget_from.set_time(datenumber=min_value)
        axis_time_widget.time_widget_to.set_time(datenumber=max_value)




def old_update_limits_in_axis_float_widget(user_object=None,
                                       axis_float_widget=None,
                                       plot_object=None, 
                                       par=None, 
                                       axis=None):
    """
    Takes information from settings_object and updates the Axis.SettingsFloatWidget.
    If parameter not present in settings limits are taken from the current plot_object. 
    """

    if not all([user_object, par, axis]):
        return
    
    min_value = None 
    max_value = None

    if plot_object:
        if axis in ['x', 't']:
            min_value, max_value = plot_object.get_xlim(ax='first')

        elif axis in ['y', 'z']:
            min_value, max_value = plot_object.get_ylim(ax='first')

        # Save limits
        # save_limits_from_axis_float_widget(user_object=user_object,
        #                                    axis_float_widget=axis_float_widget,
        #                                    par=par,
        #                                    axis=axis)
    if min_value:
        # min_value = user_object.range.setdefault(par, 'min', float(min_value))
        # max_value = user_object.range.setdefault(par, 'max', float(max_value))

        axis_float_widget.set_min_value(str(min_value))
        axis_float_widget.set_max_value(str(max_value))


def update_limits_in_axis_float_widget(axis_float_widget=None,
                                       plot_object=None,
                                       axis=None):
    """
    Takes information from plot_object and updates the Axis.SettingsFloatWidget.
    """

    if not all([plot_object, plot_object, axis]):
        return

    min_value = None
    max_value = None

    if axis in ['x', 't']:
        min_value, max_value = plot_object.get_xlim(ax='first')

    elif axis in ['y', 'z']:
        min_value, max_value = plot_object.get_ylim(ax='first')

    if min_value:
        axis_float_widget.set_min_value(str(min_value))
        axis_float_widget.set_max_value(str(max_value))

            
"""
================================================================================
================================================================================
================================================================================
"""
def save_limits_from_axis_time_widget(user_object=None,
                                      axis_time_widget=None, 
                                      par=None):
    """
    Takes informatioen from a Axiscore.SettingsTimeWidget object and store them in given gismo settings object.
    Not commonly used. Risk of missing data.
    """
    
    if not user_object:
        # Cant save if no settings_object is active. 
        return
    
    if not par:
        return
    
    min_value = axis_time_widget.time_widget_from.get_time_number()
    max_value = axis_time_widget.time_widget_to.get_time_number()

    user_object.range.set(par, 'min', float(min_value))
    user_object.range.set(par, 'max', float(max_value))

    # if par not in settings_object['ranges']:
    #     settings_object['ranges'][par] = {}
    #
    # settings_object['ranges'][par]['min'] = float(min_value)
    # settings_object['ranges'][par]['max'] = float(max_value)
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
def save_limits_from_axis_float_widget(user_object=None,
                                       axis_float_widget=None, 
                                       par=None):
    """
    Takes informatioen from a AxisSettingsTimeWidget object and store them in given gismo settings object. 
    """
    
    if not user_object:
        # Cant save if no settings_object is active. 
        return
    
    if not par:
        return
    
    min_value = axis_float_widget.stringvar_min.get()
    max_value = axis_float_widget.stringvar_max.get()

    print('type:', type(min_value), min_value)
    user_object.range.set(par, 'min', float(min_value))
    user_object.range.set(par, 'max', float(max_value))
    
    # if par not in settings_object['ranges']:
    #     settings_object['ranges'][par] = {}
    #
    # settings_object['ranges'][par]['min'] = float(min_value)
    # settings_object['ranges'][par]['max'] = float(max_value)
    
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
# def save_limits_from_plot_object(plot_object=None,
#                                  user_object=None,
#                                  par=None,
#                                  axis=None,
#                                  use_plot_limits=False):
#     """
#     Saves limits in in given settings_object from plot_object if limit not already in settings_object.
#     If use_plot_limits==True limits are overwritten by the limits in plot_object.
#     """
#
#     if not all([plot_object, user_object, par, axis]):
#         return
#
#     if axis in ['x', 't']:
#         min_value, max_value = plot_object.get_xlim()
#     elif axis in ['y', 'z']:
#         min_value, max_value = plot_object.get_ylim()
#
#     user_object.range.set(par, 'min', float(min_value))
#     user_object.range.set(par, 'max', float(max_value))


def plot_map_background_data(map_widget=None, session=None, user=None, current_file_id=None, **kwargs):
    """
    Plots "background" data to plot object. Background data is data not associated with current_file_id.

    :param session:
    :param current_file_id:
    :return:
    """
    ferrybox_track_every = kwargs.get('ferrybox_track_every', 10)
    ferrybox_track_color = user.map_prop.setdefault('ferrybox_track_color_background', 'gray')

    fixed_platforms_color = user.map_prop.setdefault('fixed_platform_color_background', 'gray')
    fixed_platforms_markersize = user.map_prop.setdefault('fixed_platform_markersize_background', 5)

    ctd_shark_color = user.map_prop.setdefault('ctd_profile_color_background', 'gray')
    ctd_shark_markersize = user.map_prop.setdefault('ctd_profile_markersize_background', 5)

    physicalchemical_color = user.map_prop.setdefault('physicalchemical_color_background', 'gray')
    physicalchemical_markersize = user.map_prop.setdefault('physicalchemical_markersize_background', 5)

    map_widget.delete_all_markers()
    map_widget.delete_all_map_items()
    for sampling_type in session.get_sampling_types():
        for file_id in session.get_file_id_list(sampling_type):
            if not kwargs.get('exclude_current_file') and file_id == current_file_id:
                continue
            # print('SAMPLING TYPE:', sampling_type, file_id)
            if 'ferrybox' in sampling_type.lower():
                zorder = 10
                data = session.get_data(file_id, 'lat', 'lon')
                map_widget.add_line(data['lat'][::ferrybox_track_every],
                                    data['lon'][::ferrybox_track_every],
                                    marker_id=file_id,
                                    color=ferrybox_track_color,
                                    zorder=zorder,
                                    marker='.',
                                    linestyle='')

            elif 'physicalchemical' in sampling_type.lower():
                zorder = 11
                data = session.get_data(file_id, 'lat', 'lon')
                # Get unique positions
                lat_lon = sorted(set(zip(data['lat'], data['lon'])))
                lat_list, lon_list = zip(*lat_lon)
                map_widget.add_markers(list(lat_list), list(lon_list), marker_id=file_id, linestyle='None', marker='D',
                                       color=physicalchemical_color, markersize=physicalchemical_markersize, zorder=zorder)

            elif 'fixed platform' in sampling_type.lower():
                zorder = 12
                data = session.get_data(file_id, 'lat', 'lon')
                lat = np.nanmean(data['lat'])
                lon = np.nanmean(data['lon'])
                # print('lat', lat)
                # print('lon', lon)
                map_widget.add_markers(lat, lon, marker_id=file_id, linestyle='None', marker='s',
                                       color=fixed_platforms_color, markersize=fixed_platforms_markersize, zorder=zorder)

            elif 'ctd' in sampling_type.lower():
                zorder = 13
                data = session.get_data(file_id, 'lat', 'lon')
                lat = np.nanmean(data['lat'])
                lon = np.nanmean(data['lon'])
                # print('lat', lat)
                # print('lon', lon)
                map_widget.add_markers(lat, lon, marker_id=file_id, linestyle='None', marker='d',
                                       color=ctd_shark_color, markersize=ctd_shark_markersize, zorder=zorder)

def get_file_id(string):
    """
    Returns file_id from a information string like Ferrybox CMEMS: <file_id>
    :param string:
    :return:
    """
    return string.split(':')[-1].strip()