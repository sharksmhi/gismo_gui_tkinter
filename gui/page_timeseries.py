#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2016-2017 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import shutil
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
        self.session = controller.session
        self.settings = controller.settings

        self.gismo_sampling_type_settings = None

    #===========================================================================
    def startup(self):
        self._set_frame()

        # Set reference info
        gui.update_compare_widget(compare_widget=self.compare_widget,
                                  settings_object=self.settings)

        self.update_page()
        
    #===========================================================================
    def update_page(self):
        self.select_data_widget.update_items(self.controller.get_loaded_files_list())
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
        tkw.grid_configure(self.labelframe_parameter, nr_rows=1)
        
        #----------------------------------------------------------------------
        # Options notebook
        
        self.notebook_options = tkw.NotebookWidget(self.frame_notebook, 
                                                   frames=['Axis range', 'Select', 'Flag', 'Compare', 'Save'], row=0)  
        tkw.grid_configure(self.frame_notebook, nr_rows=1)
        
        
        self._set_notebook_frame_axis_range()
        self._set_notebook_frame_select()
        self._set_notebook_frame_flag()
        self._set_notebook_frame_compare()
        self._set_notebook_frame_save()
        
        
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
                                            callback=self._callback_sample)
        
        
    #===========================================================================
    def _callback_sample(self):
        logging.debug('page_ferrybox._callback_sample: Start')
        gui.add_sample_data_to_plot(plot_object=self.plot_object, 
                                    par=core.Boxen().current_par_ferrybox, 
                                    sample_object=core.Boxen().current_sample_object, 
                                    gismo_object=core.Boxen().current_ferrybox_object, 
                                    compare_widget=self.compare_widget, 
                                    help_info_function=self.controller.update_help_information)
        logging.debug('page_ferrybox._callback_sample: End')
        
        
    #===========================================================================
    def _set_notebook_frame_save(self):
        frame = self.notebook_options.frame_save
        
        self.save_widget = gui.SaveWidget(frame, 
                                      callback=self._callback_save_file, 
                                      sticky='nw') 
        
        tkw.grid_configure(frame)
        
        
    #===========================================================================
    def _callback_save_file(self, directory, file_name):
        file_path = os.path.realpath(self.current_gismo_object.file_path)
        output_file_path = os.path.realpath('/'.join([directory, file_name]))
        
        if file_path != output_file_path:
            self.current_gismo_object.save_file(output_file_path)
        else:
            overwrite = messagebox.askyesno(u'Overwrite file!', u'Do you want to replace the original file?')
            if not overwrite:
                return
            # Create temporary file and then overwrite by changing the name. This is so that the process don't get interrupted.
            output_file_path = directory + '/temp_%s' % file_name
            self.current_gismo_object.save_file(output_file_path)
            os.remove(file_path)
            shutil.copy2(output_file_path, file_path)
        
        
    #===========================================================================
    def _callback_axis_widgets(self):
        logging.debug('page_ferrybox._callback_axis_widgets: Start')
        # Update limits in settings_object from axis widget.
        self._save_limits_from_axis_widgets()
        
        # Update limits in plot
        self._update_plot_limits()
    
        
        self.plot_object.call_targets()
        logging.debug('page_ferrybox._callback_axis_widgets: End')
    
    #===========================================================================
    def _on_file_update(self):
        logging.debug('page_ferrybox._on_file_update: Start')
        # Update valid time range in time axis

        data_file_id = self._get_file_id(self.select_data_widget.get_value())
        gui.set_valid_time_in_time_axis(gismo_object=self.session.get_gismo_object(data_file_id),
                                        time_axis_widget=self.xrange_widget)

        reference_file_id = self._get_file_id(self.select_ref_data_widget.get_value())
        gui.set_valid_time_in_time_axis(gismo_object=self.session.get_gismo_object(reference_file_id),
                                        time_axis_widget=self.xrange_selection_widget)
        
        self._update_parameter_list()
        self._on_select_parameter()
        logging.debug('page_ferrybox._on_file_update: End')
        
    #===========================================================================
    def _callback_plot_range(self):
        logging.debug('page_ferrybox._callback_plot_range: Start')
        if not self.plot_object.mark_range_orientation:
            return
        elif self.plot_object.mark_range_orientation == 'vertical':
            gui.update_range_selection_widget(plot_object=self.plot_object,
                                          range_selection_widget=self.yrange_selection_widget)
        elif self.plot_object.mark_range_orientation == 'horizontal':
            gui.update_range_selection_widget(plot_object=self.plot_object,
                                          range_selection_widget=self.xrange_selection_widget)
        logging.debug('page_ferrybox._callback_plot_range: End')

    
    #===========================================================================
    def _update_parameter_list(self):
        logging.debug('page_ferrybox._update_parameter_list: Start')
        exclude_parameters = ['time', 'lat', 'lon']
        parameter_list = [item for item in self.session.get_parameter_list(self.current_file_id) if item not in exclude_parameters]
        self.parameter_widget.update_items(parameter_list,
                                           default_item=None)
        logging.debug('page_ferrybox._update_parameter_list: End')  
                                           
    #===========================================================================
    def _reset_widgets(self):
        logging.debug('page_ferrybox._reset_widgets: Start')  
        self.plot_object.reset_plot()
        self.parameter_widget.update_items()

        self.xrange_widget.reset_widget()
        self.yrange_widget.reset_widget()
        self.xrange_selection_widget.reset_widget()
        self.yrange_selection_widget.reset_widget()
        
        logging.debug('page_ferrybox._reset_widgets: End')  
        
    #===========================================================================
    def _on_select_parameter(self):
        logging.debug('page_ferrybox._on_select_parameter: Start')
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


        logging.debug('page_ferrybox._on_select_parameter: End')

    #===========================================================================
    def _update_plot_limits(self):
        logging.debug('page_ferrybox._update_plot_limits: Start')
        
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
        logging.debug('page_ferrybox._update_plot_limits: End')
    
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
        logging.debug('page_ferrybox._save_limits_from_axis_widgets: Start')
                           
        gui.save_limits_from_axis_time_widget(user_object=self.controller.user,
                                              axis_time_widget=self.xrange_widget,
                                              par='time')
                                          
        gui.save_limits_from_axis_float_widget(user_object=self.controller.user,
                                               axis_float_widget=self.yrange_widget,
                                               par=self.current_parameter)
        logging.debug('page_ferrybox._save_limits_from_axis_widgets: End')
        
    #===========================================================================
    def _update_axis_widgets(self):
        logging.debug('page_ferrybox._update_axis_widgets: Start')
        
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
        logging.debug('page_ferrybox._update_axis_widgets: End')    
    
    #===========================================================================
    def _on_flag_widget_flag(self):
        logging.debug('page_ferrybox._on_flag_widget_flag: Start')
        self.controller.update_help_information('Flagging data, please wait...')
        gui.flag_data_time_series(flag_widget=self.flag_widget, 
                              gismo_object=self.current_gismo_object,
                              plot_object=self.plot_object, 
                              par=self.current_parameter)
        
        self._update_plot()
        
        self.controller.update_help_information('Done!')
        logging.debug('page_ferrybox._on_flag_widget_flag: End')
        
    #===========================================================================
    def _update_plot(self, **kwargs):
        """
        Called by the parameter widget to update plot.  
        """        
        logging.debug('page_ferrybox._update_plot: Start')
        
        gui.update_time_series_plot(gismo_object=self.current_gismo_object,
                                    par=self.current_parameter,
                                    plot_object=self.plot_object,
                                    flag_widget=self.flag_widget,
                                    help_info_function=self.controller.update_help_information,
                                    call_targets=kwargs.get('call_targets', True))
        
