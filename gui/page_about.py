# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import libs.sharkpylib.tklib.tkinter_widgets as tkw

import webbrowser

import os
import core
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

"""
================================================================================
================================================================================
================================================================================
"""
class PageAbout(tk.Frame):
    """
    Dummy page used as a base.
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # parent is the frame "container" in App. contoller is the App class
        self.parent = parent
        self.controller = controller

    #===========================================================================
    def startup(self):
        self._set_frame()
        self.update()
    
    #===========================================================================
    def update_page(self):
        pass
        
    #===========================================================================
    def _set_frame(self):
        padx = 5
        pady = 5

        self.labelframe_about = tk.LabelFrame(self, text='About')
        self.labelframe_about.grid(row=0, column=0, sticky='nsew', padx=padx, pady=pady)

        self.labelframe_developed = tk.LabelFrame(self, text='Developed by')
        self.labelframe_developed.grid(row=0, column=1, sticky='nsew', padx=padx, pady=pady)

        self.labelframe_cooperation = tk.LabelFrame(self, text='In cooperation with')
        self.labelframe_cooperation.grid(row=0, column=2, sticky='nsew', padx=padx, pady=pady)

        tkw.grid_configure(self, nr_columns=3)

        self._set_frame_about()
        self._set_frame_developed()
        self._set_frame_cooperation()

    def _set_frame_about(self):
        frame = self.labelframe_about

        padx = 5
        pady = 5
        tk.Label(frame, text=core.texts.about()).grid(row=0, column=0, sticky='nsew', padx=padx, pady=pady)

        tkw.grid_configure(frame)

    def _set_frame_cooperation(self):
        def _on_click_jerico_link(event):
            webbrowser.open_new(r'www.jerico-ri.eu')
        frame = self.labelframe_developed

        padx = 5
        pady = 5
        self.jerico_image = tk.PhotoImage(
            file=os.path.join(self.controller.app_directory, 'system/pic/Logotype_Jerico_next.gif'))
        self.jerico_image_label = tk.Label(frame, image=self.jerico_image, cursor="hand2")
        self.jerico_image_label.grid(row=0, column=0, sticky='nsew', padx=padx, pady=pady)
        self.jerico_image_label.bind("<Button-1>", _on_click_jerico_link)

        self.jerico_link = tk.Label(frame, text=r'www.jerico-ri.eu', fg="blue", cursor="hand2")
        self.jerico_link.grid(row=1, column=0, sticky='nsew', padx=padx, pady=pady)
        self.jerico_link.bind("<Button-1>", _on_click_jerico_link)

        tkw.grid_configure(frame, nr_rows=2)


    def _set_frame_developed(self):
        def _on_click_smhi_link(event):
            webbrowser.open_new(r'www.smhi.se')
        frame = self.labelframe_cooperation

        padx = 5
        pady = 5
        self.smhi_image = tk.PhotoImage(
            file=os.path.join(self.controller.app_directory, 'system/pic/smhi_logo.gif'))
        self.smhi_image_label = tk.Label(frame, image=self.smhi_image, cursor="hand2")
        self.smhi_image_label.grid(row=0, column=0, sticky='nsew', padx=padx, pady=pady)
        self.smhi_image_label.bind("<Button-1>", _on_click_smhi_link)

        self.smhi_link = tk.Label(frame, text=r'www.smhi.se', fg="blue", cursor="hand2")
        self.smhi_link.grid(row=1, column=0, sticky='nsew', padx=padx, pady=pady)
        self.smhi_link.bind("<Button-1>", _on_click_smhi_link)

        tkw.grid_configure(frame, nr_rows=2)
    



    
    
    
    