#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import matplotlib as mpl

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime

import os
import numpy as np
import pandas as pd
#import shutil

from libs.sharkpylib import loglib
from plugins.gismo_qc import gui

import libs.sharkpylib.tklib.tkinter_widgets as tkw
import libs.sharkpylib.tklib.tkmap as tkmap

logger = loglib.get_logger(name='gismo_gui')


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
        self.user_manager = self.controller.user_manager

    def show_information(self, text=''):

        if not self.user_manager.user.options.setdefault('show_info_popups', True):
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
        self.user_manager.user.options.set('show_info_popups', False)
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


def show_information(title, message):
    messagebox.showinfo(title, message)


def show_warning(title, message):
    messagebox.showwarning(title, message)


def show_error(title, message):
    messagebox.showerror(title, message)

