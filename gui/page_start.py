#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import tkinter as tk

#import os

import gtb_gui
#import gtb_lib
#import gtb_core


#import gtb_lib.shd_gismo.gismo as gismo
#import gtb_lib.shd_plot.plot_selector as plot_selector
#from gtb_lib.shd_tk.tkmap import TkMap
#import gtb_lib.shd_tk.tkinter_widgets as tkw

import logging

pages = set()
#============================================================================
# Ferrybox pages
try:
    pages.add(gtb_gui.PageTimeSeries)
#     logging.info('PageFerrybox imported!')
except:
    pass
#     logging.info('PageFerrybox not imported!')

#----------------------------------------------------------------------------
#try:
#    pages.add(gtb_gui.PageFerryboxRoute)
##     logging.info('PageFerryboxRoute imported!')
#except:
#    pass
#     logging.info('PageFerryboxRoute not imported!')


#============================================================================
# CTD pages
try:
    pages.add(gtb_gui.PageCTD)
#     logging.info('PageCTD imported!')
except:
    pass
#     logging.info('PageCTD not imported!')

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
                print(r, c)
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
        self.button_texts = {gtb_gui.PageTimeSeries: 'Ferrybox and\nfixed platforms'}
        self.button_colors = {gtb_gui.PageTimeSeries:'sandybrown'}
        
        r=0
        c=0
        for page in sorted(self.button_texts): 
            print(r, c)
            if page in pages:
                text = self.button_texts[page]
                color = self.button_colors[page] 
                self.button[page] = tk.Button(self.frames[r][c], 
                                     text=text, 
                                     command=lambda: self.controller.show_frame(page), 
#                                     width=width, height=height, 
                                     font=font, 
                                     bg=color)
                
            
            
                self.button[page].grid(row=0, column=0, padx=padx, pady=pady, sticky='nsew') 
                self.frames[r][c].grid_rowconfigure(0, weight=1)
                self.frames[r][c].grid_columnconfigure(0, weight=1)
                c+=1
                if c >= nr_columns:
                    c=0 
                    r+=1
        
        
        
        #-----------------------------------------------------------------------
#        try:
#            if gtb_gui.PageFerryboxRoute in pages:
#                self.button_ferrybox_route = tk.Button(self, 
#                            text='Ferrybox Route', 
#                            command=lambda: self.controller.show_frame(gtb_gui.PageFerryboxRoute), 
#                            width=width, height=height, font=font, bg='darkgreen')
#        except:
#            self.button_ferrybox_route = tk.Button(self, 
#                        text='Ferrybox Route', 
#                        command=None, 
#                        width=width, height=height, font=font, bg='darkgreen')
#            
#            self.button_ferrybox_route.config(state='disabled')
#            
#        self.button_ferrybox_route.grid(row=r, column=c, padx=padx, pady=pady, sticky='sw')
#        r+=1
              
        
        
#        r=0
#        c+=1
#        
#        #-----------------------------------------------------------------------
#        try:
#            if gtb_gui.PageCTD in pages:
#                self.button_ctd = tk.Button(self, 
#                            text='CTD', 
#                            command=lambda: self.controller.show_frame(gtb_gui.PageCTD), 
#                            width=width, height=height, font=font, bg='pink') 
#            self.button_ctd.grid(row=r, column=c, padx=padx, pady=pady, sticky='sw')
#        except:
#            pass
##            print('CTD')
##            self.button_ctd = tk.Button(self, 
##                        text='CTD', 
##                        command=None, 
##                        width=width, height=height, font=font, bg='pink')
##            
##            self.button_ctd.config(state='disabled')
#            
##            self.button_ctd.grid(row=r, column=c, padx=padx, pady=pady, sticky='sw')
#        r+=1
#        
#        r=0
#        c+=1

    
    #===========================================================================
    def update_page(self):
        pass