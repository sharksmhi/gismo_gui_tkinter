# -*- coding: utf-8 -*-
import tkinter as tk
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

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
        self.update_page()
    
    #===========================================================================
    def update_page(self):
        pass
        
    #===========================================================================
    def _set_frame(self):
        pass
    
    
    
    
    
    
    