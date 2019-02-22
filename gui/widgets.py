#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import matplotlib as mpl
from matplotlib.figure import Figure
from mpl_toolkits.basemap import Basemap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime

import os
import numpy as np
import pandas as pd
#import shutil


import gui

import libs.sharkpylib.tklib.tkinter_widgets as tkw
import libs.sharkpylib.tklib.tkmap as tkmap

import logging
gui_logger = logging.getLogger('gui_logger')

"""
================================================================================
================================================================================
================================================================================
"""
class RangeSelectorFloatWidget(ttk.Labelframe):
     
    def __init__(self, 
                 parent, 
                 label='Range selection', 
                 axis='y', 
                 prop_frame={}, 
                 line_id='current_flags', 
                 plot_object=None, 
                 callback=None, 
                 only_negative_values=False, 
                 **kwargs):

        self.line_id = line_id
        
        self.plot_object = plot_object
        self.callback = callback
        self.only_negative_values = only_negative_values
        
        self.axis = axis
        self.x_list = ['x', 't']
        self.y_list = ['y', 'z']
        
        self.prop_frame = {}
        self.prop_frame.update(prop_frame)
        
        self.grid_frame = {'padx': 5, 
                           'pady': 5, 
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)
        
        ttk.Labelframe.__init__(self, parent, text=label, **self.prop_frame)
        self.grid(**self.grid_frame)
        
        self._set_frame()
    
    
    #==========================================================================
    def _set_frame(self):
        """
        Updated 20180825     
        """
        padx = 5
        pady = 5
        
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, padx=padx, pady=pady, sticky='w')
        tkw.grid_configure(self)
        
        r=0
        
        entry_width = 10
        
        #-----------------------------------------------------------------------------------------------------------
        ttk.Button(frame, text=u'Mark max', command=self._mark_max).grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        # Entries to display selected max values
        self.stringvar_max = tk.StringVar()
        self.entry_mark_max = tk.Entry(frame, textvariable=self.stringvar_max, width=entry_width)
        self.entry_mark_max.grid(row=r, column=1, padx=padx, pady=pady, sticky='w')
        self.entry_mark_max.bind('<Return>', self._on_return_entry_max)
        self.stringvar_max.trace("w", lambda name, index, mode, 
                                 sv=self.stringvar_max, 
                                 en=self.entry_mark_max: tkw.check_float_entry(sv, en, only_negative_values=self.only_negative_values))
        r+=1        
        
        
        ttk.Button(frame, text=u'Mark min', command=self._mark_min).grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        # Entries to display selected min values
        self.stringvar_min = tk.StringVar()
        self.entry_mark_min = tk.Entry(frame, textvariable=self.stringvar_min, width=entry_width)
        self.entry_mark_min.grid(row=r, column=1, padx=padx, pady=pady, sticky='w')
        self.entry_mark_min.bind('<Return>', self._on_return_entry_min)
        self.stringvar_min.trace("w", lambda name, index, mode, 
                                 sv=self.stringvar_min, 
                                 en=self.entry_mark_min: tkw.check_float_entry(sv, en, only_negative_values=self.only_negative_values))
        r+=1
        
            
        ttk.Button(frame, text=u'Clear mark', command=self._clear_mark).grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        tkw.grid_configure(frame, nr_rows=r+1, nr_columns=2)
        
        
    #========================================================================== 
    def set_min(self, min_value):
        if min_value == None:
            self.stringvar_min.set('')
        else:
            self.stringvar_min.set(str(min_value))
        
    #========================================================================== 
    def set_max(self, max_value):
        if max_value == None:
            self.stringvar_max.set('')
        else:
            self.stringvar_max.set(str(max_value))

    #========================================================================== 
    def _mark_min(self):
        if not self.plot_object:
            return
            
        if self.callback:
            self.callback()
            
        self.plot_object.add_mark_range_target(1, color='r') # Should be in an other place
        if self.axis in self.y_list:
            self.plot_object.mark_range_from_bottom(line_id=self.line_id) # Negative values in plot
        elif self.axis in self.x_list:
            self.plot_object.mark_range_from_left(line_id=self.line_id)
        
    #========================================================================== 
    def _mark_max(self):
        if not self.plot_object:
            return
            
        if self.callback:
            self.callback()
        
        self.plot_object.add_mark_range_target(1, color='r') # Should be in an other place
        if self.axis in self.y_list:
            self.plot_object.mark_range_from_top(line_id=self.line_id) # Negative values in plot
        elif self.axis in self.x_list:
            self.plot_object.mark_range_from_right(line_id=self.line_id)
        
    #========================================================================== 
    def _clear_mark(self):
        if not self.plot_object:
            return
        self.plot_object.clear_marked_range()
        self.plot_object.clear_marked_points()
        self.stringvar_min.set('')
        self.stringvar_max.set('')
        
        if self.callback:
            self.callback()
        
    #===========================================================================
    def _on_return_entry_min(self, event):
        if not self.plot_object:
            return
        
        min_value = self.stringvar_min.get()
        if min_value:
            min_value = float(min_value)
            
        max_value = self.stringvar_max.get()
        if max_value:
            max_value = float(max_value)
            
        if min_value > max_value:
            min_value = str(max_value)
            self.stringvar_min.set(min_value)
            
        if self.axis in self.y_list:
            self.plot_object.set_bottom_range(min_value, 
                                              diconnect_events=True, 
                                              line_id=self.line_id)
        elif self.axis in self.x_list:
            self.plot_object.set_left_range(min_value, 
                                             diconnect_events=True, 
                                             line_id=self.line_id)
            
        self.entry_mark_max.focus()
        self.entry_mark_max.select_range('0', 'end')
    
    #===========================================================================
    def _on_return_entry_max(self, event):
        if not self.plot_object:
            return
            
        min_value = self.stringvar_min.get()
        if min_value:
            min_value = float(min_value)
            
        max_value = self.stringvar_max.get()
        if max_value:
            max_value = float(max_value)
            
        if max_value < min_value:
            max_value = str(min_value)
            self.stringvar_max.set(max_value)
        
        if self.axis in self.y_list:
            self.plot_object.set_top_range(max_value, 
                                           diconnect_events=True, 
                                           line_id=self.line_id)
        elif self.axis in self.x_list:
            self.plot_object.set_right_range(max_value, 
                                            diconnect_events=True, 
                                            line_id=self.line_id)
            
        self.entry_mark_min.focus()
        self.entry_mark_min.select_range('0', 'end')

    #===========================================================================
    def reset_widget(self):
        self.stringvar_min.set('')
        self.stringvar_max.set('')

    # ===========================================================================
    def clear_widget(self):
        self.stringvar_min.set('')
        self.stringvar_max.set('')

    #===========================================================================
    def disable_widget(self):
        for children in self.winfo_children:
            children.config(state='disabled')
            
    #===========================================================================
    def enable_widget(self):
        for children in self.winfo_children:
            children.config(state='normal')

"""
================================================================================
================================================================================
================================================================================
"""
class RangeSelectorTimeWidget(ttk.Labelframe):
     
    def __init__(self, 
                 parent, 
                 label='Range selection', 
                 axis='x', 
                 prop_frame={}, 
                 line_id='current_flags', 
                 plot_object=None,
                 **kwargs):

        self.line_id = line_id
        
        self.plot_object = plot_object
        
        self.axis = axis
        self.x_list = ['x', 't']
        self.y_list = ['y', 'z']
        
        self.prop_frame = {}
        self.prop_frame.update(prop_frame)
        
        self.grid_frame = {'padx': 5, 
                           'pady': 5, 
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)
        
        ttk.Labelframe.__init__(self, parent, text=label, **self.prop_frame)
        self.grid(**self.grid_frame)
        
        self._set_frame()
    
    #==========================================================================
    def _set_frame(self):
        padx = 5
        pady = 5
        
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, padx=padx, pady=pady, sticky='w')
        tkw.grid_configure(self)
        
        r=0
        
        ttk.Button(frame, text=u'Mark from', command=self._mark_min).grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        self.time_widget_from = tkw.TimeWidget(frame, 
                                  title='From', 
                                  show_header=True,
                                  lowest_time_resolution='second',
                                  callback_target=self._callback_time_widget_from,
                                  row=r, 
                                  column=1)
        r+=1  
        
        #-----------------------------------------------------------------------------------------------------------
        ttk.Button(frame, text=u'Mark to', command=self._mark_max).grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        self.time_widget_to = tkw.TimeWidget(frame, 
                                  title='To', 
                                  show_header=True,
                                  lowest_time_resolution='second',
                                  callback_target=self._callback_time_widget_to, 
                                  row=r, 
                                  column=1)
        r+=1   
        
        ttk.Button(frame, text=u'Clear mark', command=self._clear_mark).grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        tkw.grid_configure(frame, nr_rows=r+1, nr_columns=2)
        
        
    #========================================================================== 
    def set_min(self, min_value):
        if type(min_value) in [str]:
            self.time_widget_from.set_time(time_string=min_value)
        else:
            self.time_widget_from.set_time(datenumber=min_value)
            
            
    #========================================================================== 
    def set_max(self, max_value):
        if type(max_value) in [str]:
            self.time_widget_to.set_time(time_string=max_value)
        else:
            self.time_widget_to.set_time(datenumber=max_value)

    #===========================================================================
    def set_valid_time_span_from_list(self, time_list):
        self.time_widget_from.set_valid_time_span_from_list(time_list)
        self.time_widget_to.set_valid_time_span_from_list(time_list)
        
    #========================================================================== 
    def _mark_min(self):
        if not self.plot_object:
            return
        self.plot_object.add_mark_range_target(1, color='r') # Should be in another place
        if self.axis in self.y_list:
            self.plot_object.mark_range_from_bottom(line_id=self.line_id) # Negative values in plot
        elif self.axis in self.x_list:
            self.plot_object.mark_range_from_left(line_id=self.line_id)
        
    #========================================================================== 
    def _mark_max(self):
        if not self.plot_object:
            return
        self.plot_object.add_mark_range_target(1, color='r') # Should be in an other place
        if self.axis in self.y_list:
            self.plot_object.mark_range_from_top(line_id=self.line_id) # Negative values in plot
        elif self.axis in self.x_list:
            self.plot_object.mark_range_from_right(line_id=self.line_id)
        
    #========================================================================== 
    def _clear_mark(self):
        if not self.plot_object:
            return
        self.plot_object.clear_all_marked()
        self.clear_widget()
