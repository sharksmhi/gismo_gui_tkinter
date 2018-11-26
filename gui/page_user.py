# -*- coding: utf-8 -*-
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import tkinter as tk
from tkinter import ttk

import core

import libs.sharkpylib.tklib.tkinter_widgets as tkw

import matplotlib.pyplot as plt

"""
================================================================================
================================================================================
================================================================================
"""
class PageUser(tk.Frame):
    """
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # parent is the frame "container" in App. contoller is the App class
        self.parent = parent
        self.controller = controller
        self.settings = self.controller.settings
        self.session = self.controller.session
        self.user_manager = self.controller.user_manager
        self.user = self.user_manager.user # Obs. Have to update un updata page if user is updated

    #===========================================================================
    def startup(self):
        self._set_frame()
        self.update()
    
    #===========================================================================
    def update_page(self):
        self.user = self.user_manager.user

        self.stringvar_user.set(self.user.name)

        # Map
        self._set_map_boundries()

        # Colormap
        # self._load_color_map_info()
        self._on_select_colormap()


        
    #===========================================================================
    def _set_frame(self):

        opt = {'padx': 5,
               'pady': 5,
               'sticky': 'nsew'}

        padx = 5
        pady = 5

        # User
        self.user_frame = tk.Frame(self)
        self.user_frame.grid(row=0, column=0, **opt)
        tk.Label(self.user_frame, text='Settings for user:').grid(row=0, column=0, sticky='w', padx=padx, pady=pady)

        self.stringvar_user = tk.StringVar()
        tk.Label(self.user_frame, textvariable=self.stringvar_user).grid(row=0, column=1, sticky='w', padx=padx, pady=pady)
        tkw.grid_configure(self.user_frame, nr_columns=2)


        r=1
        # -----------------------------------------------------------------------
        # Creating frames
        self.labelframe_map = ttk.Labelframe(self, text='Map')
        self.labelframe_map.grid(row=r, column=0, **opt)

        self.labelframe_color_maps = ttk.Labelframe(self, text='Color maps')
        self.labelframe_color_maps.grid(row=r, column=1, **opt)

        self.labelframe_plot_style = ttk.Labelframe(self, text='Plot style')
        self.labelframe_plot_style.grid(row=r, column=2, **opt)

        r+=1
        self.labelframe_options = ttk.Labelframe(self, text='Other options')
        self.labelframe_options.grid(row=r, column=0, **opt)

        tkw.grid_configure(self, nr_rows=3, nr_columns=3, r1=10)
    
        self._set_frame_map_boundries()
        self._set_frame_color_maps()
        self._set_frame_plot_style()
        self._set_frame_options()

    def _set_frame_options(self):
        def _on_change():
            self.user.options.set('show_info_popups', self.intvar_show_info_popup.get())
        frame = self.labelframe_options
        self.intvar_show_info_popup = tk.IntVar()
        self.checkbutton_show_info_popup = tk.Checkbutton(frame,
                                                          text='Show help info popups',
                                                          variable=self.intvar_show_info_popup,
                                                          command=_on_change)
        self.checkbutton_show_info_popup.grid(row=0, column=0, padx=5, pady=5, sticky='nw')
        tkw.grid_configure(frame)


    def _set_frame_plot_style(self):
        labelframe = self.labelframe_plot_style
        frame = tk.Frame(labelframe)
        frame.grid(row=0, column=0, sticky='nw')
        tkw.grid_configure(labelframe)
        style_list = plt.style.available
        self.widget_selected_plotstyle = tkw.ComboboxWidget(frame, items=style_list, title='', callback_target=self._on_select_plotstyle, row=0, column=0, sticky='nw')
        self.widget_selected_plotstyle.set_value(self.user.layout.setdefault('plotstyle', self.settings['default']['plotstyle']))
        tk.Label(frame, text='Note that you have to restart\nthe program to activate the\nnew plot style.').grid(row=1,
                                                                                                                 column=0,
                                                                                                                 pady=10,
                                                                                                                 sticky='nw')
        tkw.grid_configure(frame, nr_rows=2)

    def _set_frame_map_boundries(self):
        labelframe = self.labelframe_map
        frame = tk.Frame(labelframe)
        frame.grid(row=0, column=0, sticky='nw')
        tkw.grid_configure(labelframe)

        padx = 5
        pady = 5
        
        # Labels 
        tk.Label(frame, text='Latitude MIN').grid(row=0, column=0, sticky='w', padx=padx, pady=pady)
        tk.Label(frame, text='Latitude MAX').grid(row=1, column=0, sticky='w', padx=padx, pady=pady)
        tk.Label(frame, text='Longitude MIN').grid(row=2, column=0, sticky='w', padx=padx, pady=pady)
        tk.Label(frame, text='Longitude MAX').grid(row=3, column=0, sticky='w', padx=padx, pady=pady)  
        
        # Entries
        prop_entry = {'width': 10}

        self.widget_lat_min = tkw.EntryWidget(frame, entry_type='float',
                                              entry_id='lat_min',
                                              prop_entry=prop_entry,
                                              callback_on_focus_out=self._on_change_map_boundries, row=0, column=1,
                                              sticky='w', padx=padx, pady=pady)
        self.widget_lat_max = tkw.EntryWidget(frame, entry_type='float',
                                              entry_id='lat_max',
                                              prop_entry=prop_entry,
                                              callback_on_focus_out=self._on_change_map_boundries, row=1, column=1,
                                              sticky='w', padx=padx, pady=pady)
        self.widget_lon_min = tkw.EntryWidget(frame, entry_type='float',
                                              entry_id='lon_min',
                                              prop_entry=prop_entry,
                                              callback_on_focus_out=self._on_change_map_boundries, row=2, column=1,
                                              sticky='w', padx=padx, pady=pady)
        self.widget_lon_max = tkw.EntryWidget(frame, entry_type='float',
                                              entry_id='lon_max',
                                              prop_entry=prop_entry,
                                              callback_on_focus_out=self._on_change_map_boundries, row=3, column=1,
                                              sticky='w', padx=padx, pady=pady)

        tk.Label(frame,
                 text="""Hit RETURN to confirm.
                 
                 Note that you have to restart
                 the program to activate the
                 new boundries.""").grid(row=4,
                                         column=0,
                                         columnspan=2,
                                         pady=10,
                                         sticky='nw')
        tkw.grid_configure(frame, nr_rows=4, nr_columns=2)

        # Link entries
        self.widget_lat_min.south_entry = self.widget_lat_max
        self.widget_lat_max.south_entry = self.widget_lon_min
        self.widget_lon_min.south_entry = self.widget_lon_max
        self.widget_lon_max.south_entry = self.widget_lat_min


        # Map resolution
        self.widget_map_resolution = None


    def _set_map_boundries(self):
        self.widget_lat_min.set_value(self.user.map_boundries.setdefault('lat_min', 53))
        self.widget_lat_max.set_value(self.user.map_boundries.setdefault('lat_max', 66))
        self.widget_lon_min.set_value(self.user.map_boundries.setdefault('lon_min', 9))
        self.widget_lon_max.set_value(self.user.map_boundries.setdefault('lon_max', 31))

    def _on_change_map_boundries(self, widget):
        self.user.map_boundries.set('lat_min', self.widget_lat_min.get_value())
        self.user.map_boundries.set('lat_max', self.widget_lat_max.get_value())
        self.user.map_boundries.set('lon_min', self.widget_lon_min.get_value())
        self.user.map_boundries.set('lon_max', self.widget_lon_max.get_value())
    
    def _set_frame_color_maps(self):
        labelframe = self.labelframe_color_maps
        frame = tk.Frame(labelframe)
        frame.grid(row=0, column=0, sticky='nw')
        tkw.grid_configure(labelframe)

        cmap_list = core.Colormaps().get_list()
        self.widget_selected_cmap = tkw.ComboboxWidget(frame, items=cmap_list, title='', callback_target=self._on_select_colormap, row=0, column=0, sticky='w')

        # self.button_save_cmap = tk.Button(frame, text='Save colormaps', command=self._save_colormap, bg='lightgreen')
        # self.button_save_cmap.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        self.widget_listbox_cmap = tkw.ListboxSelectionWidget(frame, row=1, column=0, sticky='nw', target=self._on_select_par_for_colormap)

        tkw.grid_configure(frame, nr_rows=2)

        self.current_pars_in_cmap = {}

    def _save_current_colormap(self):
        """
        Get color map information from user.
        :return:
        """
        self.current_pars_in_cmap[self.widget_selected_cmap.get_value()] = self.widget_listbox_cmap.get_selected()

    def _on_select_plotstyle(self):
        plotstyle = self.widget_selected_plotstyle.get_value()
        if plotstyle:
            self.user.layout.set('plotstyle', plotstyle)

    def _on_select_colormap(self):
        # Get all loaded parameters
        parameter_list_all = []
        for sampling_type in self.session.get_sampling_types():
            for file_id in self.session.get_file_id_list(sampling_type):
                parameter_list_all.extend(self.session.get_parameter_list(file_id))
        if not parameter_list_all:
            return
        # Update widget_listbox_cmap
        self.widget_listbox_cmap.update_items(sorted(parameter_list_all))
        self.widget_listbox_cmap.move_items_to_selected(self._get_pars_for_colormap())

        self._save_current_colormap()

    def _get_pars_for_colormap(self):
        """
        Returns a list of parameters for the given colormap. Information from User.
        :return:
        """
        cmap = self.widget_selected_cmap.get_value()
        par_list = []
        for par in self.user.parameter_colormap.get_keys():
            if self.user.parameter_colormap.get(par) == cmap:
                par_list.append(par)
        return par_list


    def _on_select_par_for_colormap(self):
        selected_cmap = self.widget_selected_cmap.get_value()
        selected_pars = self.widget_listbox_cmap.get_selected()

        # Check removed pars
        before = self.current_pars_in_cmap[selected_cmap][:]
        after = selected_pars
        removed = [item for item in before if item not in after]
        added = [item for item in after if item not in before]

        # Remove removed
        for par in removed:
            self.user.parameter_colormap.remove(par)


        # Add new and remove in other
        for par in added:
            self.user.parameter_colormap.set(par, selected_cmap)

        self._save_current_colormap()

        # for par in selected_pars:
        #     self.colormap_mapping.setdefault(selected_cmap, [])
        #     if par not in self.colormap_mapping[selected_cmap]:
        #         self.colormap_mapping[selected_cmap].append(par)
        #     # If added we should remove from other list
        #     for cmap in self.colormap_mapping.keys():
        #         if cmap == selected_cmap:
        #             continue
        #         if par in self.colormap_mapping[cmap]:
        #             self.colormap_mapping[cmap].pop(self.colormap_mapping.index(par))
        #             break

    # def _save_colormap(self):
    #     print(self.colormap_mapping)
    #     for cmap in self.colormap_mapping:
    #         for par in self.colormap_mapping.get(cmap):
    #             self.user.parameter_colormap.set(par, cmap)
    #
    #     self.button_save_cmap.config(bg='lightgreen')
    