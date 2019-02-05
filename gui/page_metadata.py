# -*- coding: utf-8 -*-
import tkinter as tk


import libs.sharkpylib.tklib.tkinter_widgets as tkw

import gui
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

"""
================================================================================
================================================================================
================================================================================
"""
class PageMetadata(tk.Frame):
    """
    Dummy page used as a base.
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # parent is the frame "container" in App. contoller is the App class
        self.parent = parent
        self.controller = controller
        self.user_manager = controller.user_manager
        self.user = self.user_manager.user
        self.session = controller.session
        self.settings = controller.settings

    #===========================================================================
    def startup(self):
        self._set_frame()
        self.update()
    
    #===========================================================================
    def update_page(self):
        current_file_id = self.combobox_metadata_files.get_value()
        loaded_file_list = self.controller.get_loaded_files_list()
        file_id_list = []
        for file_string in loaded_file_list:
            file_id = gui.get_file_id(file_string)
            if self.session.has_metadata(file_id):
                file_id_list.append(file_id)
        self.combobox_metadata_files.update_items(file_id_list)
        if current_file_id in file_id_list:
            self.combobox_metadata_files.set_value(current_file_id)
        else:
            self.combobox_metadata_files.set_value(file_id_list[0])
        self._update_treeview()

    #===========================================================================
    def _set_frame(self):
        self.combobox_metadata_files = tkw.ComboboxWidget(self,
                                                          title='Show metadata for file',
                                                          prop_combobox={'width': 60},
                                                          sticky='w',
                                                          callback_target=self._update_treeview)
        self.treeview_metadata = tkw.TreeviewWidget(self,
                                                    columns=['Metadata', 'Value'],
                                                    row=1)

        tkw.grid_configure(self, nr_rows=2, r1=20)

    def _update_treeview(self):
        file_id = self.combobox_metadata_files.get_value()
        if not file_id:
            return

        metadata_dict = self.session.get_metadata_tree(file_id)
        self.treeview_metadata.set_treeview_dict(metadata_dict)
    
    
    
    
    
    