#        self.plot_object.clear_marked_range()
#        self.plot_object.clear_marked_points()
#         self.reset_widget()
        
        
    #===========================================================================
    def _callback_time_widget_from(self):
        if not self.plot_object:
            return
        
        min_value = self.time_widget_from.get_time_number()
        max_value = self.time_widget_to.get_time_number()

        if min_value > max_value:
            min_value = self.time_widget_to.get_time_number()
            self.time_widget_from.set_time(datenumber=min_value)
            
            
        if self.axis in self.y_list:
            self.plot_object.set_bottom_range(min_value, 
                                           diconnect_events=True, 
                                           line_id=self.line_id)
        elif self.axis in self.x_list:
            self.plot_object.set_left_range(min_value, 
                                            diconnect_events=True, 
                                            line_id=self.line_id)
    
    #===========================================================================
    def _callback_time_widget_to(self):
        if not self.plot_object:
            return

        try:
            min_value = self.time_widget_from.get_time_number()
            max_value = self.time_widget_to.get_time_number()
        except ValueError as e:
            gui.show_warning(e.message)

        if min_value > max_value:
            max_value = self.time_widget_from.get_time_number()
            self.time_widget_to.set_time(datenumber=max_value)
            
        if self.axis in self.y_list:
            self.plot_object.set_top_range(max_value, 
                                           diconnect_events=True, 
                                           line_id=self.line_id)
        elif self.axis in self.x_list:
            self.plot_object.set_right_range(max_value, 
                                            diconnect_events=True, 
                                            line_id=self.line_id)

    #===========================================================================
    def reset_widget(self):
        self.time_widget_from.reset_widget()
        self.time_widget_to.reset_widget()

    # ===========================================================================
    def clear_widget(self):
        """
        Clears widget but keeps values.
        :return:
        """
        self.time_widget_from.clear_widget()
        self.time_widget_to.clear_widget()
        
    #===========================================================================
    def disable_widget(self):
        for children in self.winfo_children:
            children.config(state='disabled')
            
    #===========================================================================
    def enable_widget(self):
        for children in self.winfo_children:
            children.config(state='normal')

"""
================================================================================
================================================================================
================================================================================
""" 
class AxisSettingsBaseWidget(ttk.Labelframe):
    """
    Saves options for the widget and calls _set_frame. 
    """
    def __init__(self, 
                 parent, 
                 plot_object=None,
                 map_object=None,
                 callback=None, 
                 label='y-axis', 
                 prop_frame={}, 
                 show_grid=True, 
                 **kwargs):
        
        self.plot_object = plot_object
        self.map_object = map_object
        self.callback = callback
        self.show_grid = show_grid
        
        self.x_list = ['x', 't']
        self.y_list = ['y', 'z']
        
        self.prop_frame = {}
        self.prop_frame.update(prop_frame)
        
        self.grid_frame = {'padx': 5, 
                           'pady': 5, 
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)
        
        ttk.Labelframe.__init__(self, parent, text=label, **self.prop_frame)
        self.grid(**self.grid_frame)
        
        self._set_frame()
        
        
    #===========================================================================
    def update_widget(self):
        pass
        
        
    #===========================================================================
    def _toggle_grid(self):
        if not self.plot_object:
            return 
        if self.axis in self.x_list:
            # print('self.axis', self.axis, self.x_list)
            self.plot_object.set_x_grid(ax='first', grid_on=self.boolvar_grid.get())
        elif self.axis in self.y_list:
            # print('self.axis', self.axis, self.y_list)
            self.plot_object.set_y_grid(ax='first', grid_on=self.boolvar_grid.get())

  
"""
================================================================================
================================================================================
================================================================================
""" 
class AxisSettingsFloatWidget(AxisSettingsBaseWidget):
    
    def __init__(self, 
                 parent, 
                 plot_object,
                 callback=None,
                 axis='y', 
                 label='y-axis', 
                 prop_frame={}, 
                 show_grid=True, 
                 only_negative_values=False, 
                 **kwargs):
        
        self.axis = axis
        self.only_negative_values = only_negative_values
 
        AxisSettingsBaseWidget.__init__(self, 
                                        parent, 
                                        plot_object,
                                        callback=callback, 
                                        label=label, 
                                        prop_frame=prop_frame, 
                                        show_grid=show_grid, 
                                        **kwargs)
                                        
        
    #===========================================================================
    def reset_widget(self):
        self.stringvar_min.set('')
        self.stringvar_max.set('')

    def set_min_value(self, min_value):
        self.stringvar_min.set(min_value)

    def set_max_value(self, max_value):
        self.stringvar_max.set(max_value)

    def set_limits(self, min_value, max_value):
        self.set_min_value(min_value)
        self.set_max_value(max_value)
        
    #===========================================================================
    def _set_frame(self):
        """
        Updated 20180825     
        """
        padx = 5
        pady = 5
        
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, padx=padx, pady=pady, sticky='w')
        tkw.grid_configure(self)
        
        r=0
        c=0
        
        
        self.boolvar_grid = tk.BooleanVar()
        self.cbutton_grid = tk.Checkbutton(frame, text=u'Show grid', 
                                                  variable=self.boolvar_grid, 
                                                  command=self._toggle_grid)
        self.cbutton_grid.grid(row=r, column=c, columnspan=1, sticky=u'w', padx=padx, pady=pady)
        if self.show_grid:
            self.boolvar_grid.set(True)
            self._toggle_grid()
            
        # Zoom to data
        ttk.Button(frame, text='Zoom to full range', command=self._zoom_to_data).grid(row=r, column=c+2, padx=padx, pady=pady, sticky='se')
        r+=1
        
        entry_width = 10
        
        self.stringvar_min = tk.StringVar()
        self.entry_lim_min = tk.Entry(frame, textvariable=self.stringvar_min, width=entry_width)
        self.entry_lim_min.grid(row=r, column=c, sticky=u'w', padx=padx, pady=pady)
        self.stringvar_min.trace("w", lambda name, index, mode,  
                                 sv=self.stringvar_min, 
                                 en=self.entry_lim_min: tkw.check_float_entry(sv, en, only_negative_values=self.only_negative_values))
        self.entry_lim_min.bind('<Return>', self._on_return_min_range)  
        c+=1
        
        tk.Label(frame, text=u'to').grid(row=r, column=c, sticky=u'w', padx=padx, pady=pady)
        c+=1
        
        
        self.stringvar_max = tk.StringVar()
        self.entry_lim_max = tk.Entry(frame, textvariable=self.stringvar_max, width=entry_width)
        self.entry_lim_max.grid(row=r, column=c, sticky=u'w', padx=padx, pady=pady)
        self.stringvar_max.trace("w", lambda name, index, mode,  
                                 sv=self.stringvar_max, 
                                 en=self.entry_lim_max: tkw.check_float_entry(sv, en, only_negative_values=self.only_negative_values))
        self.entry_lim_max.bind('<Return>', self._on_return_max_range)

        ttk.Button(frame, text='Set range', command=self._on_return_max_range).grid(row=r, column=c + 2, padx=padx,
                                                                                    pady=pady, sticky='se')
        
        tkw.grid_configure(frame, nr_rows=r+1, nr_columns=3)
        
        
    #===========================================================================
    def _zoom_to_data(self):

        if self.axis in self.x_list:
            x_limits = True
            y_limits = False
        else:
            x_limits = False
            y_limits = True

        self.plot_object.zoom_to_data(ax='first', call_targets=False, x_limits=x_limits, y_limits=y_limits)
        
        if self.axis in self.x_list:
            min_value, max_value = self.plot_object.get_xlim(ax='first')
        elif self.axis in self.y_list:
            min_value, max_value = self.plot_object.get_ylim(ax='first')
            
        if min_value and max_value:
            if min_value < 10:
                self.stringvar_min.set('{:.1f}'.format(min_value))
            else:
                self.stringvar_min.set(str(int(min_value)))
            if max_value < 10:
                self.stringvar_max.set('{:.1f}'.format(max_value))
            else:
                self.stringvar_max.set(str(np.ceil(max_value)))
        
        self._callback()
