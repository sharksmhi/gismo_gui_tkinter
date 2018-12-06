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

import os
import numpy as np
#import shutil


#import gtb_core
#import gtb_gui
#import gtb_lib
#import gtb_utils

import libs.sharkpylib.tklib.tkinter_widgets as tkw

import logging 

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
        
            
        ttk.Button(frame, text=u'Clear mark', command=self._clear_mark).grid(row=r, column=1, padx=padx, pady=pady, sticky='w')
        
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
                                  callback_target=self._callback_time_widget_from, 
                                  row=r, 
                                  column=1)
        r+=1  
        
        #-----------------------------------------------------------------------------------------------------------
        ttk.Button(frame, text=u'Mark to', command=self._mark_max).grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        self.time_widget_to = tkw.TimeWidget(frame, 
                                  title='To', 
                                  show_header=True, 
                                  callback_target=self._callback_time_widget_to, 
                                  row=r, 
                                  column=1)
        r+=1   
        
        ttk.Button(frame, text=u'Clear mark', command=self._clear_mark).grid(row=r, column=1, padx=padx, pady=pady, sticky='w')
        
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
        
        min_value = self.time_widget_from.get_time_number()
        max_value = self.time_widget_to.get_time_number()

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
        ttk.Button(frame, text=u'Zoom to data', command=self._zoom_to_data).grid(row=r, column=c+2, padx=padx, pady=pady, sticky='se')
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
        
        tkw.grid_configure(frame, nr_rows=r+1, nr_columns=3)
        
        
    #===========================================================================
    def _zoom_to_data(self):
        
        self.plot_object.zoom_to_data(ax='first', call_targets=False)
        
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
    def _on_return_min_range(self, event):
#        self._save_limits()
        self.update_widget()
        self.entry_lim_max.focus()
        self.entry_lim_max.select_range('0', 'end')
        self._callback()
