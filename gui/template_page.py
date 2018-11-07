# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 13:42:06 2017

@author: a001985
"""
try:
    # Python 2.7
    import Tkinter as tk 
except:
    # Python 3.0
    import tkinter as tk
import ttk



from utils.settings import Settings

# from utils.load_files import load_ferrybox_file
from utils.boxen import Boxen, Temp

from shd_tk.utils import grid_configure 
from shd_tk import tkinter_widgets as tkw
from shd_plot import plot_selector 
from shd_gismo.gismo import PlatformSettings

from gui.widgets import *
from gui.communicate import *
import logging
"""
================================================================================
================================================================================
================================================================================
"""
class PageTemplate(tk.Frame):
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
        pass
    
    
    
    
    
    
    