#            self._save_limits()
#            self._set_limits_in_plot_object()

    def get_limits(self):
        return self.stringvar_min.get(), self.stringvar_max.get()
        
    #===========================================================================
    def _on_return_min_range(self, event=None):
        # Check if value is bigger than max range
        value_min_str = self.stringvar_min.get()
        value_max_str = self.stringvar_max.get()
        if not all([value_min_str, value_max_str]):
            return
        value_min = float(value_min_str)
        value_max = float(value_max_str)

        if value_max < value_min:
            self.stringvar_min.set(value_max_str)

#        self._save_limits()
        self.update_widget()
        self.entry_lim_max.focus()
        self.entry_lim_max.select_range('0', 'end')
        self._callback()
#        self._set_limits_in_plot_object()
        
    #===========================================================================
    def _on_return_max_range(self, event=None):
        # Check if value is smaller than min range
        value_min_str = self.stringvar_min.get()
        value_max_str = self.stringvar_max.get()
        if not all([value_min_str, value_max_str]):
            return
        value_min = float(value_min_str)
        value_max = float(value_max_str)

        if value_max < value_min:
            self.stringvar_max.set(value_min_str)

#        self._save_limits()
        self.update_widget()
        self.entry_lim_min.focus()
        self.entry_lim_min.select_range('0', 'end')
        self._callback()
#        self._set_limits_in_plot_object()
                
    #===========================================================================
    def _callback(self):
        
        if self.callback:
            self.callback()
        else:
            logging.info('No callback function given to AxisSettingsWidget')

"""
================================================================================
================================================================================
================================================================================
""" 
class AxisSettingsTimeWidget(AxisSettingsBaseWidget):
    """
    Updated 20180825     
    """
    def __init__(self, 
                 parent, 
                 plot_object=None, 
                 map_object=None, 
                 callback=None, 
                 axis='x', 
                 label='y-axis', 
                 prop_frame={},  
                 show_grid=True, 
                 **kwargs):
        
        self.axis = axis
        
        AxisSettingsBaseWidget.__init__(self, 
                                        parent, 
                                        plot_object=plot_object,
                                        map_object=map_object, 
                                        callback=callback, 
                                        label=label, 
                                        prop_frame=prop_frame, 
                                        show_grid=show_grid, 
                                        **kwargs)
        
    #===========================================================================
    def set_valid_time_span_from_list(self, time_list):
        self.time_widget_from.set_valid_time_span_from_list(time_list)
        self.time_widget_to.set_valid_time_span_from_list(time_list)

        
    #===========================================================================
    def reset_widget(self):
        self.time_widget_from.reset_widget()
        self.time_widget_to.reset_widget()  
        
        
    #===========================================================================
    def get_limits(self):
        return self.time_widget_from.get_time_object(), self.time_widget_to.get_time_object()
        
    def set_limits(self, min_time, max_time):
        """
        min- and max_time are of format datenumber
        :param min_time:
        :param max_time:
        :return:
        """
        if isinstance(min_time, datetime.datetime):
            self.time_widget_from.set_time(datetime_object=min_time)
            self.time_widget_to.set_time(datetime_object=max_time)
        else:
            self.time_widget_from.set_time(datenumber=min_time)
            self.time_widget_to.set_time(datenumber=max_time)


    #===========================================================================
    def _set_frame(self):
        """
        Updated 20180825     
        """
        padx = 5
        pady = 5
        
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, padx=padx, pady=pady, sticky='w')
        tkw.grid_configure(self)
        
        r=0
        if self.show_grid:
            self.boolvar_grid = tk.BooleanVar()
            self.cbutton_grid = tk.Checkbutton(frame, text=u'Show grid', 
                                                      variable=self.boolvar_grid, 
                                                      command=self._toggle_grid)
            self.cbutton_grid.grid(row=r, column=0, columnspan=3, sticky=u'w', padx=padx, pady=pady)
        
            self.boolvar_grid.set(True)
            self._toggle_grid()
            
        # Zoom to data
        ttk.Button(frame, text='Zoom to full time range', command=self._zoom_to_data).grid(row=r, column=1, sticky='se')
            
        r+=1
        
        self.time_widget_from = tkw.TimeWidget(frame, 
                                  title='From', 
                                  show_header=True,
                                  lowest_time_resolution='second',
                                  callback_target=self._callback_time_widget,
                                  row=r, 
                                  columnspan=2)
        r+=1
        
        self.time_widget_to = tkw.TimeWidget(frame, 
                                  title='To', 
                                  show_header=True,
                                  lowest_time_resolution='second',
                                  callback_target=self._callback_time_widget, 
                                  row=r, 
                                  columnspan=2)
                                  
        
        tkw.grid_configure(frame, nr_rows=r+1)
    
    
    #===========================================================================
    def _callback_time_widget(self):
        # First check so that times are in order
        time_from = self.time_widget_from.get_time_object()
        time_to = self.time_widget_to.get_time_object()
        print('*'*50)
        print('_callback_time_widget')
        print(time_from, type(time_from))
        print(time_to, type(time_to))
        if time_to < time_from:
            print('time_to < time_from')
            self.time_widget_to.set_time(datetime_object=time_from)

        if self.callback:
            self.callback()
#        self._save_limits()
#        self.update_widget()
#        self._set_limits_in_plot_object()

    #===========================================================================
    def _zoom_to_data(self):
        if self.map_object:
            self.time_widget_from.set_time(first=True)
            self.time_widget_to.set_time(last=True)
            self._callback_time_widget()
            
        elif self.plot_object:
            if self.axis in self.x_list:
                x_limits = True
                y_limits = False
            else:
                x_limits = False
                y_limits = True

            self.plot_object.zoom_to_data(ax='first', call_targets=False, x_limits=x_limits, y_limits=y_limits)
            
            if self.axis in self.x_list:
                min_value, max_value = self.plot_object.get_xlim(ax='first')
            elif self.axis in self.y_list:
                min_value, max_value = self.plot_object.get_ylim(ax='first')
                
            if min_value and max_value:
                self.time_widget_from.set_time(datenumber=min_value)
                self.time_widget_to.set_time(datenumber=max_value)
    
            self._callback_time_widget()
#            self._save_limits()
#            self._set_limits_in_plot_object()
  


