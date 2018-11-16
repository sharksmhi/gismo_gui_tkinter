#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2016-2017 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import shutil
import datetime
import sys

# Python 2.7
import tkinter as tk 

from tkinter import ttk
from tkinter import messagebox


import gui
import core


import libs.sharkpylib.gismo as gismo
import libs.sharkpylib.plot.plot_selector as plot_selector
import libs.sharkpylib.tklib.tkinter_widgets as tkw
import libs.sharkpylib.tklib.tkmap as tkmap

from libs.sharkpylib.gismo.exceptions import *

import logging


"""
================================================================================
================================================================================
================================================================================
"""
class PageTimeseries(tk.Frame):
    """
    Dummy page used as a base.
    """
    def __init__(self, parent, controller, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        # parent is the frame "container" in App. contoller is the App class
        self.parent = parent
        self.controller = controller
        self.user = controller.user
        self.session = controller.session
        self.settings = controller.settings

        self.gismo_sampling_type_settings = None

        self.current_ref_file_id = None
        self.current_file_id = None

    #===========================================================================
    def startup(self):
        self._set_frame()

        self.update_page()
        
    #===========================================================================
    def update_page(self):
        loaded_file_list = self.controller.get_loaded_files_list()
        add_file_list = [item for item in loaded_file_list if 'PhysicalChemical' not in item]

        self.select_data_widget.update_items(add_file_list)
        self.select_ref_data_widget.update_items(self.controller.get_loaded_files_list())
        # self.stringvar_current_file.set('')
        # self.stringvar_current_sample_file.set('')

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
        Updated     20180822    by Magnus
        """
        frame = self.labelframe_plot
        
        self.plot_object = plot_selector.Plot(sync_colors=True, 
                                              allow_two_axis=False, 
                                              orientation='horizontal', 
                                              figsize=(2, 2),
#                                               figsize=None,
#                                              figsize=(12, 7), 
                                              time_axis='x')
        margins = {'right': 0.03, 
                    'left': 0.06, 
                    'top': 0.04, 
                    'bottom': 0.03}
        self.plot_object.add_first_ax(margins=margins)
        
        # Target to plot object is called when set range is activ. 
        self.plot_object.add_range_target(self._callback_plot_range) 
        
#        f = tk.Toplevel(frame)
#        f1 = tk.Frame(f)
#        f1.pack(side='left', fill='both', expand=True)
#        f2 = tk.Frame(f)
#        f2.pack(side='right', fill='both', expand=True)
        self.plot_widget = tkw.PlotFrame(frame, 
                                         self.plot_object, 
                                         pack=False,
                                         include_toolbar=False)
        
#        button = tk.Button(f2, text='TEST BUTTON')
##        button.pack(side='right', fill='both', expand=True)
#        button.grid(row=0, column=0, padx=40, pady=30, sticky='nsew')
        # Add taget method
#        self.controller.loaded_files_combobox_widget.add_target(self._update_file)
        tkw.grid_configure(self.labelframe_plot)
        
    #===========================================================================
    def _set_frame_options(self):
        
        frame = self.labelframe_options
        
        opt = {'padx': 5, 
               'pady': 5, 
               'sticky': 'nsew'}

        
        
        self.labelframe_data = tk.LabelFrame(frame, text='Data file')
        self.labelframe_data.grid(row=0, column=0, **opt)
        
        self.labelframe_reference = tk.LabelFrame(frame, text='Reference file')
        self.labelframe_reference.grid(row=1, column=0, **opt)
        
        self.labelframe_parameter = tk.LabelFrame(frame, text='Parameter')
        self.labelframe_parameter.grid(row=2, column=0, **opt)
        
        self.frame_notebook = tk.Frame(frame)
        self.frame_notebook.grid(row=3, column=0, **opt)
        
        tkw.grid_configure(frame, nr_rows=4, r0=5, r1=5, r3=5)
        
        
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
                    text=u'Load/update main file', 
                    command=self._update_file)
        self.button_load_current.grid(row=0, column=1, sticky='w', **pad)
        
        self.stringvar_current_data_file = tk.StringVar()
        tk.Label(self.labelframe_data, 
                 textvariable=self.stringvar_current_data_file, 
                 bg=None).grid(row=2, column=0, columnspan=2, sticky='w', **pad)
        tkw.grid_configure(self.labelframe_data, nr_rows=3)
        
        #----------------------------------------------------------------------
        # Reference file
        self.select_ref_data_widget = tkw.ComboboxWidget(self.labelframe_reference,
                                                         title='',
                                                         prop_combobox=prop_combobox,
                                                         #                                                   callback_target=self._on_select_parameter,
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
        
        #----------------------------------------------------------------------
        # Parameter listbox 
        self.parameter_widget = tkw.ComboboxWidget(self.labelframe_parameter, 
                                                   title='',
                                                   callback_target=self._on_select_parameter, 
                                                   row=0, 
                                                   pady=5, 
                                                   sticky='w')
        self.stringvar_parameter_info = tk.StringVar()
        tk.Label(self.labelframe_parameter, textvariable=self.stringvar_parameter_info)
        tkw.grid_configure(self.labelframe_parameter, nr_rows=1)
        
        #----------------------------------------------------------------------
        # Options notebook
        
        self.notebook_options = tkw.NotebookWidget(self.frame_notebook, 
                                                   frames=['Axis range', 'Select', 'Flag', 'Compare', 'Save/Export', 'Preview map'], row=0)
        tkw.grid_configure(self.frame_notebook, nr_rows=1)
        
        
        self._set_notebook_frame_axis_range()
        self._set_notebook_frame_select()
        self._set_notebook_frame_flag()
        self._set_notebook_frame_compare()
        self._set_notebook_frame_save()
        self._set_notebook_frame_preview_map()
        
    def _set_parameter_info(self, text=''):
        self.stringvar_parameter_info.set(text)

    def _set_notebook_frame_preview_map(self):
        frame = self.notebook_options.frame_preview_map
        self.preview_map_widget = tkmap.MapWidget(frame)
        tkw.grid_configure(frame)


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
                                                   pady=1)   
        r+=1
        
        
        #----------------------------------------------------------------------
        # y-axis options
        self.yrange_widget = gui.AxisSettingsFloatWidget(frame, 
                                                    self.plot_object, 
                                                    callback=self._callback_axis_widgets, 
                                                    label='y-axis', 
                                                    axis='y', 
                                                    row=r, 
                                                    pady=1) 
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
        
        
    #===========================================================================
    def _lasso_select(self):
        self.plot_object.add_mark_lasso_target('first', color='r') # Should be in an other place
        self.plot_object.mark_lasso(line_id='current_flags') # Negative values in plot

    def _update_notebook_frame_flag(self):
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
                
        self.compare_widget = gui.CompareWidget(frame,
                                                session=self.controller.session,
                                                user=self.user,
                                                callback=self._callback_sample)

    def _update_compare_widget(self):
        self.compare_widget.update_parameter_list(self.current_ref_file_id)

        
    #===========================================================================
    def _callback_sample(self):
        logging.debug('page_timeseries._callback_sample: Start')
        try:
            gui.add_sample_data_to_timeseries_plot(plot_object=self.plot_object,
                                                    session=self.controller.session,
                                                    sample_file_id=self.current_ref_file_id,
                                                    main_file_id=self.current_file_id,
                                                    compare_widget=self.compare_widget,
                                                    help_info_function=self.controller.update_help_information)
        except GISMOExceptionInvalidOption as e:
            gui.show_warning('Invalid option', e)
        except gismo.exceptions.GISMOExceptionInvalidInputArgument as e:
            # Could be
            if not self.stringvar_current_reference_file.get():
                gui.show_warning('File not loaded', 'No reference file selected')
            else:
                gui.show_error('Internal error', 'Un unexpected error occurred. Please contact administration. ')
        logging.debug('page_timeseries._callback_sample: End')

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
            self.current_gismo_object.save_file(file_path=output_file_path)
        else:
            overwrite = messagebox.askyesno(u'Overwrite file!', u'Do you want to replace the original file?')
            if not overwrite:
                return
            # Create temporary file and then overwrite by changing the name. This is so that the process don't get interrupted.
            output_file_path = directory + '/temp_%s' % file_name
            self.current_gismo_object.save_file(file_path=output_file_path)
            os.remove(file_path)
            shutil.copy2(output_file_path, file_path)




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
                                                    'This might take some time and MAY make the program crash. '
                                                    'Do you wish to continue anyway? ')
            if not ok_to_continue:
                self.controller.update_help_information('Export aborted by user.')
                return

        main_data = {}
        ref_data = {}
        if parameter_dict.get('main'):
            main_data = self.session.get_data(self.current_file_id, *parameter_dict.get('main'))
        if parameter_dict.get('ref'):
            ref_data = self.session.get_data(self.current_file_id, *parameter_dict.get('ref'))

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
                    individual_plot_object = html_plot.PlotlyPlot(title=par, yaxis_title='')
                    for qf, des in zip(selected_flags, selected_descriptions):
                        data = self.session.get_data(self.current_file_id, 'time', par, mask_options={'include_flags': [qf]})
                        individual_plot_object.add_scatter_data(data['time'], data[par],
                                                                name='{} ({})'.format(qf, des),
                                                                mode='markers')
                    individual_plot_object.plot_to_file(os.path.join(export_dir, 'plot_{}.html'.format(par.replace('/', '_'))))
            if ref_data:
                for par in ref_data:
                    individual_plot_object = html_plot.PlotlyPlot(title=par, yaxis_title='')
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
        self.current_parameter = self.parameter_widget.selected_item
        if not self.current_parameter:
            return
            
        logging.debug('ferrybox: _on_select_parameter')
            
        # First plot...
        self._update_plot(call_targets=False)
        
        # ...then set full range in plot without updating (not calling to update the tk.canvas). 
        self.plot_object.zoom_to_data(call_targets=False)
        #
        # # Next is to update limits in settings_object. This will not overwrite old settings.
        self._save_limits_from_plot()
        #
        # # Now update the Axis-widgets...
        self._update_axis_widgets()
        #
        # # ...and update limits in plot
        # self._update_plot_limits()
        #
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

    #===========================================================================
    def _update_file(self):
        logging.debug('page_timeseries._update_file: Start')
        self._set_current_file()

        if not self.current_file_id:
            self.save_widget.set_file_path('')
            self.stringvar_current_file.set('')
            return
        
        self._reset_widgets() 
        
        # Update flag widget. The apperance of flag widget will change depending on the loaded settings file 
        self._update_notebook_frame_flag()

        # Update valid time range in time axis
        data_file_string = self.select_data_widget.get_value()
        data_file_id = self._get_file_id(data_file_string)
        gui.set_valid_time_in_time_axis(gismo_object=self.session.get_gismo_object(data_file_id),
                                        time_axis_widget=self.xrange_widget)

        self._update_parameter_list()
        self._on_select_parameter()

        if not self.current_file_path:
            self.save_widget.set_file_path()
            self.stringvar_current_data_file.set('')
            return
        self.save_widget.set_file_path(self.current_file_path)
        self.stringvar_current_data_file.set(self.current_file_path)

        # Update reference file combobox. Should not include selected file.
        all_files = self.controller.get_loaded_files_list()
        ref_file_list = [item for item in all_files if item != data_file_string]
        self.select_ref_data_widget.update_items(ref_file_list)

        self._update_preview_map()

        logging.debug('page_timeseries._update_file: End')

    def _update_preview_map(self):
        data = self.session.get_data(self.current_file_id, 'lat', 'lon')
        lat = data['lat']
        lon = data['lon']

        self.preview_map_widget.delete_all_markers()

        if 'ferrybox' in self.current_sampling_type.lower():
            title = 'Ferrybox route'
            self.preview_map_widget.add_simple_line(lat, lon, title=title)

        
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
        