#         self.xrange_selection_widget.reset_widget()
#         self.yrange_selection_widget.reset_widget()
        gui.save_user_info_from_flag_widget(self.flag_widget, self.controller.user)
        
        logging.debug('page_ferrybox._update_plot: End')



    #===========================================================================
    def _on_flag_widget_change(self):
        logging.debug('page_ferrybox._on_flag_widget_change: Start')
        selection = self.flag_widget.get_selection()
        for k, flag in enumerate(selection.selected_flags):
            self.plot_object.set_prop(ax='first', line_id=flag, **selection.get_prop(flag))
        logging.debug('page_ferrybox._on_flag_widget_change: End')

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
        logging.debug('page_ferrybox._update_file: Start')
        self._set_current_file()

        if not self.current_file_id:
            self.save_widget.set_file_path('')
            self.stringvar_current_file.set('')
            return
        
        self._reset_widgets() 
        
        # Update flag widget. The apperance of flag widget will change depending on the loaded settings file 
        self._update_notebook_frame_flag()
        
        self._on_file_update()

        if not self.current_file_path:
            self.save_widget.set_file_path()
            self.stringvar_current_data_file.set('')
            return
        self.save_widget.set_file_path(self.current_file_path)
        self.stringvar_current_data_file.set(self.current_file_path)

        logging.debug('page_ferrybox._update_file: End')
        
        
    #===========================================================================
    def _update_file_reference(self):
        logging.debug('page_ferrybox._update_file_reference: Start')
        self._set_current_reference_file()
        
        if not self.current_ref_file_id:
            self.stringvar_current_reference_file.set('')
            return

        if not self.current_ref_file_path:
            self.stringvar_current_reference_file.set('')
            return
        self.stringvar_current_reference_file.set(self.current_ref_file_path)

        logging.debug('page_ferrybox._update_file_reference: End')
        