"""
================================================================================
================================================================================
================================================================================
""" 
class CompareWidget(tk.Frame):
    def __init__(self, 
                 parent,
                 controller=None,
                 session=None,
                 include_sampling_depth=False,
                 include_depth=True,
                 callback=None, 
                 prop_frame={},  
                 **kwargs):

        self.prop_frame = {}
        self.prop_frame.update(prop_frame)
        self.controller = controller
        self.session = session
        self.include_sampling_depth = include_sampling_depth
        self.callback = callback
        self.include_depth = include_depth
        
        self.grid_frame = {'padx': 5, 
                           'pady': 5, 
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)
        
        tk.Frame.__init__(self, parent, **self.prop_frame)
        self.grid(**self.grid_frame)
        
        self.old_values = []
        self.new_values = []
        self.values_are_updated = True

        self.time = None
        self.dist = None
        self.depth = None
        self.sampling_depth = None
        
        self._set_frame()

        if self.include_depth:
            self.set_data(time=self.controller.user.match.setdefault('hours', '24'),
                          dist=self.controller.user.match.setdefault('dist', '5000'),
                          depth=self.controller.user.match.setdefault('depth', '2'))
        else:
            self.set_data(time=self.controller.user.match.setdefault('hours', '24'),
                          dist=self.controller.user.match.setdefault('dist', '5000'))

        
    #===========================================================================
    def _set_frame(self):
        padx=5
        pady=5
        r=0
        c=0

        self.entry = {}

        self.parameter_widget = tkw.ComboboxWidget(self,
                                                   title='Parameter',
                                                   callback_target=self._save,
                                                   row=r,
                                                   column=0,
                                                   pady=5,
                                                   sticky='w')

        r += 1
        prop_entry = dict(width=10)
        tk.Label(self, text='Max time diff [hours]:').grid(row=r, column=c, padx=padx, pady=pady, sticky='w')
        self.entry['time'] = tkw.EntryWidget(self, prop_entry=prop_entry, callback_on_change_value=self._save,
                                              entry_type='int', row=r,
                                              column=c + 1, padx=padx, pady=pady, sticky='w')

        r += 1
        tk.Label(self, text='Max distance [m]:').grid(row=r, column=c, padx=padx, pady=pady, sticky='w')
        self.entry['dist'] = tkw.EntryWidget(self, prop_entry=prop_entry, callback_on_change_value=self._save,
                                              entry_type='int', row=r,
                                              column=c + 1, padx=padx, pady=pady, sticky='w')

        if self.include_depth:
            r += 1
            tk.Label(self, text='Max depth diff [m]:').grid(row=r, column=c, padx=padx, pady=pady, sticky='w')
            self.entry['depth'] = tkw.EntryWidget(self, prop_entry=prop_entry, callback_on_change_value=self._save,
                                                  entry_type='int', row=r,
                                                  column=c + 1, padx=padx, pady=pady, sticky='w')

            # Link entries
            self.entry['time'].south_entry = self.entry['dist']
            self.entry['dist'].south_entry = self.entry['depth']
            self.entry['depth'].south_entry = self.entry['time']
        else:
            self.entry['time'].south_entry = self.entry['dist']
            self.entry['dist'].south_entry = self.entry['time']

        r += 1

        tkw.grid_configure(self, nr_rows=r, nr_columns=2)

    def update_parameter_list(self, file_id):
        parameter_list = self.session.get_parameter_list(file_id)
        default_parameter = self.controller.user.parameter_priority.get_priority(parameter_list)
        self.parameter_widget.update_items(parameter_list, default_item=default_parameter)

    def get_parameter(self):
        return self.parameter_widget.get_value()

    def get_selection(self):
        return self.new_values


    #===========================================================================
    def _save(self, entry=None):
        if self.include_depth:
            try:
                self.time = float(self.entry['time'].get_value())
                self.dist = float(self.entry['dist'].get_value())
                self.depth = float(self.entry['depth'].get_value())
            except ValueError:
                raise

            self.new_values = [self.time, self.dist, self.depth]
            if self.new_values != self.old_values:
                self.values_are_updated = True
            else:
                self.values_are_updated = False
            self.old_values = self.new_values

            # Save settings to user
            self.controller.user.match.set('hours', str(self.time))
            self.controller.user.match.set('dist', str(self.dist))
            self.controller.user.match.set('depth', str(self.depth))
        else:
            try:
                self.time = float(self.entry['time'].get_value())
                self.dist = float(self.entry['dist'].get_value())
            except ValueError:
                pass

            self.new_values = [self.time, self.dist]
            if self.new_values != self.old_values:
                self.values_are_updated = True
            else:
                self.values_are_updated = False
            self.old_values = self.new_values

            # Save settings to user
            self.controller.user.match.set('hours', str(self.time))
            self.controller.user.match.set('dist', str(self.dist))

        # Save parameter
        self.controller.user.parameter_priority.set_priority(self.get_parameter())
    
    #===========================================================================
    def set_data(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.entry:
                self.entry[key].set_value(str(int(float(value))))
        self._save()
        
"""
================================================================================
================================================================================
================================================================================
"""
class SaveWidget(ttk.LabelFrame):
    def __init__(self, 
                 parent,
                 label='',
                 include_file_name=True,
                 prop_frame={},  
                 prop_entry={},
                 callback=None,
                 user=None,
                 **kwargs):
                     
        
        self.prop_frame = {}
        self.prop_frame.update(prop_frame)
        
        self.prop_entry = {'width': 50}
        self.prop_entry.update(prop_entry)
        
        self.grid_frame = {'padx': 5, 
                           'pady': 5, 
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)
        
        ttk.LabelFrame.__init__(self, parent, text=label, **self.prop_frame)
        self.grid(**self.grid_frame)

        self.include_file_name = include_file_name
        self.callback = callback
        self.user = user
        
        self._set_frame()

        self.set_directory()
        
    #===========================================================================
    def _set_frame(self):
        padx=5
        pady=5
        
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, padx=padx, pady=pady, sticky='w')
        tkw.grid_configure(self)
        
        r=0
        c=0
        
        tk.Label(frame, text='Directory:').grid(row=r, column=c, padx=padx, pady=pady, sticky='nw')
        self.stringvar_directory = tk.StringVar()
        self.entry_directory = tk.Entry(frame, textvariable=self.stringvar_directory, **self.prop_entry)
        self.entry_directory.grid(row=r, column=c+1, padx=padx, pady=pady, sticky='nw')
        self.stringvar_directory.trace("w", lambda name, index, mode, sv=self.stringvar_directory: tkw.check_path_entry(sv))

        ttk.Button(frame, text='Get directory', command=self._get_directory).grid(row=r, column=c + 2, columnspan=2,
                                                                                  padx=padx,
                                                                                  pady=pady, sticky='se')
        r+=1

        self.stringvar_file_name = tk.StringVar()
        if self.include_file_name:
            tk.Label(frame, text='File name:').grid(row=r, column=c, padx=padx, pady=pady, sticky='nw')
            self.entry_file_name = tk.Entry(frame, textvariable=self.stringvar_file_name, **self.prop_entry)
            self.entry_file_name.grid(row=r, column=c+1, padx=padx, pady=pady, sticky='nw')
            self.stringvar_file_name.trace("w", lambda name, index, mode, sv=self.stringvar_file_name: tkw.check_path_entry(sv))
            r+=1

        ttk.Button(frame, text='Save', command=self._save_file).grid(row=r, column=c+1, columnspan=2, padx=padx, pady=pady, sticky='se')
        r += 1

        tkw.grid_configure(frame, nr_rows=r)
   
    def _get_directory(self):
        directory = tk.filedialog.askdirectory()
        if directory:
            self.stringvar_directory.set(directory)

    # ===========================================================================
    def set_directory(self, directory=None):
        if not self.user:
            return
        if directory:
            directory = directory.replace('\\', '/')
            self.user.path.set('export_directory', directory)
        else:
            directory = self.user.path.setdefault('export_directory', '')
            directory = directory.replace('\\', '/')
        self.stringvar_directory.set(directory)

    def get_directory(self):
        return self.stringvar_directory.get().strip()

    #===========================================================================
    def _save_file(self):
        if self.callback:
            directory = self.stringvar_directory.get().strip() #.replace('\\', '/')
            file_name = self.stringvar_file_name.get().strip()
            if self.user:
                self.user.path.set('export_directory', directory)
            self.callback(directory, file_name)
    
    #===========================================================================
    def set_file_path(self, file_path=None):
        if not file_path: # or os.path.exists(file_path):
            self.stringvar_directory.set('')
            self.stringvar_file_name.set('')
            self.set_directory()
            return
        directory, file_name = os.path.split(file_path)
        directory = directory.replace('\\', '/')
        self.stringvar_directory.set(directory)
        self.stringvar_file_name.set(file_name)


