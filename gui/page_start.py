#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import tkinter as tk




"""
================================================================================
================================================================================
================================================================================
"""
class PageStart(tk.Frame):

    def __init__(self, parent, main_app, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        # parent is the frame "container" in App. contoller is the App class
        self.parent = parent
        self.main_app = main_app

    
    #===========================================================================
#     @error_handler(raise_error)
    def startup(self):
        
        padx = 10
        pady = 10
        width = None
        height = 7
        font = 12
#        return
        #----------------------------------------------------------------------
        # Create frame grid 
        nr_rows = 4 
        nr_columns = 8
        self.frames = {} 
        self.texts = {}
        for r in range(nr_rows):
            for c in range(nr_columns): 
#                print('=', r, c)
                if r not in self.frames: 
                    self.frames[r] = {}
                    self.texts[r] = {}
#                print('-', r, c)
#                color = 'darkgreen'
#                if r%2 and not c%2:
#                    color = 'blue' 
#                 print(r, c)
                self.frames[r][c] = tk.Frame(self) 
                self.frames[r][c].grid(row=r, column=c, padx=padx, pady=pady, sticky='nsew')
#                self.texts[r][c] = tk.Label(self.frames[r][c], text='{}:{}'.format(r, c))
#                self.texts[r][c].grid(row=0, column=0, sticky='')
                
#                self.frames[r][c].update_idletasks()
                
        
        for r in range(nr_rows):
            for c in range(nr_columns):
                self.grid_rowconfigure(r, weight=1)
                self.grid_columnconfigure(c, weight=1)
#                self.frames[r][c].grid_rowconfigure(0, weight=1)
#                self.frames[r][c].grid_columnconfigure(0, weight=1)
        #----------------------------------------------------------------------
        
        # Buttons 
        self.button = {}

        # self.button_texts = {gui.PageFerrybox: 'Ferrybox',
        #                      gui.PageBuoy: 'Buoy'}
        # print('self.main_app.MODULES', self.main_app.get_plugins())
        self.button_texts = {}
        self.button_colors = {}
        color_list = ['sandybrown', 'red', 'blue']
        for i, (name, plugin) in enumerate(self.main_app.get_plugins().items()):
            # plugin_app = self.main_app.get_app_class(plugin)
            self.button_texts[plugin.INFO.get('title', 'Unknown title {}'.format(i))] = name
            self.button_colors[name] = color_list[i]
        
        r=0
        c=0
        for text in sorted(self.button_texts):
            page_name = self.button_texts[text]
            # try:
                # text = self.button_texts[page]
            color = self.button_colors[page_name]
            print('startup', page_name)
            self.button[page_name] = tk.Button(self.frames[r][c],
                                 text=text,
                                 command=lambda x=page_name: self.main_app.show_frame(page_name=x),
                                 font=font,
                                 bg=color)

            self.button[page_name].grid(row=0, column=0, padx=padx, pady=pady, sticky='nsew')
            self.frames[r][c].grid_rowconfigure(0, weight=1)
            self.frames[r][c].grid_columnconfigure(0, weight=1)
            c+=1
            if c >= nr_columns:
                c = 0
                r += 1
            print('OK', text, page_name)
            # except:
            #     pass


    
    #===========================================================================
    def update_page(self):
        pass