#        self._set_limits_in_plot_object()
        
    #===========================================================================
    def _on_return_max_range(self, event):
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
        ttk.Button(frame, text=u'Zoom to data', command=self._zoom_to_data).grid(row=r, column=1, sticky='se')
            
        r+=1
        
        self.time_widget_from = tkw.TimeWidget(frame, 
                                  title='From', 
                                  show_header=True, 
                                  callback_target=self._callback_time_widget,
                                  row=r, 
                                  columnspan=2)
        r+=1
        
        self.time_widget_to = tkw.TimeWidget(frame, 
                                  title='To', 
                                  show_header=True, 
                                  callback_target=self._callback_time_widget, 
                                  row=r, 
                                  columnspan=2)
                                  
        
        tkw.grid_configure(frame, nr_rows=r+1)
    
    
    #===========================================================================
    def _callback_time_widget(self):
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
            self.plot_object.zoom_to_data(ax='first', call_targets=False)
            
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
                 session=None,
                 user=None,
                 include_sampling_depth=False,
                 callback=None, 
                 prop_frame={},  
                 **kwargs):

        self.prop_frame = {}
        self.prop_frame.update(prop_frame)
        self.session = session
        self.user = user
        self.include_sampling_depth = include_sampling_depth
        self.callback = callback
        
        self.grid_frame = {'padx': 5, 
                           'pady': 5, 
                           'sticky': 'nsew'}
        self.grid_frame.update(kwargs)
        
        tk.Frame.__init__(self, parent, **self.prop_frame)
        self.grid(**self.grid_frame)
        
        self.old_values = ''
        self.new_values = ''

        self.time = None
        self.dist = None
        self.depth = None
        self.sampling_depth = None
        
        self._set_frame()

        self.set_data(time=self.user.match.setdefault('hours', '24'),
                      dist=self.user.match.setdefault('dist', '5000'),
                      depth=self.user.match.setdefault('depth', '2'))
        
    #===========================================================================
    def _set_frame(self):
        padx=5
        pady=5
        r=0
        c=0
        
        self.stringvar = {}
        self.entry = {}

        if self.include_sampling_depth:
            # Typically used when no depth is given for fixed platform
            tk.Label(self, text='Sampling depth:').grid(row=r, column=c, padx=padx, pady=pady, sticky='w')
            self.stringvar['sampling_depth'] = tk.StringVar()
            self.entry['sampling_depth'] = tk.Entry(self, textvariable=self.stringvar['sampling_depth'], width=40)
            self.entry['sampling_depth'].grid(row=r, column=c + 1, padx=padx, pady=pady, sticky='w')
            self.stringvar['sampling_depth'].trace("w",
                                         lambda name, index, mode, sv=self.stringvar['sampling_depth']: tkw.check_int_entry(sv))
            r += 1
        
        tk.Label(self, text='Max time diff [hours]:').grid(row=r, column=c, padx=padx, pady=pady, sticky='w')
        self.stringvar['time'] = tk.StringVar()
        self.entry['time'] = tk.Entry(self, textvariable=self.stringvar['time'], width=40)
        self.entry['time'].grid(row=r, column=c+1, padx=padx, pady=pady, sticky='w')
        self.stringvar['time'].trace("w", lambda name, index, mode, sv=self.stringvar['time']: tkw.check_int_entry(sv))
        r+=1
        
        tk.Label(self, text='Max distance [m]:').grid(row=r, column=c, padx=padx, pady=pady, sticky='w')
        self.stringvar['dist'] = tk.StringVar()
        self.entry['dist'] = tk.Entry(self, textvariable=self.stringvar['dist'], width=40)
        self.entry['dist'].grid(row=r, column=c+1, padx=padx, pady=pady, sticky='w')
        self.stringvar['dist'].trace("w", lambda name, index, mode, sv=self.stringvar['dist']: tkw.check_int_entry(sv))
        r+=1
        
        tk.Label(self, text='Max depth diff [m]:').grid(row=r, column=c, padx=padx, pady=pady, sticky='w')
        self.stringvar['depth'] = tk.StringVar()
        self.entry['depth'] = tk.Entry(self, textvariable=self.stringvar['depth'], width=40)
        self.entry['depth'].grid(row=r, column=c+1, padx=padx, pady=pady, sticky='w')
        self.stringvar['depth'].trace("w", lambda name, index, mode, sv=self.stringvar['depth']: tkw.check_int_entry(sv))
        r+=1

        self.parameter_widget = tkw.ComboboxWidget(self,
                                                   title='Parameter',
                                                   callback_target=[],
                                                   row=r,
                                                   column=0,
                                                   pady=5,
                                                   sticky='w')
        r += 1

        self.button_add_sample_values = tk.Button(self, 
                                                    text=u'Add sample data',
                                                    command=self._on_add_sample_data)
        self.button_add_sample_values.grid(row=r, column=0, padx=padx, pady=(pady, pady), sticky='w')
        r+=1

        tkw.grid_configure(self, nr_rows=r, nr_columns=2)

    def update_parameter_list(self, file_id):
        parameter_list = self.session.get_parameter_list(file_id)
        self.parameter_widget.update_items(parameter_list)

    def get_parameter(self):
        return self.parameter_widget.get_value()

    #===========================================================================
    def _on_add_sample_data(self):
        self.time = float(self.stringvar['time'].get())
        self.dist = float(self.stringvar['dist'].get())
        self.depth = float(self.stringvar['depth'].get())
        if self.include_sampling_depth:
            self.sampling_depth = float(self.stringvar['sampling_depth'].get())