class SaveWidgetHTML(ttk.LabelFrame):
    def __init__(self,
                 parent,
                 user=None,
                 label='',
                 prop_frame={},
                 prop_entry={},
                 callback=None,
                 default_directory='',
                 **kwargs):

        self.prop_frame = {}
        self.prop_frame.update(prop_frame)

        self.prop_entry = {'width': 50}
        self.prop_entry.update(prop_entry)

        self.grid_frame = {'padx': 5,
                           'pady': 5,
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)

        ttk.Labelframe.__init__(self, parent, text=label, **self.prop_frame)
        self.grid(**self.grid_frame)

        self.callback = callback

        self.user = user
        self.default_directory = default_directory

        self._set_frame()

        # self._set_directory()

        # ===========================================================================

    def _set_frame(self):
        padx = 5
        pady = 5

        frame = tk.Frame(self)
        frame.grid(row=0, column=0, padx=padx, pady=pady, sticky='w')

        self.frame_parameters = tk.Frame(frame)
        # self.frame_parameters = tk.LabelFrame(frame, text='Parameters to export')
        self.frame_parameters.grid(row=0, column=0, columnspan=1, padx=padx, pady=pady, sticky='nsew')

        self.checkbutton_widget = tkw.CheckbuttonWidget(frame,
                                                      items=['Combined plot', 'Individual plots'],
                                                      pre_checked_items=[],
                                                      include_select_all=False,
                                                      colors=[],
                                                      pady=0,
                                                      row=0,
                                                      column=1)

        ttk.Button(frame, text='Export', command=self._save_file).grid(row=1, column=0, columnspan=2, padx=padx,
                                                                      pady=pady, sticky='sw')

        tkw.grid_configure(frame, nr_rows=2, nr_columns=2)

        self._set_frame_listbox_parameters()

    def _set_frame_listbox_parameters(self):

        self.listbox_widget_parameters = tkw.ListboxSelectionWidget(self.frame_parameters,
                                                                    prop_frame={},
                                                                    prop_items={'height': 4},
                                                                    prop_selected={'height': 4},
                                                                    items=[],
                                                                    selected_items=[],
                                                                    title_items='Available parameters',
                                                                    title_selected='Selected parameters',
                                                                    font=None,
                                                                    include_button_move_all_items=True,
                                                                    include_button_move_all_selected=True,
                                                                    callback_match_in_file=None,
                                                                    callback_match_subselection=None,
                                                                    sort_selected=False,
                                                                    include_blank_item=False,
                                                                    target=None,
                                                                    target_select=None,
                                                                    target_deselect=None,
                                                                    bind_tab_entry_items=None,
                                                                    widget_id=u'',
                                                                    allow_nr_selected=None,
                                                                    vertical=False)
        tkw.grid_configure(self.frame_parameters)

    # ===========================================================================
    def _save_file(self):
        if self.callback:
            self.callback()

    def get_selection(self):
        """
        Returns all selections in the widget as a dict.
        :return:
        """
        selection = dict()
        selection['parameters'] = self.listbox_widget_parameters.get_selected()
        plot_types_selected = self.checkbutton_widget.get_checked_item_list()
        selection['combined_plot'] = 'Combined plot' in plot_types_selected
        selection['individual_plots'] = 'Individual plots' in plot_types_selected
        selection['individual_maps'] = 'Individual maps' in plot_types_selected

        return selection

    def has_sufficient_selections(self):
        if self.checkbutton_widget.get_checked_item_list() and self.listbox_widget_parameters.get_selected():
            return True
        else:
            return False

    # ===========================================================================
    def _set_directory(self):
        directory = self.user.path.setdefault('html_export_directory', self.default_directory)
        directory = directory.replace('\\', '/')
        self.stringvar_directory.set(directory)

    def update_parameters(self, parameter_list=[]):
        self.listbox_widget_parameters.update_items(parameter_list)


"""
================================================================================
================================================================================
================================================================================
"""
class MovableText(object):
    """ A simple class to handle Drag n Drop.

    This is a simple example, which works for Text objects only
    """
    def __init__(self, figure=None) :
        """ Create a new drag handler and connect it to the figure's event system.
        If the figure handler is not given, the current figure is used instead
        """
        self.fig = figure
#         if figure is None : figure = p.gcf()
        # simple attibute to store the dragged text object
        self.dragged = None
        self.events = {}

        # Connect events and callbacks
#         figure.canvas.mpl_connect("pick_event", self.on_pick_event)
        self.events[u'pick_event'] = self.fig.canvas.mpl_connect('pick_event', lambda event: self.on_pick_event(event))
#         self.events[u'button_press_event'] = self.fig.canvas.mpl_connect('button_pres_event', lambda event: self.on_press_event(event)) # Have to remove saved entris too.
        self.events[u'button_release_event'] = self.fig.canvas.mpl_connect('button_release_event', lambda event: self.on_release_event(event))
#         self.events[u'motion_notify_event'] = self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.on_motion_notify_event(event))
#         figure.canvas.mpl_connect("button_release_event", self.on_release_event)
        
    def on_pick_event(self, event):
        " Store which text object was picked and were the pick event occurs."
        
#         print('on_pick_event', event.mouseevent.key 
        if isinstance(event.artist, mpl.text.Text):
            if event.mouseevent.button == 3:
                event.artist.remove()
                self.fig.canvas.draw()
                return
            self.dragged = event.artist
            self.pick_pos = (event.mouseevent.xdata, event.mouseevent.ydata)
        return True
    
    #==========================================================================
    def on_press_event(self, event):
#         print(event.button
        if event.button == 3 and self.dragged:
            self.dragged.remove()
            self.dragged = None
            self.fig.canvas.draw()
            
    #==========================================================================
    def on_release_event(self, event):
        " Update text position and redraw"
        
#         print('on_release_event'
        if self.dragged is not None :
            old_pos = self.dragged.get_position()
            new_pos = (old_pos[0] + event.xdata - self.pick_pos[0],
                       old_pos[1] + event.ydata - self.pick_pos[1])
            self.dragged.set_position(new_pos)
            self.dragged = None
            self.fig.canvas.draw()
        return True
    
    #==========================================================================
    def on_motion_notify_event(self, event):
        " Update text position and redraw"
        
        if self.dragged is not None :
            print('on_motion_notify_event')
            old_pos = self.dragged.get_position()
            new_pos = (old_pos[0] + event.xdata - self.pick_pos[0],
                       old_pos[1] + event.ydata - self.pick_pos[1])
            self.dragged.set_position(new_pos)
            self.fig.canvas.draw()
        return True
    
    #==========================================================================
    def disconnect(self):
        for event in self.events:
            self.fig.canvas.mpl_disconnect(event)
        self.events = {}


class InformationPopup(object):
    """
    Handles information popups to user.
    """
    def __init__(self, controller):
        self.controller = controller
        self.user = self.controller.user

    def show_information(self, text=''):

        if not self.user.options.setdefault('show_info_popups', True):
            return

        padx = 5
        pady = 5

        self.popup_frame = tk.Toplevel(self.controller)
        x = self.controller.winfo_x()
        y = self.controller.winfo_y()

        # Set text
        # text = self._format_text(text)
        self.label = tk.Label(self.popup_frame, text=text)
        self.label.grid(row=0, column=0, columnspan=2, padx=padx, pady=pady)
        self.label.bind('<Configure>', self._update_wrap)

        button_ok = tk.Button(self.popup_frame, text='Great tip!\nKeep them coming!', command=self._ok)
        button_ok.grid(row=1, column=0, padx=padx, pady=pady)

        button_ok_and_forget = tk.Button(self.popup_frame, text="Thanks,\nbut I don't need tips anymore!", command=self._ok_and_forget)
        button_ok_and_forget.grid(row=1, column=1, padx=padx, pady=pady)

        tkw.grid_configure(self.popup_frame, nr_columns=2, nr_rows=2)

        self.popup_frame.update_idletasks()

        root_dx = self.controller.winfo_width()
        root_dy = self.controller.winfo_height()

        dx = int(root_dx/3)
        dy = int(root_dy/3)
        w = self.popup_frame.winfo_width()
        h = self.popup_frame.winfo_height()
        self.popup_frame.geometry("%dx%d+%d+%d" % (w, h, x + dx, y + dy))
        # self.controller.withdraw()

    def _ok(self):
        self.popup_frame.destroy()
        # self.controller.deiconify()
        self.controller.update_all()

    def _ok_and_forget(self):
        self.user.options.set('show_info_popups', False)
        self.popup_frame.destroy()
        # self.controller.deiconify()
        self.controller.update_all()

    def _update_wrap(self, event):
        self.label.config(wraplength=self.popup_frame.winfo_width())

    def _format_text(self, text):
        nr_signs_per_row = 10
        split_text = text.split()
        text_lines = []
        line = ''
        for word in split_text:
            line = '{} {}'.format(line, word)
            if len(line) > nr_signs_per_row:
                text_lines.append(line)
                line = ''
        if line:
            text_lines.append(line)
        return '\n'.join(text_lines)

class EntryPopup(object):
    """
    Handles popop for an entry.
    """
    def __init__(self, controller, text=''):
        self.controller = controller
        self.user = self.controller.user
        self.text = text

    def display(self):
        padx = 5
        pady = 5

        self.popup_frame = tk.Toplevel(self.controller)
        x = self.controller.winfo_x()
        y = self.controller.winfo_y()

        # Set text
        self.label = tk.Label(self.popup_frame, text=self.text)
        self.label.grid(row=0, column=0, columnspan=2, padx=padx, pady=pady)

        self.entry = tkw.EntryWidget(self.popup_frame, entry_type='int')

        button_ok = tk.Button(self.popup_frame, text='Ok', command=self._ok)
        button_ok.grid(row=1, column=0, padx=padx, pady=pady)

        tkw.grid_configure(self.popup_frame, nr_columns=2, nr_rows=2)

        self.popup_frame.update_idletasks()

        root_dx = self.controller.winfo_width()
        root_dy = self.controller.winfo_height()

        dx = int(root_dx/3)
        dy = int(root_dy/3)
        w = self.popup_frame.winfo_width()
        h = self.popup_frame.winfo_height()
        self.popup_frame.geometry("%dx%d+%d+%d" % (w, h, x + dx, y + dy))
        # self.controller.withdraw()

    def _ok(self):
        if self.entry.get_value():
            self.popup_frame.destroy()
        # self.controller.deiconify()


