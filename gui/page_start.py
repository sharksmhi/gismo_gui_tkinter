#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import tkinter as tk

import gui


import logging

pages = set()
#============================================================================
# Ferrybox pages
# try:
#     pages.add(gui.PageTimeseries)
# #     logging.info('PageFerrybox imported!')
# except:
#     pass
# #     logging.info('PageFerrybox not imported!')

#----------------------------------------------------------------------------
#try:
#    pages.add(gui.PageFerryboxRoute)
##     logging.info('PageFerryboxRoute imported!')
#except:
#    pass
#     logging.info('PageFerryboxRoute not imported!')


#============================================================================
# CTD pages
# try:
#     pages.add(gui.PageCTD)
# #     logging.info('PageCTD imported!')
# except:
#     pass
# #     logging.info('PageCTD not imported!')

"""
================================================================================
================================================================================
================================================================================
"""
class PageStart(tk.Frame):

    def __init__(self, parent, controller, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        # parent is the frame "container" in App. contoller is the App class
        self.parent = parent
        self.controller = controller

    
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
        self.button_texts = {'Ferrybox': gui.PageFerrybox,
                             'Fixed platforms': gui.PageFixedPlatforms}
        self.button_colors = {gui.PageFerrybox: 'sandybrown',
                              gui.PageFixedPlatforms: 'lightblue'}
        
        r=0
        c=0
        for text in sorted(self.button_texts):
            page = self.button_texts[text]
            try:
                # text = self.button_texts[page]
                color = self.button_colors[page] 
                self.button[page] = tk.Button(self.frames[r][c], 
                                     text=text, 
                                     command=lambda x=page: self.controller.show_frame(x),
                                     font=font, 
                                     bg=color)
                
            
            
                self.button[page].grid(row=0, column=0, padx=padx, pady=pady, sticky='nsew') 
                self.frames[r][c].grid_rowconfigure(0, weight=1)
                self.frames[r][c].grid_columnconfigure(0, weight=1)
                c+=1
                if c >= nr_columns:
                    c = 0
                    r += 1
                print('OK', text, page)
            except:
                pass


    
    #===========================================================================
    def update_page(self):
        pass