#        self.modulus = int(self.stringvar['modulus'].get())
        
        self.new_values = ''.join([self.stringvar[item].get() for item in sorted(self.stringvar)])
        if self.new_values != self.old_values:
            self.values_are_updated = True
        else:
            self.values_are_updated = False
        self.old_values = self.new_values

        # Save settings to user
        self.user.match.set('hours', str(self.time))
        self.user.match.set('dist', str(self.dist))
        self.user.match.set('depth', str(self.depth))
        
        if self.callback:
            self.callback()
    
    #===========================================================================
    def set_data(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.stringvar:
                self.stringvar[key].set(str(int(float(value))))
        
"""
================================================================================
================================================================================
================================================================================
"""
class SaveWidget(ttk.LabelFrame):
    def __init__(self, 
                 parent,
                 label='',
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
        
        self.callback = callback
        self.user = user
        
        self._set_frame()

        self._set_directory()
        
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

        ttk.Button(frame, text='Get directory', command=self._get_directory).grid(row=r, column=c + 2, columnspan=2, padx=padx,
                                                                      pady=pady, sticky='se')

        r+=1
        
        tk.Label(frame, text='File name:').grid(row=r, column=c, padx=padx, pady=pady, sticky='nw')
        self.stringvar_file_name = tk.StringVar()
        self.entry_file_name = tk.Entry(frame, textvariable=self.stringvar_file_name, **self.prop_entry)
        self.entry_file_name.grid(row=r, column=c+1, padx=padx, pady=pady, sticky='nw')
        self.stringvar_file_name.trace("w", lambda name, index, mode, sv=self.stringvar_file_name: tkw.check_path_entry(sv))
        r+=1
        
        ttk.Button(frame, text='Save', command=self._save_file).grid(row=r, column=c+1, columnspan=2, padx=padx, pady=pady, sticky='se')
        
        tkw.grid_configure(frame, nr_rows=r+1)
   
    def _get_directory(self):
        directory = tk.filedialog.askdirectory()
        if directory:
            self.stringvar_directory.set(directory)

    # ===========================================================================
    def _set_directory(self):
        if not self.user:
            return
        directory = self.user.path.setdefault('save_file_directory', '')
        directory = directory.replace('\\', '/')
        self.stringvar_directory.set(directory)

    #===========================================================================
    def _save_file(self):
        if self.callback:
            directory = self.stringvar_directory.get().strip() #.replace('\\', '/')
            file_name = self.stringvar_file_name.get().strip()
            if self.user:
                self.user.path.set('save_file_directory', directory)
            self.callback(directory, file_name)
    
    #===========================================================================
    def set_file_path(self, file_path=None):
        if not file_path: # or os.path.exists(file_path):
            self.stringvar_directory.set('')
            self.stringvar_file_name.set('')
            self._set_directory()
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

        self._set_directory()

        # ===========================================================================

    def _set_frame(self):
        padx = 5
        pady = 5

        frame = tk.Frame(self)
        frame.grid(row=0, column=0, padx=padx, pady=pady, sticky='w')
        tkw.grid_configure(self)


        tk.Label(frame, text='Directory:').grid(row=0, column=0, padx=padx, pady=pady, sticky='nw')
        self.stringvar_directory = tk.StringVar()
        self.entry_directory = tk.Entry(frame, textvariable=self.stringvar_directory, **self.prop_entry)
        self.entry_directory.grid(row=0, column=1, padx=padx, pady=pady, sticky='nw')
        self.stringvar_directory.trace("w",
                                       lambda name, index, mode, sv=self.stringvar_directory: tkw.check_path_entry(sv))


        self.frame_parameters = tk.Frame(frame)
        # self.frame_parameters = tk.LabelFrame(frame, text='Parameters to export')
        self.frame_parameters.grid(row=1, column=0, columnspan=2, padx=padx, pady=pady, sticky='nsew')

        self.checkbutton_widget = tkw.CheckbuttonWidget(frame,
                                                      items=['Combined plot', 'Individual plots'],
                                                      pre_checked_items=[],
                                                      include_select_all=False,
                                                      colors=[],
                                                      pady=0,
                                                      row=1,
                                                      column=2)


        ttk.Button(frame, text=u'Export', command=self._save_file).grid(row=2, column=0, columnspan=2, padx=padx,
                                                                      pady=pady, sticky='se')

        tkw.grid_configure(frame, nr_rows=2, nr_columns=2)

        self._set_frame_listbox_parameters()

    def _set_frame_listbox_parameters(self):

        self.listbox_widget_parameters = tkw.ListboxSelectionWidget(self.frame_parameters,
                                                                    prop_frame={},
                                                                    prop_items={'height': 3},
                                                                    prop_selected={'height': 3},
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
        selection['directory'] = self.stringvar_directory.get()
        selection['parameters'] = self.listbox_widget_parameters.get_selected()
        plot_types_selected = self.checkbutton_widget.get_checked_item_list()
        selection['combined_plot'] = 'Combined plot' in plot_types_selected
        selection['individual_plots'] = 'Individual plots' in plot_types_selected
        selection['individual_maps'] = 'Individual maps' in plot_types_selected

        return selection

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

    def _ok_and_forget(self):
        self.user.options.set('show_info_popups', False)
        self.popup_frame.destroy()
        # self.controller.deiconify()

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
    Handles popop for a entry.
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





def show_information(title, message):
    messagebox.showinfo(title, message)


def show_warning(title, message):
    messagebox.showwarning(title, message)


def show_error(title, message):
    messagebox.showerror(title, message)