class FilterPopup(object):
    """
    Handles popup for filter widget.
    """
    def __init__(self,
                 parent,
                 controller,
                 session=None,
                 callback_target=None):
        self.parent = parent
        self.controller = controller
        self.session = session
        self.user = self.controller.user
        self.callback_target = callback_target
        self.popup_frame = None

    def display(self):

        if self.popup_frame:
            self.popup_frame.tkraise()
            return
        padx = 5
        pady = 5

        self.popup_frame = tk.Toplevel(self.parent)
        self.popup_frame.withdraw()

        # Set filter frame
        self.filter_widget = FilterWidgetSelection(self.popup_frame,
                                                    user=self.user,
                                                    # controller=None,
                                                    session=self.session,
                                                    callback=None,
                                                    prop_frame={},
                                                    padx=padx,
                                                    pady=pady,
                                                    columnspan=2)

        button_ok = tk.Button(self.popup_frame, text='Save filter', command=self._ok)
        button_ok.grid(row=1, column=0, padx=padx, pady=pady)

        button_cancel = tk.Button(self.popup_frame, text='Cancel', command=self._exit)
        button_cancel.grid(row=1, column=1, padx=padx, pady=pady)

        tkw.grid_configure(self.popup_frame, nr_rows=2, nr_columns=2, r0=10)

        self.popup_frame.update_idletasks()

        root_position = self.controller.get_root_window_position()
        w = self.popup_frame.winfo_width()
        h = self.popup_frame.winfo_height()

        x = root_position['x']
        y = root_position['y']

        dx = abs(int(root_position['w']/4))
        dy = abs(int(root_position['h']/4))

        self.popup_frame.geometry("%dx%d+%d+%d" % (w, h, x + dx, y + dy))
        self.popup_frame.update_idletasks()
        self.popup_frame.tkraise()
        self.popup_frame.deiconify()

        self.popup_frame.protocol('WM_DELETE_WINDOW', self._exit)

        tk.Tk.wm_title(self.popup_frame, 'Filter for user: {}'.format(self.user.name))

        self.popup_frame.update_idletasks()
        self.popup_frame.deiconify()

        self.popup_frame.grab_set()

    def _reset_filter(self):
        if self.filter_popup:
            self.controller.user.filter.reset()
            self.callback_target(update=True)

    def _ok(self):
        old_filter = self.user.filter.get_settings()
        filter_dict = self.filter_widget.get_filter()
        # print('=' * 20)
        # print('FILTER DICT')
        # for key in sorted(filter_dict):
        #     print(key, type(filter_dict[key]), filter_dict[key])
        # print('=' * 20)



        if filter_dict == old_filter:
            print('Unchanged filter. Will not save filter to user!')
            self._exit()
        else:
            # Save to user
            for key, value in filter_dict.items():
                # print('Saving FILTER', key, type(value), value)
                self.user.filter.set(key, value, save=False)
            self.user.filter.save()
            self._exit(update=True)

    def _exit(self, **kwargs):
        """
        :type kwargs: object
        """
        # Save tab selection
        tab_name = self.filter_widget.notebook.get_selcted_tab()
        self.user.focus.set('filter_notebook_tab', tab_name)

        self.popup_frame.destroy()
        self.popup_frame = None
        if self.callback_target:
            self.callback_target(**kwargs)


class QCroutineOptionsPopup(object):
    """
    Handles popup for qc options widget.
    """
    def __init__(self,
                 parent,
                 controller,
                 session=None,
                 qc_routine=None,
                 callback_target=None):
        self.parent = parent
        self.controller = controller
        self.session = session
        self.qc_routine = qc_routine
        self.user = self.controller.user
        self.callback_target = callback_target
        self.popup_frame = None

        self.title = 'Options for QC routine: {}'.format(self.qc_routine)

    def display(self):

        if self.popup_frame:
            self.popup_frame.tkraise()
            return
        padx = 15
        pady = 15

        self.popup_frame = tk.Toplevel(self.parent)
        self.popup_frame.withdraw()

        self.label_title = tk.Label(self.popup_frame, text=self.title, font=('bold', 20))
        self.label_title.grid(row=0, column=0, padx=padx, pady=pady,)

        # Set filter frame
        self.option_widget = QCroutineOptionsWidget(self.popup_frame,
                                                    user=self.user,
                                                    session=self.session,
                                                    controller=self.controller,
                                                    qc_routine=self.qc_routine,
                                                    callback=None,
                                                    prop_frame={},
                                                    padx=padx,
                                                    pady=pady,
                                                    columnspan=2,
                                                    row=1)

        button_ok = tk.Button(self.popup_frame, text='Save options', command=self._ok)
        button_ok.grid(row=2, column=0, padx=padx, pady=pady)

        button_cancel = tk.Button(self.popup_frame, text='Cancel', command=self._exit)
        button_cancel.grid(row=2, column=1, padx=padx, pady=pady)

        tkw.grid_configure(self.popup_frame, nr_rows=3, nr_columns=2, r0=10)

        self.popup_frame.update_idletasks()

        root_position = self.controller.get_root_window_position()
        w = self.popup_frame.winfo_width()
        h = self.popup_frame.winfo_height()

        x = root_position['x']
        y = root_position['y']

        dx = abs(int(root_position['w']/4))
        dy = abs(int(root_position['h']/4))

        self.popup_frame.geometry("%dx%d+%d+%d" % (w, h, x + dx, y + dy))

        self.popup_frame.protocol('WM_DELETE_WINDOW', self._exit)

        tk.Tk.wm_title(self.popup_frame, self.title)

        self.popup_frame.grab_set()

        self.popup_frame.update_idletasks()
        self.popup_frame.deiconify()

        self._save_options()

    def _ok(self):
        old_options = self.user.qc_routine_options.get_settings().get(self.qc_routine)
        options_dict = self.option_widget.get_options()

        if options_dict == old_options:
            self._exit()
        else:
            self._save_options()
            self._exit(update=True)
            gui_logger.info('Options saved for qc_routine {}'.format(self.qc_routine))

    def _save_options(self):
        # Save to user
        options_dict = self.option_widget.get_options()
        for key, value in options_dict.items():
            if 'gismo' in key.lower() and 'version' in key.lower():
                # Dont save gismo version
                continue
            elif 'save' in key.lower() and 'directory' in key.lower():
                # Saved in different user settings
                self.user.directory.set('save_directory_qc', value)
                # self.user.qc_routine_options.set(self.qc_routine, key, value)
                continue
            self.user.qc_routine_options.set(self.qc_routine, key, value)

    def _exit(self, event=None, **kwargs):
        """
        :type kwargs: object
        """
        self.popup_frame.destroy()
        self.popup_frame = None
        if self.callback_target:
            self.callback_target(**kwargs)


