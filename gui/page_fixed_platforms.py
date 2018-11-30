#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2016-2017 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import shutil
import datetime
import numpy as np
import re
import sys

import tkinter as tk 

from tkinter import ttk
from tkinter import messagebox

import pandas as pd
import matplotlib
import matplotlib.colors as mcolors

import gui
import core

import libs.sharkpylib.gismo as gismo
import libs.sharkpylib.plot.plot_selector as plot_selector
import libs.sharkpylib.plot.contour_plot as contour_plot
import libs.sharkpylib.tklib.tkinter_widgets as tkw
import libs.sharkpylib.tklib.tkmap as tkmap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from libs.sharkpylib.gismo.exceptions import *

import logging


"""
================================================================================
================================================================================
================================================================================
"""
class PageFixedPlatforms(tk.Frame):
    """
    """
    def __init__(self, parent, controller, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        # parent is the frame "container" in App. contoller is the App class
        self.parent = parent
        self.controller = controller
        self.user_manager = controller.user_manager
        self.user = self.user_manager.user
        self.session = controller.session
        self.settings = controller.settings

        self.colormaps = core.Colormaps()

        self.gismo_sampling_type_settings = None

        self.current_ref_file_id = None
        self.current_file_id = None

        self.toplevel_map_widget_1 = None
        self.toplevel_map_widget_2 = None

        self.info_popup = gui.InformationPopup(self.controller)

    #===========================================================================
    def startup(self):
        self._set_frame()
        # self.update_page()
        
    #===========================================================================
    def update_page(self):
        self.user = self.user_manager.user
        self.info_popup = gui.InformationPopup(self.controller)

        loaded_file_list = self.controller.get_loaded_files_list()
        add_file_list = [item for item in loaded_file_list if 'Fixed platform' in item]
        # add_file_list = [item for item in loaded_file_list if 'PhysicalChemical' not in item]

        self.select_data_widget.update_items(add_file_list)
        self.select_ref_data_widget.update_items(self.controller.get_loaded_files_list())

    #===========================================================================
    def _set_frame(self):
        self._set_labelframes()
        self._set_frame_plot()
        self._set_frame_options()
        
    #===========================================================================
    def _set_labelframes(self):
        
        opt = {'padx': 5, 
               'pady': 5, 
               'sticky': 'nsew'}
        
        #-----------------------------------------------------------------------
        # Creating frames
        self.labelframe_plot = ttk.Labelframe(self, text=u'Plot')
        self.labelframe_plot.grid(row=0, column=0, **opt)
        
        self.labelframe_options = ttk.Labelframe(self, text=u'Options')
        self.labelframe_options.grid(row=0, column=1, **opt)
                                       
        tkw.grid_configure(self, nr_columns=2, c0=7, c1=1)
        
        
    
    #===========================================================================
    def _set_frame_plot(self):
        """
        """
        frame = self.labelframe_plot
        self.notebook_plot = tkw.NotebookWidget(frame, ['Time plot', 'Contour plot'])

        tkw.grid_configure(frame)

        self._set_notebook_time_plot()
        self._set_notebook_contour_plot()

    def _set_notebook_contour_plot(self):
        frame = self.notebook_plot.frame_contour_plot

        self.plot_object_contour = contour_plot.PlotContour()

        self.plot_widget_contour = tkw.PlotFrame(frame,
                                                 self.plot_object_contour,
                                                 pack=False,
                                                 include_toolbar=False)


    def _set_notebook_time_plot(self):
        frame = self.notebook_plot.frame_time_plot

        self.plot_object = plot_selector.Plot(sync_colors=True, 
                                              allow_two_axis=False, 
                                              orientation='horizontal', 
                                              figsize=(2, 2),
                                              hover_target=None,
                                              time_axis='x')
        margins = {'right': 0.03, 
                    'left': 0.06, 
                    'top': 0.04, 
                    'bottom': 0.03}

        self.plot_object.add_first_ax(margins=margins)

        # Target to plot object is called when set range is active.
        self.plot_object.add_range_target(self._callback_plot_range) 

        self.plot_widget = tkw.PlotFrame(frame,
                                         self.plot_object, 
                                         pack=False,
                                         include_toolbar=False)

    #===========================================================================
    def _set_frame_options(self):
        
        frame = self.labelframe_options
        
        opt = {'padx': 5, 
               'pady': 5, 
               'sticky': 'nsew'}

        
        
        self.labelframe_data = tk.LabelFrame(frame, text='Data file')
        self.labelframe_data.grid(row=0, column=0, columnspan=2, **opt)
        
        self.labelframe_parameter = tk.LabelFrame(frame, text='Parameter')
        self.labelframe_parameter.grid(row=2, column=0, **opt)

        self.labelframe_parameter_contour = tk.LabelFrame(frame, text='Contour plot')
        self.labelframe_parameter_contour.grid(row=2, column=1, **opt)
        
        self.frame_notebook = tk.Frame(frame)
        self.frame_notebook.grid(row=3, column=0, columnspan=2, **opt)

        # tkw.grid_configure(frame, nr_rows=4, r0=4, r1=4, r3=5)
        tkw.grid_configure(frame, nr_rows=4, nr_columns=2, r3=10)
        
        
        pad = {'padx': 5, 
               'pady': 5}
        prop_combobox = {'width': 60}
        #----------------------------------------------------------------------

        # Data file
        self.select_data_widget = tkw.ComboboxWidget(self.labelframe_data, 
                                                   title='',
                                                   prop_combobox=prop_combobox,
#                                                   callback_target=self._on_select_parameter, 
                                                   row=0, 
                                                   pady=5, 
                                                   sticky='w')
        
        
        self.button_load_current = tk.Button(self.labelframe_data, 
                                             text='Update data file',
                                             command=self._update_file)
        self.button_load_current.grid(row=0, column=1, sticky='w', **pad)
        
        self.stringvar_current_data_file = tk.StringVar()
        tk.Label(self.labelframe_data, 
                 textvariable=self.stringvar_current_data_file, 
                 bg=None).grid(row=2, column=0, columnspan=2, sticky='w', **pad)
        tkw.grid_configure(self.labelframe_data, nr_rows=2)
        
        #----------------------------------------------------------------------
        # Parameter listbox 
        self.parameter_widget = tkw.ComboboxWidget(self.labelframe_parameter, 
                                                   title='',
                                                   callback_target=self._on_select_parameter, 
                                                   row=0, 
                                                   pady=5, 
                                                   sticky='w')
        tkw.grid_configure(self.labelframe_parameter)

        # ----------------------------------------------------------------------
        # Parameter contour plot
        self.parameter_contour_plot_widget = tkw.ComboboxWidget(self.labelframe_parameter_contour,
                                                               title='',
                                                               row=0,
                                                               pady=5,
                                                               sticky='w')
        self.button_plot_contour = tk.Button(self.labelframe_parameter_contour,
                                             text='Update contour plot',
                                             command=self._update_contour_plot)
        self.button_plot_contour.grid(row=0, column=1, **pad)

        tkw.grid_configure(self.labelframe_parameter_contour, nr_columns=2)
        
        #----------------------------------------------------------------------
        # Options notebook
        
        self.notebook_options = tkw.NotebookWidget(self.frame_notebook, 
                                                   frames=['Axis range', 'Select', 'Flag', 'Compare', 'Save/Export', 'Map', 'Automatic QC'], row=0)
        tkw.grid_configure(self.frame_notebook, nr_rows=1)
        
        
        self._set_notebook_frame_axis_range()
        self._set_notebook_frame_select()
        self._set_notebook_frame_flag()
        self._set_notebook_frame_compare()
        self._set_notebook_frame_save()
        self._set_notebook_frame_map()
        self._set_notebook_frame_automatic_qc()

    def _set_notebook_frame_automatic_qc(self):
        frame = self.notebook_options.frame_automatic_qc
        qc_routines = self.session.get_qc_routines()
        grip_prop = dict(padx=5,
                         pady=5,
                         sticky='sw')
        self.widget_automatic_qc_options = tkw.CheckbuttonWidget(frame, items=qc_routines, **grip_prop)


        self.button_run_automatic_qc = tk.Button(frame, text='Run QC', command=self._run_automatic_qc)
        self.button_run_automatic_qc.grid(row=0, column=1, **grip_prop)

    def _set_notebook_frame_map(self):
        frame = self.notebook_options.frame_map
        frame_map_1 = tk.Frame(frame)
        frame_map_1.grid(row=0, column=0, sticky='nsew')
        frame_map_2 = tk.Frame(frame)
        frame_map_2.grid(row=0, column=1, sticky='nsew')
        frame_buttons = tk.Frame(frame)
        frame_buttons.grid(row=1, column=0, columnspan=2, sticky='nsew')
        tkw.grid_configure(frame, nr_columns=2, nr_rows=2, r0=10)
        tkw.grid_configure(frame_map_1)
        tkw.grid_configure(frame_map_2)
        tkw.grid_configure(frame_buttons, nr_columns=2)



        # self.map_widget_1 = tkmap.MapWidget(frame_map)
        # self.map_widget_2 = tkmap.MapWidget(frame_options)

        # Get map boundries
        boundaries = self._get_map_boundaries()


        self.map_widget_1 = tkmap.TkMap(frame_map_1, boundaries=boundaries)
        self.map_widget_2 = tkmap.TkMap(frame_map_2, boundaries=boundaries)

        self.button_frame_map_1 = tk.Button(frame_buttons, text='Big map', command=self._popup_map_1)
        self.button_frame_map_1.grid(row=0, column=0, sticky='nsew', pady=5)
        self.button_frame_map_2 = tk.Button(frame_buttons, text='Big map', command=self._popup_map_2)
        self.button_frame_map_2.grid(row=0, column=1, sticky='nsew', pady=5)

    def _popup_map_1(self):
        def delete_map_1():
            self.toplevel_frame_map_1.destroy()
            self.toplevel_map_widget_1 = None 
            
        if self.toplevel_map_widget_1: 
            return
        
        self.toplevel_frame_map_1 = tk.Toplevel(self.controller)

        boundaries = self._get_map_boundaries()

        self.toplevel_map_widget_1 = tkmap.TkMap(self.toplevel_frame_map_1, boundaries=boundaries)
        tkw.grid_configure(self.toplevel_frame_map_1)
        self._update_map_1(self.toplevel_map_widget_1)

        self.toplevel_frame_map_1.protocol('WM_DELETE_WINDOW', delete_map_1)

    def _popup_map_2(self):
        def delete_map_2():
            self.toplevel_frame_map_2.destroy()
            self.toplevel_map_widget_2 = None
        
        if self.toplevel_map_widget_2: 
            return
        self.toplevel_frame_map_2 = tk.Toplevel(self.controller)

        boundaries = self._get_map_boundaries()

        self.toplevel_map_widget_2 = tkmap.TkMap(self.toplevel_frame_map_2, boundaries=boundaries)
        tkw.grid_configure(self.toplevel_frame_map_2)
        self._update_map_2(self.toplevel_map_widget_2)

        self.toplevel_frame_map_2.protocol('WM_DELETE_WINDOW', delete_map_2)

    def _get_map_boundaries(self):
        boundaries = [self.user.map_boundries.setdefault('lon_min', 9),
                      self.user.map_boundries.setdefault('lon_max', 31),
                      self.user.map_boundries.setdefault('lat_min', 53),
                      self.user.map_boundries.setdefault('lat_max', 66)]
        return boundaries        

    #===========================================================================
    def _set_notebook_frame_axis_range(self):
        frame = self.notebook_options.frame_axis_range
        
#        padx=5
#        pady=5
        r=0
        
        #----------------------------------------------------------------------
        # x-axis options
        self.xrange_widget = gui.AxisSettingsTimeWidget(frame, 
                                                   plot_object=self.plot_object, 
                                                   callback=self._callback_axis_widgets, 
                                                   label='time-axis', 
                                                   axis='x', 
                                                   row=r, 
                                                   pady=1,
                                                   sticky='nw')
        r+=1
        
        
        #----------------------------------------------------------------------
        # y-axis options
        self.yrange_widget = gui.AxisSettingsFloatWidget(frame, 
                                                    self.plot_object, 
                                                    callback=self._callback_axis_widgets, 
                                                    label='y-axis', 
                                                    axis='y', 
                                                    row=r, 
                                                    pady=1,
                                                    sticky='nw')
        r+=1
        
        tkw.grid_configure(frame, nr_rows=2)
        
        
    #===========================================================================
    def _set_notebook_frame_select(self):
        frame = self.notebook_options.frame_select
        
        r=0
        
        #----------------------------------------------------------------------
        # Range widget
        self.xrange_selection_widget = gui.RangeSelectorTimeWidget(frame, 
                                                          label='time-range', 
                                                          plot_object=self.plot_object,
                                                          axis='t', 
                                                          row=r)
        r+=1
        
        self.yrange_selection_widget = gui.RangeSelectorFloatWidget(frame, 
                                                          label='y-range', 
                                                          plot_object=self.plot_object, 
                                                          axis='y', 
                                                          row=r)
        tkw.grid_configure(frame, nr_rows=2)
        
        
        #----------------------------------------------------------------------
        # Lasso
#        self.button_lasso_select = ttk.Button(frame, text=u'Lasso select', command=self._lasso_select)
#        self.button_lasso_select.grid(row=r, column=c, padx=padx, pady=pady, sticky='se')

    def _run_automatic_qc(self):
        qc_routine_list = self.widget_automatic_qc_options.get_checked_item_list()
        nr_routines = len(qc_routine_list)
        if nr_routines == 0:
            gui.show_information('Run QC', 'No QC routines selected!')
            return

        if nr_routines == 1:
            text = 'You are about to run 1 automatic quality control. This might take some time. Do you want to continue?'
        else:
            text = 'You are about tu run {} automatic quality controles. This might take some time. Do you want to continue?'.format(nr_routines)

        if not tk.messagebox.askyesno('Run QC', text):
            return

        self.controller.run_progress(lambda: self.session.run_automatic_qc(self.current_file_id,
                                                                           qc_routines=qc_routine_list),
                                     'Running qc on file: {}'.format(self.current_file_id))


        
    #===========================================================================
    def _lasso_select(self):
        self.plot_object.add_mark_lasso_target('first', color='r') # Should be in an other place
        self.plot_object.mark_lasso(line_id='current_flags') # Negative values in plot

    def _update_notebook_frame_flag(self):
        """
        Update flag widget. The apperance of flag widget will change depending on the loaded settings file
        :return:
        """
        try:
            self.frame_flag_widget.destroy()
        except:
            pass
        # file_id self.
        self.gismo_sampling_type_settings = self.current_gismo_object.settings
        self._set_notebook_frame_flag()

    #===========================================================================
    def _set_notebook_frame_flag(self):
        self.frame_flag_widget = tk.Frame(self.notebook_options.frame_flag)
        self.frame_flag_widget.grid(row=0, column=0, sticky='nsew')

        padx=5
        pady=5
        r=0
        c=0
        self.flag_widget = gui.get_flag_widget(parent=self.frame_flag_widget,
                                               settings_object=self.gismo_sampling_type_settings,
                                               user_object=self.controller.user,
                                               callback_flag_data=self._on_flag_widget_flag,
                                               callback_update=self._update_plot,
                                               callback_prop_change=self._on_flag_widget_change,
                                               include_marker_size=True,
                                               row=r,
                                               column=c,
                                               padx=padx,
                                               pady=pady,
                                               sticky='nw')

        tkw.grid_configure(self.frame_flag_widget)


    #===========================================================================
    def _set_notebook_frame_compare(self):
        frame = self.notebook_options.frame_compare
        grid_opt = {'padx': 5,
                    'pady': 5,
                    'sticky': 'nsew'}
        self.labelframe_reference = tk.LabelFrame(frame, text='Reference file')
        self.labelframe_reference.grid(row=0, column=0, **grid_opt)

        # ----------------------------------------------------------------------
        # Reference file
        pad = {'padx': 5,
               'pady': 5}
        prop_combobox = {'width': 60}
        self.select_ref_data_widget = tkw.ComboboxWidget(self.labelframe_reference,
                                                         title='',
                                                         prop_combobox=prop_combobox,
                                                         row=0,
                                                         pady=5,
                                                         sticky='w')

        self.button_load_current_sample = tk.Button(self.labelframe_reference,
                                                    text=u'Load/update reference file',
                                                    command=self._update_file_reference)
        self.button_load_current_sample.grid(row=0, column=1, sticky='w', **pad)

        self.stringvar_current_reference_file = tk.StringVar()
        tk.Label(self.labelframe_reference,
                 textvariable=self.stringvar_current_reference_file,
                 bg=None).grid(row=2, column=0, columnspan=2, sticky='w', **pad)
        tkw.grid_configure(self.labelframe_reference, nr_rows=2)

        self.compare_widget = gui.CompareWidget(frame,
                                                session=self.controller.session,
                                                user=self.user,
                                                callback=self._callback_compare,
                                                row=1,
                                                **grid_opt)
        tkw.grid_configure(frame, nr_rows=2)

    def _update_compare_widget(self):
        self.compare_widget.update_parameter_list(self.current_ref_file_id)


    #===========================================================================
    def _callback_compare(self):
        logging.debug('page_timeseries._callback_compare: Start')
        try:
            match_data = gui.add_compare_to_timeseries_plot(plot_object=self.plot_object,
                                                            session=self.session,
                                                            sample_file_id=self.current_ref_file_id,
                                                            main_file_id=self.current_file_id,
                                                            compare_widget=self.compare_widget,
                                                            help_info_function=self.controller.update_help_information)

            self.map_widget_1.add_scatter(match_data['lat'], match_data['lat'], marker_id='match_data')
        except GISMOExceptionInvalidOption as e:
            gui.show_warning('Invalid option', e)
        except gismo.exceptions.GISMOExceptionInvalidInputArgument as e:
            # Could be
            if not self.stringvar_current_reference_file.get():
                gui.show_warning('File not loaded', 'No reference file selected')
            else:
                gui.show_error('Internal error', 'Un unexpected error occurred. Please contact administration. ')
        logging.debug('page_timeseries._callback_compare: End')

    def _set_notebook_frame_save(self):
        frame = self.notebook_options.frame_dict['Save/Export']
        # frame = self.notebook_options.frame_save

        self.save_widget = gui.SaveWidget(frame,
                                          label='Save file',
                                          callback=self._callback_save_file,
                                          sticky='nw')

        # Export html plot and map
        self.save_widget_html = gui.SaveWidgetHTML(frame,
                                                   label='Export html plots',
                                                   callback=self._callback_save_html,
                                                   default_directory=self.settings['directory']['Export directory'],
                                                   user=self.user,
                                                   sticky='nw',
                                                   row=1)

        tkw.grid_configure(frame, nr_rows=2)


    #===========================================================================
    def _callback_save_file(self, directory, file_name):
        if not self.current_file_id:
            gui.show_information('No file loaded', 'Cant save file, no file loaded.')
        file_path = os.path.realpath(self.current_gismo_object.file_path)
        output_file_path = os.path.realpath('/'.join([directory, file_name]))

        if file_path != output_file_path:
            try:
                self.current_gismo_object.save_file(file_path=output_file_path)
            except GISMOExceptionFileExcists:
                if not messagebox.askyesno('Overwrite file!', 'The given file already exists. Do you want to replace the original file?'):
                    return
        else:
            if not messagebox.askyesno('Overwrite file!', 'Do you want to replace the original file?'):
                return

        # Create temporary file and then overwrite by changing the name. This is so that the process don't get interrupted.
        output_file_path = directory + '/temp_%s' % file_name
        self.current_gismo_object.save_file(file_path=output_file_path, overwrite=True)
        os.remove(file_path)
        shutil.copy2(output_file_path, file_path)
        os.remove(output_file_path)



    def _callback_save_html(self):

        # Import lib here. We dont want to start a thread if we cant import modules
        import libs.sharkpylib.plot.html_plot as html_plot
        self.controller.run_progress(self._save_html, 'Saving plots...')

    def _save_html(self):

        def get_par_list_by_file_id(parameter_list):
            """
            Extendet par i is a parameter starting with Main: or Ref: depending on if its a parameter from the
            main file of reference file.
            :param plot_object:
            :param extended_par:
            :return:
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

        selection = self.save_widget_html.get_selection()

        # Check selection
        export_combined_plots = selection.get('combined_plot')
        export_individual_plots = selection.get('individual_plots')
        export_individual_maps = selection.get('individual_maps')
        parameter_list = selection.get('parameters')
        directory = selection.get('directory')

        # Check selection
        if not any([export_combined_plots, export_individual_plots, export_individual_maps, parameter_list]):
            gui.show_information('No selection', 'You need to select what type of plots/maps to export')

        # Check directory
        if not directory:
            gui.show_information('Missing directory', 'Could not save html maps and/or plots. No directory selected.')
            return
        if not os.path.exists(directory):
            create_dirs = tk.messagebox.askyesno('Missing directory', 'Directory does not exist. Would you like to create a new directory?')
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
        max_nr_par = self.user.process.setdefault('warn_export_nr_parameters', 10)
        if nr_par > max_nr_par:
            ok_to_continue = tk.messagebox.askyesno('Export plots/maps',
                                                    'You have chosen to export {} parameters. '
                                                    'This might take some time and MAY cause the program to crash. '
                                                    'Do you wish to continue anyway? ')
            if not ok_to_continue:
                self.controller.update_help_information('Export aborted by user.')
                return

        main_data = {}
        ref_data = {}
        if self.current_file_id and parameter_dict.get('main'):
            main_data = self.session.get_data(self.current_file_id, *parameter_dict.get('main'))
        if self.current_ref_file_id and parameter_dict.get('ref'):
            ref_data = self.session.get_data(self.current_ref_file_id, *parameter_dict.get('ref'))

        if export_combined_plots:
            combined_plot_object = html_plot.PlotlyPlot()
            # Add Main data
            if main_data:
                for par in main_data:
                    if par == 'time':
                        continue
                    combined_plot_object.add_scatter_data(main_data['time'], main_data[par], name='{} (main)'.format(par),
                                                                mode='markers')
            if ref_data:
                for par in ref_data:
                    if par == 'time':
                        continue
                    combined_plot_object.add_scatter_data(ref_data['time'], ref_data[par], name='{} (ref)'.format(par),
                                                                mode='markers')
            combined_plot_object.plot_to_file(os.path.join(export_dir, 'plot_combined.html'))

        if export_individual_plots:

            flag_selection = self.flag_widget.get_selection()
            selected_flags = flag_selection.selected_flags
            selected_descriptions = flag_selection.selected_descriptions
            if main_data:
                for par in main_data:
                    individual_plot_object = html_plot.PlotlyPlot(title='{} (main)'.format(par), yaxis_title='')
                    for qf, des in zip(selected_flags, selected_descriptions):
                        data = self.session.get_data(self.current_file_id, 'time', par, mask_options={'include_flags': [qf]})
                        individual_plot_object.add_scatter_data(data['time'], data[par],
                                                                name='{} ({})'.format(qf, des),
                                                                mode='markers')
                    individual_plot_object.plot_to_file(os.path.join(export_dir, 'plot_{}.html'.format(par.replace('/', '_'))))
            if ref_data:
                for par in ref_data:
                    individual_plot_object = html_plot.PlotlyPlot(title='{} (ref)'.format(par), yaxis_title='')
                    for qf, des in zip(selected_flags, selected_descriptions):
                        data = self.session.get_data(self.current_ref_file_id, 'time', par, mask_options={'include_flags': [qf]})
                        individual_plot_object.add_scatter_data(data['time'], data[par],
                                                                name='{} ({})'.format(qf, des),
                                                                mode='markers')
                    individual_plot_object.plot_to_file(os.path.join(export_dir, 'plot_{}.html'.format(par.replace('/', '_'))))

        if export_individual_maps:
            pass




    #===========================================================================
    def _callback_axis_widgets(self):
        logging.debug('page_timeseries._callback_axis_widgets: Start')
        # Update limits in settings_object from axis widget.
        self._save_limits_from_axis_widgets()

        # Update limits in plot
        self._update_plot_limits()

        self.plot_object.call_targets()

        # Update plots
        time_limits = self.xrange_widget.get_limits()
        y_limits = self.yrange_widget.get_limits()
        # TODO: Handle error
        time_start, time_end = time_limits
        min_value, max_value = y_limits

        # Save to user
        self.user.range.set(self.current_parameter, 'min', float(min_value))
        self.user.range.set(self.current_parameter, 'max', float(max_value))

        self._update_map_1(highlighted_time_start=time_start, highlighted_time_end=time_end)
        self._update_map_2(highlighted_time_start=time_start, highlighted_time_end=time_end)


        logging.debug('page_timeseries._callback_axis_widgets: End')

    #===========================================================================
    def _callback_plot_range(self):
        logging.debug('page_timeseries._callback_plot_range: Start')
        if not self.plot_object.mark_range_orientation:
            return
        elif self.plot_object.mark_range_orientation == 'vertical':
            gui.update_range_selection_widget(plot_object=self.plot_object,
                                          range_selection_widget=self.yrange_selection_widget)
        elif self.plot_object.mark_range_orientation == 'horizontal':
            gui.update_range_selection_widget(plot_object=self.plot_object,
                                          range_selection_widget=self.xrange_selection_widget)
        logging.debug('page_timeseries._callback_plot_range: End')


    #===========================================================================
    def _update_parameter_list(self):
        logging.debug('page_timeseries._update_parameter_list: Start')
        exclude_parameters = ['time', 'lat', 'lon']
        parameter_list = [item for item in self.session.get_parameter_list(self.current_file_id) if item not in exclude_parameters]

        # Single (plot) parameter widget
        self.parameter_widget.update_items(parameter_list[:],
                                           default_item=None)

        self._update_export_parameter_list()
        logging.debug('page_timeseries._update_parameter_list: End')

    def _update_export_parameter_list(self):
        # Parameters for exporting
        parameter_list = []
        if self.current_file_id:
            for par in self.session.get_parameter_list(self.current_file_id):
                if not par.strip():
                    continue
                parameter_list.append('{} (main)'.format(par))
        if self.current_ref_file_id:
            for par in self.session.get_parameter_list(self.current_file_id):
                if not par.strip():
                    continue
                parameter_list.append('{} (ref)'.format(par))
        self.save_widget_html.update_parameters(parameter_list)

    #===========================================================================
    def _reset_widgets(self):
        logging.debug('page_timeseries._reset_widgets: Start')
        self.plot_object.reset_plot()
        self.parameter_widget.update_items()

        self.xrange_widget.reset_widget()
        self.yrange_widget.reset_widget()
        self.xrange_selection_widget.reset_widget()
        self.yrange_selection_widget.reset_widget()

        logging.debug('page_timeseries._reset_widgets: End')

    #===========================================================================
    def _on_select_parameter(self):
        logging.debug('page_timeseries._on_select_parameter: Start')
        # Reset plot
        self.plot_object.reset_plot()

        self.current_parameter = self.parameter_widget.selected_item

        # Find all stations
        # all_fixed_platforms_id = [self._get_file_id(item) for item in self.controller.listbox_widget_loaded_files.items if
        #                           'fixed platform' in item.lower()]
        # self.current_all_data = dict()
        # for file_id in all_fixed_platforms_id:
        #     if file_id == self.current_file_id:
        #         data = self.session.get_data(file_id, 'lat', 'lon', self.current_parameter)
        #     else:
        #         data = self.session.get_data(file_id, 'lat', 'lon')
        #     self.current_all_data[file_id] = data
        #     self.current_all_data[file_id] = data

        if not self.current_parameter:
            return

        logging.debug('ferrybox: _on_select_parameter')

        # First plot...
        self._update_plot(call_targets=False)

        # ...then set full range in plot without updating (not calling to update the tk.canvas).
        # self.plot_object.zoom_to_data(call_targets=False)

        self._update_plot_limits()
        #
        # # Next is to update limits in settings_object. This will not overwrite old settings.
        self._save_limits_from_plot()
        #
        # # Now update the Axis-widgets...
        self._update_axis_widgets()
        #
        # # ...and update limits in plot
        # self._update_plot_limits()

        self._update_map_2()

        self.plot_object.call_targets()


        logging.debug('page_timeseries._on_select_parameter: End')

    #===========================================================================
    def _update_plot_limits(self):
        logging.debug('page_timeseries._update_plot_limits: Start')

        gui.update_plot_limits_from_settings(plot_object=self.plot_object,
                                             user_object=self.controller.user,
                                             axis='x',
                                             par='time',
                                             call_targets_in_plot_object=False)

        gui.update_plot_limits_from_settings(plot_object=self.plot_object,
                                             user_object=self.controller.user,
                                             axis='y',
                                             par=self.current_parameter,
                                             call_targets_in_plot_object=False)
        logging.debug('page_timeseries._update_plot_limits: End')

    #===========================================================================
    def _save_limits_from_plot(self):
        """
        Method saves limits from plot object and adds information to user_object.
        :return:
        """
        logging.debug('timeseries: _save_limits_from_plot: Start')
        gui.save_limits_from_plot_object(plot_object=self.plot_object,
                                         user_object=self.controller.user,
                                         par='time',
                                         axis='x',
                                         use_plot_limits=False)

        gui.save_limits_from_plot_object(plot_object=self.plot_object,
                                         user_object=self.controller.user,
                                         par=self.current_parameter,
                                         axis='y',
                                         use_plot_limits=False)
        logging.debug('page_timeseries._save_limits_from_plot: End')


    #===========================================================================
    def _save_limits_from_axis_widgets(self):
        logging.debug('page_timeseries._save_limits_from_axis_widgets: Start')

        gui.save_limits_from_axis_time_widget(user_object=self.controller.user,
                                              axis_time_widget=self.xrange_widget,
                                              par='time')

        gui.save_limits_from_axis_float_widget(user_object=self.controller.user,
                                               axis_float_widget=self.yrange_widget,
                                               par=self.current_parameter)
        logging.debug('page_timeseries._save_limits_from_axis_widgets: End')

    #===========================================================================
    def _update_axis_widgets(self):
        logging.debug('page_timeseries._update_axis_widgets: Start')

        gui.update_limits_in_axis_time_widget(user_object=self.controller.user,
                                              axis_time_widget=self.xrange_widget,
                                              plot_object=self.plot_object,
                                              par='time',
                                              axis='x')

        gui.update_limits_in_axis_float_widget(user_object=self.controller.user,
                                               axis_float_widget=self.yrange_widget,
                                               plot_object=self.plot_object,
                                               par=self.current_parameter,
                                               axis='y')
        logging.debug('page_timeseries._update_axis_widgets: End')

    #===========================================================================
    def _on_flag_widget_flag(self):
        logging.debug('page_timeseries._on_flag_widget_flag: Start')
        self.controller.update_help_information('Flagging data, please wait...')
        gui.flag_data_time_series(flag_widget=self.flag_widget,
                              gismo_object=self.current_gismo_object,
                              plot_object=self.plot_object,
                              par=self.current_parameter)

        self._update_plot()

        self.controller.update_help_information('Done!')
        logging.debug('page_timeseries._on_flag_widget_flag: End')

    #===========================================================================
    def _update_plot(self, **kwargs):
        """
        Called by the parameter widget to update plot.
        """
        logging.debug('page_timeseries._update_plot: Start')

        gui.update_time_series_plot(gismo_object=self.current_gismo_object,
                                    par=self.current_parameter,
                                    plot_object=self.plot_object,
                                    flag_widget=self.flag_widget,
                                    help_info_function=self.controller.update_help_information,
                                    call_targets=kwargs.get('call_targets', True))

#         self.xrange_selection_widget.reset_widget()
#         self.yrange_selection_widget.reset_widget()
#         gui.save_user_info_from_flag_widget(self.flag_widget, self.controller.user)

        logging.debug('page_timeseries._update_plot: End')

    def _update_contour_plot(self, **kwargs):
        contour_par = self.parameter_contour_plot_widget.get_value()
        if contour_par not in self.current_contour_parameters:
            gui.show_information('Could not plot contour for parameter "{}"'.format(contour_par))
            return
        par_list = self.current_contour_parameters[contour_par]

        z = []
        y = []
        for par in par_list:
            z.append(self.session.get_data(self.current_file_id, par)[par])
            y.append(float(re.findall('_\d*', par)[0].strip('_')))

        x = self.session.get_data(self.current_file_id, 'time')['time']
        self.plot_object_contour.set_data(x, y, z, contour_plot=True)
        self.plot_object_contour.add_legend()




    #===========================================================================
    def _on_flag_widget_change(self):
        logging.debug('page_timeseries._on_flag_widget_change: Start')
        selection = self.flag_widget.get_selection()
        for k, flag in enumerate(selection.selected_flags):
            self.plot_object.set_prop(ax='first', line_id=flag, **selection.get_prop(flag))
        gui.save_user_info_from_flag_widget(self.flag_widget, self.controller.user)
        logging.debug('page_timeseries._on_flag_widget_change: End')

    def _get_file_id(self, string):
        """
        Returns file_id from a information string like Ferrybox CMEMS: <file_id>
        :param string:
        :return:
        """
        return string.split(':')[-1].strip()

    def _set_current_file(self):
        """
        Sets the current file information. file_id and file_path are set.
        Information taken from self.select_data_widget
        :return:
        """
        self.current_sampling_type = self.select_data_widget.get_value().split(':')[0].strip()
        self.current_file_id = self._get_file_id(self.select_data_widget.get_value())
        self.current_file_path = self.session.get_file_path(self.current_file_id)
        self.current_gismo_object = self.session.get_gismo_object(self.current_file_id)

        self.stringvar_current_data_file.set(self.current_file_path)

    def _set_current_reference_file(self):
        """
        Sets the current reference file information. file_id and file_path are set.
        Information taken from self.select_ref_data_widget
        :return:
        """
        self.current_ref_sampling_type = self.select_ref_data_widget.get_value().split(':')[0].strip()
        self.current_ref_file_id = self._get_file_id(self.select_ref_data_widget.get_value())
        self.current_ref_file_path = self.session.get_file_path(self.current_ref_file_id)
        self.current_ref_gismo_object = self.session.get_gismo_object(self.current_ref_file_id)

    def _update_contour_parameters(self):
        """
        Creates the contour parameter list and updates the contour parameter widget.
        :return:
        """
        par_list = self.session.get_parameter_list(self.current_file_id)
        striped_pars = []
        nr_list = []
        print('='*50)
        for par in par_list:
            print(par, type(par))
            striped_pars.append(re.sub('_\d*', '', par))
            found = re.findall('_\d*', par)
            if found:
                nr_list.append(int(found[0].strip('_')))
            else:
                nr_list.append(0)

        par_list = np.array(par_list)
        striped_pars = np.array(striped_pars)
        nr_list = np.array(nr_list)

        self.current_contour_parameters = dict()
        for spar in set(striped_pars):
            if list(striped_pars).count(spar) > 1:
                boolean = striped_pars == spar
                par_dict = dict(zip(par_list[boolean], nr_list[boolean]))
                sorted_par_list = [item[0] for item in sorted(par_dict.items(), key=lambda kv: kv[1], reverse=True)]
                self.current_contour_parameters[spar] = sorted_par_list

        #     self.current_contour_parameters[par] = sorted_par_listself.current_contour_parameters = dict()
        # for par in set(striped_pars):
        #     if list(striped_pars).count(par) > 1:
        #         self.current_contour_parameters[par] = []
        #
        # for spar in self.current_contour_parameters:
        #     boolean = striped_pars == spar
        #     par_dict = dict(zip(striped_pars[boolean], nr_list[boolean]))
        #     sorted_par_list = [item[0] for item in sorted(par_dict.items(), key=lambda kv: kv[1], reverse=True)]
        #     self.current_contour_parameters[par] = sorted_par_list

        self.parameter_contour_plot_widget.update_items(sorted(self.current_contour_parameters))

    #===========================================================================
    def _update_file(self):
        logging.debug('page_timeseries._update_file: Start')
        self._set_current_file()

        if not self.current_file_id:
            self.save_widget.set_file_path('')
            self.stringvar_current_data_file.set('')
            return

        self._reset_widgets()

        self._update_notebook_frame_flag()

        self._update_valid_time_range_in_time_axis()

        self._update_parameter_list()
        self._update_contour_parameters()
        self._on_select_parameter()

        self.plot_object.zoom_to_data(call_targets=True)

        self._update_frame_save_widget()

        self._update_frame_reference_file()

        self._update_map_1()
        self._update_map_2()
        
        self._update_frame_automatic_qc()

        logging.debug('page_timeseries._update_file: End')

    def _update_frame_automatic_qc(self):
        self.widget_automatic_qc_options.deactivate_all()
        for routine in self.session.get_valid_qc_routines(self.current_file_id):
            self.widget_automatic_qc_options.activate(routine)

    def _update_valid_time_range_in_time_axis(self):
        data_file_string = self.select_data_widget.get_value()
        data_file_id = self._get_file_id(data_file_string)
        gui.set_valid_time_in_time_axis(gismo_object=self.session.get_gismo_object(data_file_id),
                                        time_axis_widget=self.xrange_widget)

    def _update_frame_save_widget(self):
        if not self.current_file_path:
            self.save_widget.set_file_path()
            self.stringvar_current_data_file.set('')
            return
        self.save_widget.set_file_path(self.current_file_path)

    def _update_frame_reference_file(self):
        # Update reference file combobox. Should not include selected file.
        all_files = self.controller.get_loaded_files_list()
        ref_file_list = [item for item in all_files if item != self.stringvar_current_reference_file.get()]
        self.select_ref_data_widget.update_items(ref_file_list)

    def _update_map_1(self, *args, **kwargs):
        if args:
            map_list = args
        else:
            map_list = [self.map_widget_1, self.toplevel_map_widget_1]

        for map_widget in map_list:
            if not map_widget:
                continue

            map_widget.delete_all_markers()
            map_widget.delete_all_map_items()

            if 'fixed platform' in self.current_sampling_type.lower():
                title = 'Fixed platforms'

                data = self.session.get_data(file_id, 'lat', 'lon', self.current_parameter)

                print('TITLE', title)
                lat_list = []
                lon_list = []
                for file_id in self.current_all_data:
                    lat_list.append(np.nanmean(self.current_all_data[file_id]['lat']))
                    lon_list.append(np.nanmean(self.current_all_data[file_id]['lon']))

                map_widget.add_markers(lat_list, lon_list, marker_id='all_pos', linestyle='None', marker='o', color='black', markersize=10)

                map_widget.set_title(title, position=[0.5, 1.05])
                print(lat_list)


                # Whole track as base
                # data = self.session.get_data(self.current_file_id, 'lat', 'lon')
                # map_widget.add_line(data['lat'], data['lon'], marker_id='track_base', color='black')
                #
                # # Highlighted track
                # data = self.session.get_data(self.current_file_id, 'lat', 'lon',
                #                              filter_options={'time_start': kwargs.get('highlighted_time_start', None),
                #                                              'time_end': kwargs.get('highlighted_time_end', None)})
                # map_widget.add_line(data['lat'], data['lon'], marker_id='track_highlighted', color='blue')
                #
                # map_widget.set_title(title, position=[0.5, 1.05])

    def _update_map_2(self, *args, **kwargs):
        if args:
            map_list = args
        else:
            map_list = [self.map_widget_2, self.toplevel_map_widget_2]

        for map_widget in map_list:
            if not map_widget:
                continue

            map_widget.delete_all_markers()
            map_widget.delete_all_map_items()

            if 'ferrybox' in self.current_sampling_type.lower():
                # Set map 2
                selected_flags = self.flag_widget.get_selection().selected_flags
                data = self.session.get_data(self.current_file_id, 'lat', 'lon', self.current_parameter,
                                             filter_options={'time_start': kwargs.get('highlighted_time_start', None),
                                                             'time_end': kwargs.get('highlighted_time_end', None)},
                                             mask_options={'include_flags': selected_flags})

                cmap_string = self.user.parameter_colormap.get(self.current_parameter)
                cmap = self.colormaps.get(cmap_string)

                vmin, vmax = self.yrange_widget.get_limits()

                marker_name = map_widget.add_scatter(lat=data['lat'], lon=data['lon'],
                                                            values=data[self.current_parameter],
                                                            marker_size=10,
                                                            color_map=cmap,
                                                            marker_type='o',
                                                            marker_id='track',
                                                            edge_color=None,
                                                            zorder=10, vmin=vmin, vmax=vmax)
                # self.map_widget_2.add_scatter(data['lat'], data['lon'], data[self.current_parameter], title=self.current_parameter)
                map_widget.add_colorbar(marker_name,
                                      title=self.session.get_unit(self.current_file_id, self.current_parameter),
                                      orientation=u'vertical',
                                      position=[0.93, 0.02, 0.05, 0.3],
                                      tick_side=u'left',
                                      format='%.1f')
                                      # #                                       display_every=5,
                                      # nr_ticks=self.stringvar_nr_ticks.get())

                map_widget.set_title(self.current_parameter, position=[0.5, 1.05])


        
    #===========================================================================
    def _update_file_reference(self):
        logging.debug('page_timeseries._update_file_reference: Start')
        self._set_current_reference_file()
        
        if not self.current_ref_file_id:
            self.stringvar_current_reference_file.set('')
            return

        if not self.current_ref_file_path:
            self.stringvar_current_reference_file.set('')
            return
        self.stringvar_current_reference_file.set(self.current_ref_file_path)

        self._update_compare_widget()

        logging.debug('page_timeseries._update_file_reference: End')
        