class FilterWidgetTable(tk.Frame):
    """
    Widget contains
    """
    def __init__(self,
                 parent,
                 controller=None,
                 session=None,
                 callback_update=None,
                 callback_select=None,
                 prop_frame={},
                 file_id_startswith='',
                 **kwargs):
        self.prop_frame = {}
        self.prop_frame.update(prop_frame)
        self.parent = parent
        self.controller = controller
        self.session = session
        self.callback_update = callback_update
        self.callback_select = callback_select

        self.file_id_startswith = file_id_startswith

        self.grid_frame = {'padx': 5,
                           'pady': 5,
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)

        tk.Frame.__init__(self, parent, **self.prop_frame)
        self.grid(**self.grid_frame)

        self.columns = ['File ID', 'Station', 'Time']

        self.filter_popup = None

        self._set_frame()

    def _get_current_user(self):
        return self.controller.user

    def _set_frame(self):
        pad = {'padx': 5,
               'pady': 5}
        # ----------------------------------------------------------------------

        self.table_widget = tkw.TableWidget(self,
                                            columns=self.columns,
                                            callback_select=self._callback_table_select,
                                            callback_rightclick=self._filter_data,
                                            row=0,
                                            sticky='nsew',
                                            columnspan=3,
                                            **pad)

        self.button_filter_data = tk.Button(self,
                                            text='Show filter',
                                            command=self._filter_data)
        self.button_filter_data.grid(row=1, column=0, sticky='nw', **pad)

        self.button_reset_filter = tk.Button(self,
                                            text='Reset filter',
                                            command=self._reset_filter)
        self.button_reset_filter.grid(row=1, column=1, sticky='nw', **pad)

        self.stringvar_info = tk.StringVar()
        self.label_info = tk.Label(self, textvariable=self.stringvar_info)
        self.label_info.grid(row=1, column=2, sticky='nw', **pad)

        self.bg_color = self.label_info.cget("background")

        tkw.grid_configure(self, nr_rows=2, nr_columns=3, r0=10)

    def _filter_data(self):
        if self.filter_popup:
            self.filter_popup.display()
            return
        if not self.session.get_filtered_file_id_list(startswith=self.file_id_startswith):
            gui.show_information('No files loaded', 'No files loaded for this sampling type.')
            return
        self.filter_popup = gui.widgets.FilterPopup(self,
                                                    controller=self.controller,
                                                    callback_target=self._callback_filter_data,
                                                    session=self.session)
        self.filter_popup.display()

    def _reset_filter(self):
        if self.filter_popup:
            self.filter_popup.destroy()
        self.controller.user.filter.reset()
        self._callback_filter_data(update=True)

    def _callback_filter_data(self, **kwargs):
        if not kwargs.get('update', False):
            self.filter_popup = None
            return

        user = self._get_current_user()
        user_filter = user.filter.get_settings()
        self.table_widget.reset_table()
        user_filter['startswith'] = self.file_id_startswith

        # # Check time string and convert to datetime
        # for key, value in user_filter.items():
        #     if 'time' in key:
        #         # print(user.name)
        #         # print(key, type(value), value)
        #         try:
        #             user_filter[key] = datetime.datetime.strptime(value, '%Y%m%d%H%M%S')
        #         except:
        #             pass

        filtered_file_id_list = self.session.get_filtered_file_id_list(**user_filter)
        # print('filtered_file_id_list'.upper(), filtered_file_id_list)

        if not filtered_file_id_list:
            self.filter_popup = None
            return
        data = []
        for file_id in filtered_file_id_list:
            data_line = []
            # File id
            data_line.append(file_id)
            gismo_object = self.session.get_gismo_object(file_id)
            # Station name
            data_line.append(gismo_object.get_station_name())
            # Time
            t = pd.to_datetime(str(gismo_object.get_time()[0]))
            data_line.append(t.strftime('%Y-%m-%d %H:%M'))
            data.append(data_line)

        self.table_widget.set_table(data)

        self.filter_popup = None

        # Check if filter is set
        if sorted(self.session.get_filtered_file_id_list(startswith=self.file_id_startswith)) == sorted(filtered_file_id_list):
            # self.button_filter_data.config(bg='green')
            self.stringvar_info.set('Filter is not set')
            self.label_info.config(bg=self.bg_color)
        else:
            # self.button_filter_data.config(bg='red')
            self.stringvar_info.set('Filter is active')
            self.label_info.config(bg='pink')

        if self.callback_update:
            self.callback_update(**kwargs)

    def _callback_table_select(self, **kwargs):
        if self.callback_select:
            self.callback_select(**self.get_selected())

    def get_selected(self):
        return self.table_widget.get_selected()

    def get_filtered_file_id_list(self):
        filtered_items = self.table_widget.get_filtered_items()
        return [item['File ID'] for item in filtered_items]

    def update_widget(self, **kwargs):
        """
        Should be called when self.session is updated.
        :return:
        """
        self._callback_filter_data(update=True, **kwargs)


class FilterWidgetSelection(tk.Frame):
    """
    Handles a pop up with
    """

    def __init__(self,
                 parent,
                 user=None,
                 # controller=None,
                 session=None,
                 callback=None,
                 prop_frame={},
                 **kwargs):
        self.prop_frame = {}
        self.prop_frame.update(prop_frame)
        # self.controller = controller
        self.session = session
        self.user = user
        self.callback = callback

        self.grid_frame = {'padx': 5,
                           'pady': 5,
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)

        tk.Frame.__init__(self, parent, **self.prop_frame)
        self.grid(**self.grid_frame)

        self._set_frame()

        self._add_data_to_map_widgets()
        self._add_data_to_station_widgets()
        self._add_data_to_time_widgets()

    def _get_map_boundaries(self):
        boundaries = [self.user.map_boundries.setdefault('lon_min', 9),
                      self.user.map_boundries.setdefault('lon_max', 31),
                      self.user.map_boundries.setdefault('lat_min', 53),
                      self.user.map_boundries.setdefault('lat_max', 66)]
        return boundaries

    def _set_frame(self):
        grid = {'padx': 5,
                'pady': 5,
                'sticky': 'nsew'}

        self.notebook = tkw.NotebookWidget(self, frames=['Spatial filter', 'Time filter'], **grid)
        tkw.grid_configure(self)
        # Focus tab
        tab_name = self.user.focus.get('filter_notebook_tab')
        if tab_name:
            self.notebook.select_frame(tab_name)

        self.labelframe_map = tk.LabelFrame(self.notebook.frame_spatial_filter, text='Zoom map to filter')
        self.labelframe_map.grid(row=0, column=0, rowspan=2, **grid)

        self.labelframe_station = tk.LabelFrame(self.notebook.frame_spatial_filter, text='Filter on station')
        self.labelframe_station.grid(row=0, column=1, **grid)
        tkw.grid_configure(self.notebook.frame_spatial_filter, nr_columns=2)

        self.labelframe_time = tk.LabelFrame(self.notebook.frame_time_filter, text='Filter on time')
        self.labelframe_time.grid(row=0, column=0, **grid)
        self.labelframe_season = tk.LabelFrame(self.notebook.frame_time_filter, text='Filter on season')
        self.labelframe_season.grid(row=1, column=0, **grid)
        tkw.grid_configure(self.notebook.frame_time_filter, nr_rows=2)

        # Map
        boundaries = self._get_map_boundaries()
        self.map_widget = tkmap.TkMap(self.labelframe_map,
                                      map_resolution='l',
                                      boundaries=boundaries,
                                      toolbar=True,
                                      figsize=(8, 6))
        tkw.grid_configure(self.labelframe_map)

        # Station
        prop = {'width': 40}
        self.station_widget = tkw.ListboxSelectionWidget(self.labelframe_station,
                                                         prop_items=prop,
                                                         prop_selected=prop)
        tkw.grid_configure(self.labelframe_station)

        # Time
        prop_combobox = {'width': 20}
        self.from_time_widget = tkw.TimeWidget(self.labelframe_time,
                                               title='From',
                                               lowest_time_resolution='minute',
                                               show_header=True,
                                               prop_combobox=prop_combobox,
                                               row=0,
                                               sticky='nw')

        self.to_time_widget = tkw.TimeWidget(self.labelframe_time,
                                             title='To',
                                             lowest_time_resolution='minute',
                                             show_header=True,
                                             prop_combobox=prop_combobox,
                                             row=1,
                                             sticky='nw')
        tkw.grid_configure(self.labelframe_time, nr_rows=2)

        # Season
        self.season_widget = tkw.TimeWidgetSeason(self.labelframe_season)
        tkw.grid_configure(self.labelframe_season)


    def _add_data_to_map_widgets(self):
        gui.plot_map_background_data(map_widget=self.map_widget,
                                     session=self.session,
                                     user=self.user)

        self.map_widget.zoom(**self.user.filter.get_settings())

    def _add_data_to_station_widgets(self):
        station_list = self.session.get_station_list()

        # Add stations
        self.station_widget.update_items(station_list)

        # Select stations from user filter
        user_station_list = self.user.filter.get('stations')
        if user_station_list:
            self.station_widget.move_items_to_selected(user_station_list)

    def _add_data_to_time_widgets(self):
        file_id_list = self.session.get_file_id_list()
        if not file_id_list:
            return

        time_list = []
        for file_id in file_id_list:
            time_list.extend(self.session.get_gismo_object(file_id).get_time())

        self.from_time_widget.set_valid_time_span_from_list(time_list)
        self.to_time_widget.set_valid_time_span_from_list(time_list)

        # From time
        user_time_from = self.user.filter.get('time_from')
        if user_time_from:
            self.from_time_widget.set_time(datetime_object=user_time_from)
        else:
            self.from_time_widget.set_time(first=True)

        # To time
        user_time_to = self.user.filter.get('time_to')
        if user_time_to:
            self.to_time_widget.set_time(datetime_object=user_time_to)
        else:
            self.to_time_widget.set_time(last=True)

        # Season
        season = self.user.filter.get('season')
        if season:
            self.season_widget.set_value(**season)
        else:
            self.season_widget.reset_widget()


            # print('user_time_from'.upper(), type(user_time_from), user_time_from)
        # print('user_time_to'.upper(), type(user_time_to), user_time_to)
        #
        # # Need to convert to string here. Dont know why I get datetime object here
        # # if type(user_time_from) == datetime.datetime:
        # #     user_time_from = user_time_from.strftime('%Y%m%d%H%M%S')
        # # if type(user_time_to) == datetime.datetime:
        # #     user_time_to = user_time_to.strftime('%Y%m%d%H%M%S')
        #
        # if not user_time_from:
        #     user_time_from = pd.to_datetime(min(time_list)).strftime('%Y%m%d%H%M%S')
        # if not user_time_to:
        #     user_time_to = pd.to_datetime(max(time_list)).strftime('%Y%m%d%H%M%S')
        #
        # print('TIME FROM', type(user_time_from), user_time_from)
        # print('TIME TO', type(user_time_to), user_time_to)
        # self.from_time_widget.set_time(time_string=user_time_from)
        # self.to_time_widget.set_time(time_string=user_time_to)


    def get_filter(self):
        filter_dict = {}

        # Map
        map_limits = self.map_widget.get_map_limits()
        filter_dict.update(map_limits)

        # Stations
        filter_dict['stations'] = self.station_widget.get_selected()

        # Time
        filter_dict['time_from'] = self.from_time_widget.get_time_object()
        filter_dict['time_to'] = self.to_time_widget.get_time_object()

        # Season
        filter_dict['season'] = self.season_widget.get_value()

        # print('filter_dict', filter_dict)
        return filter_dict

class QCroutineOptionsWidget(tk.Frame):
    """
    Handles a pop up with
    """

    def __init__(self,
                 parent,
                 user=None,
                 session=None,
                 controller=None,
                 callback=None,
                 qc_routine=None,
                 prop_frame={},
                 **kwargs):
        self.prop_frame = {}
        self.prop_frame.update(prop_frame)
        self.controller = controller
        self.session = session
        self.user = user
        self.callback = callback
        self.qc_routine = qc_routine

        self.grid_frame = {'padx': 5,
                           'pady': 5,
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)

        tk.Frame.__init__(self, parent, **self.prop_frame)
        self.grid(**self.grid_frame)

        self._set_frame()

    def _set_frame(self):
        grid = {'padx': 10,
                'pady': 10,
                'sticky': 'nsew'}

        self.options = self.session.get_qc_routine_options(self.qc_routine)

        self.labelframes = {}
        self.widgets = {}
        r=0
        c=0
        for key in sorted(self.options):
            value = self.options.get(key)
            frame = tk.LabelFrame(self, text=key)
            frame.grid(row=r, column=c, sticky='nsew')
            self.labelframes[key] = frame

            if 'directory' in key:
                self.widgets[key] = tkw.DirectoryWidget(frame,
                                                        include_default_button=True,
                                                        row=r)
            elif value == str or type(value) == str:
                self.widgets[key] = tkw.EntryWidget(frame, entry_type='path', row=r)
                if value == str:
                    self.widgets[key].set_value(self.user.qc_routine_options.setdefault(self.qc_routine, key, ''))
                elif type(value) == str:
                    self.widgets[key].set_value(self.user.qc_routine_options.setdefault(self.qc_routine, key, value))
                self.widgets[key].set_value(self.user.qc_routine_options.setdefault(self.qc_routine, key, ''))
            elif value == float or type(value) == float:
                self.widgets[key] = tkw.EntryWidget(frame, entry_type='float', row=r)
                if value == float:
                    self.widgets[key].set_value(self.user.qc_routine_options.setdefault(self.qc_routine, key, None))
                elif type(value) == float:
                    self.widgets[key].set_value(self.user.qc_routine_options.setdefault(self.qc_routine, key, value))
            elif value == int or type(value) == int:
                self.widgets[key] = tkw.EntryWidget(frame, entry_type='int', row=r)
                if value == int:
                    self.widgets[key].set_value(self.user.qc_routine_options.setdefault(self.qc_routine, key, None))
                elif type(value) == int:
                    self.widgets[key].set_value(self.user.qc_routine_options.setdefault(self.qc_routine, key, value))
                self.widgets[key].set_value(self.user.qc_routine_options.setdefault(self.qc_routine, key, None))
            elif type(value) == tuple:
                self.widgets[key] = tkw.RadiobuttonWidget(frame, items=value, row=r)
                self.widgets[key].set_value(self.user.qc_routine_options.setdefault(self.qc_routine, key, ''))
            elif type(value) == list:
                if len(value) <= 5:
                    self.widgets[key] = tkw.CheckbuttonWidget(frame, items=value, include_select_all=False)
                else:
                    self.widgets[key] = tkw.ListboxSelectionWidget(frame, items=value, row=r)
                self.widgets[key].set_value(self.user.qc_routine_options.setdefault(self.qc_routine, key, value))

            # Set default
            if key.lower() == 'user':
                self.widgets[key].set_value(self.user.name)
                self.user.qc_routine_options.set(self.qc_routine, key, self.user.name)
                self.widgets[key].deactivate()
            elif 'gismo' in key.lower() and 'version' in key.lower():
                self.widgets[key].set_value(self.controller.version)
                self.user.qc_routine_options.set(self.qc_routine, key, self.controller.version)
                self.widgets[key].deactivate()
            elif 'save' in key.lower() and 'directory' in key.lower():
                default_directory = os.path.join(self.controller.settings['directory']['Export directory'])
                self.widgets[key].default_directory = default_directory
                self.widgets[key].set_value(self.user.path.setdefault('save_directory_qc', default_directory))

            r+=1
        tkw.grid_configure(self, nr_rows=r)


    def get_options(self):
        options_dict = {}
        for key in sorted(self.options):
            options_dict[key] = self.widgets[key].get_value()
        print('options_dict', options_dict)
        return options_dict


class QCroutineWidget(tk.Frame):
    """
    Widget to show and and handle qc routines and their options.
    """
    def __init__(self,
                 parent,
                 controller=None,
                 session=None,
                 prop_frame={},
                 **kwargs):

        self.prop_frame = {}
        self.prop_frame.update(prop_frame)

        self.controller = controller
        self.session = session

        self.grid_frame = {'padx': 2,
                           'pady': 2,
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)

        tk.Frame.__init__(self, parent, **self.prop_frame)
        self.grid(**self.grid_frame)

        self.qc_routines = self.session.get_qc_routines()

        self._set_frame()

    def _set_frame(self):
        grid = {'padx': 5,
                'pady': 5,
                'sticky': 'nw'}

        self.qc_routine_widgets = {}
        r = 0
        for qc_routine in self.qc_routines:
            self.qc_routine_widgets[qc_routine] = QCroutineWidgetSingle(self,
                                                                        controller=self.controller,
                                                                        qc_routine=qc_routine,
                                                                        session=self.session,
                                                                        row=r,
                                                                        **grid)
            r+=1
        tkw.grid_configure(self, nr_rows=r)

    def update_widget(self, file_id_list):
        if type(file_id_list) == str:
            file_id_list = [file_id_list]
        qc_routine_list = []
        for file_id in file_id_list:
            gismo_object = self.session.get_gismo_object(file_id)
            qc_routine_list.extend(gismo_object.valid_qc_routines)
        for qc_routine in self.qc_routines:
            if qc_routine in qc_routine_list:
                self.qc_routine_widgets[qc_routine].activate()
            else:
                self.qc_routine_widgets[qc_routine].deactivate()

    def get_selected_qc_routines(self):
        return sorted([qc_routine for qc_routine in self.qc_routines if self.qc_routine_widgets[qc_routine].is_selected()])


class QCroutineWidgetSingle(tk.Frame):
    """
    Widget to show and select(deselect a qc routine. Widget incldes option popup frame.
    """
    def __init__(self,
                 parent,
                 controller=None,
                 qc_routine='',
                 session=None,
                 prop_frame={},
                 **kwargs):

        self.prop_frame = {}
        self.prop_frame.update(prop_frame)

        self.controller = controller
        self.qc_routine = qc_routine
        self.session = session

        self.grid_frame = {'padx': 2,
                           'pady': 2,
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)

        tk.Frame.__init__(self, parent, **self.prop_frame)
        self.grid(**self.grid_frame)

        self._set_frame()

    def _set_frame(self):
        grid = {'padx': 5,
                'pady': 5,
                'sticky': 'w'}

        self.options_image = tk.PhotoImage(
            file=os.path.join(self.controller.app_directory, 'system/pic/options_icon2.gif'))
        self.options_label = tk.Label(self, image=self.options_image, cursor="hand2")
        self.options_label.grid(row=0, column=0, **grid)
        self.options_label.bind("<Button-1>", self._on_click_options)
        self.widget_is_active = True

        #self.button_options = tk.Button(self, text='Options', command=self._on_click_options)
        #self.button_options.grid(row=0, column=0, **grid)

        self.booleanvar = tk.BooleanVar()
        self.checkbutton = tk.Checkbutton(self,
                                          text=self.qc_routine,
                                          variable=self.booleanvar)
        self.checkbutton.grid(row=0, column=1, **grid)

        tkw.grid_configure(self, nr_columns=2)

        self.deactivate()

    def _on_click_options(self, event=None):
        if not self.widget_is_active:
            return
        self.popup_widget = QCroutineOptionsPopup(self,
                                                  self.controller,
                                                  session=self.session,
                                                  qc_routine=self.qc_routine,
                                                  callback_target=self._callback_popup)
        self.popup_widget.display()

    def _callback_popup(self, **kwargs):
        pass

    def deactivate(self):
        self.widget_is_active = False
        self.booleanvar.set(False)
        self.checkbutton.config(state='disabled')

    def activate(self):
        self.widget_is_active = True
        self.checkbutton.config(state='normal')

    def is_selected(self):
        return self.booleanvar.get()


def show_information(title, message):
    messagebox.showinfo(title, message)


def show_warning(title, message):
    messagebox.showwarning(title, message)


def show_error(title, message):
    messagebox.showerror(title, message)

