# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

# To use basemap you might need to install Microsoft Visual C++: https://visualstudio.microsoft.com/visual-cpp-build-tools/


import tkinter as tk 
from tkinter import ttk
from tkinter import filedialog
#    from tkinter import filedialog
#    from tkinter import messagebox 

import os
import sys


import gui
import core

from libs.sharkpylib.gismo import GISMOsession

from libs.sharkpylib import gismo
from libs.sharkpylib.t
import gtb_lib.shd_tk.tkinter_widgets as tkw


import logging

all_pages = set()

all_pages.add(gui.PageStart)

#============================================================================
# TimeSeries pages
all_pages.add(gui.PageTimeSeries)
#try:
#    all_pages.add(gui.PageFerrybox)
##     logging.info('PageFerrybox imported!')
#except:
#    pass
##     logging.info('PageFerrybox not imported!')
#
##----------------------------------------------------------------------------
#try:
#    all_pages.add(gui.PageFerryboxRoute)
##     logging.info('PageFerryboxRoute imported!')
#except:
#    pass
##     logging.info('PageFerryboxRoute not imported!')
#
#
##============================================================================
## CTD pages
#try:
#    all_pages.add(gui.PageCTD)
##     logging.info('PageCTD imported!')
#except:
#    pass
#     logging.info('PageCTD not imported!')

#============================================================================




# @gtb_utils.singleton
class App(tk.Tk):
    """
    This class contains the main window (page), "container", for 
    the GISMOtoolbox application.
    Additional pages in the application are stored under self.frames. 
    The container is the parent frame that is passed to other pages. 
    self is also passed to the other pages objects and should there be given the name
    "self.controller". 
    Toolboxsettings and logfile can be reached in all page objects by calling
    "self.controller.settings" and "self.controller.logfile" respectivly. 
    """
    
    #===========================================================================
    def __init__(self,
                 user='default',
                 users_directory='',
                 root_directory='',
                 log_directory='',
                 input_directory='',
                 default_settings_file_path='',
                 *args, **kwargs):
        """
        Updated 20181002    by Magnus
        """

        tk.Tk.__init__(self, *args, **kwargs) 

        if not all([user, users_directory, root_directory, log_directory, input_directory]):
            raise AttributeError

        # Load settings and constants (singletons)
        self.root_directory = root_directory
        self.users_directory = users_directory
        self.log_directory = log_directory
        self.input_directory = input_directory
        
        # Initiate logging
        log_file = self.log_directory + '/system/gismo.log'
        logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG) 
        logging.info('=== NEW RUN ===')       
        
        self.user = user
        self.settings = core.Settings(default_settings_file_path=default_settings_file_path,
                                          root_directory=self.root_directory)
        self.boxen = Boxen(open_directory=input_directory)
        # self.boxen = core.Boxen(self, root_directory=self.root_directory)
        self.session = GISMOsession(root_directory=self.root_directory,
                                    users_directory=self.users_directory,
                                    user=user)
        
#        CMEMSparameters(self.settings['directory']['CMEMS parameters'])
#        CMEMSstations(self.settings['directory']['CMEMS stations'])
        self.default_platform_settings = gismo.SampleTypeSettings(self.settings['directory']['Default ferrybox settings'])
        
        screen_padx = self.settings[u'general'][u'Main window indent x']
        screen_pady = self.settings[u'general'][u'Main window indent y']
        

        # Override "close window (x)". 
        # If this is not implemented the program is not properly closed.
        self.protocol(u'WM_DELETE_WINDOW', self.quit_toolbox)
        
        # Set geometry, title etc.
#        self.geometry(u'%sx%s+0+0' % (self.winfo_screenwidth(), 
#                                     self.winfo_screenheight()))
        self.geometry(u'%sx%s+0+0' % (self.winfo_screenwidth()-screen_padx, 
                                     self.winfo_screenheight()-screen_pady))
#         tk.Tk.iconbitmap(self, default=u'D:/Utveckling/w_sharktoolbox/data/logo.ico')
        # TODO: Icon does not work
        self._create_titles()
        tk.Tk.wm_title(self, u'GISMO Toolbox')
        
        self.all_ok = True
        
        self.active_page = None
        self.previous_page = None
        self.admin_mode = False
        
#        self.sv = tk.StringVar()
        self._set_frame()

        
        # Make menu at the top
        self._set_menubar()

        self.startup_pages()
        
        
        # Show start page given in settings.ini
        self.page_history = [gui.PageStart]
        self.show_frame(gui.PageTimeSeries)
#        self.show_frame(eval('gui.' + self.settings['general']['Start page']))
        
    
    #==========================================================================
    def _set_frame(self):
#        frame = tk.Frame(self, bg='blue')
#        frame.grid(row=0, column=0, sticky="nsew")
#        self.grid_rowconfigure(0, weight=1)
#        self.grid_columnconfigure(0, weight=1)
        #----------------------------------------------------------------------
        # Create three main frames
#        self.frame_top = tk.LabelFrame(self, bg='red')
#        self.frame_mid = tk.LabelFrame(self, bg='cyan')
#        self.frame_bot = tk.LabelFrame(self, bg='magenta')
        self.frame_top = tk.Frame(self)
        self.frame_mid = tk.Frame(self)
        self.frame_bot = tk.Frame(self)
         
        
        # Grid
        self.frame_top.grid(row=0, column=0, sticky="nsew")
        self.frame_mid.grid(row=1, column=0, sticky="nsew")
        self.frame_bot.grid(row=2, column=0, sticky="nsew")
        
        # Gridconfigure 
        tkw.grid_configure(self, nr_rows=3, r0=50, r1=10, r2=1)
#        self.grid_rowconfigure(0, weight=7)
#        self.grid_rowconfigure(1, weight=5)
#        self.grid_rowconfigure(2, weight=1)
#        self.grid_columnconfigure(0, weight=1)
        
        #----------------------------------------------------------------------
        # Frame top
        # Create container in that will hold (show) all frames
        self.container = tk.Frame(self.frame_top)
        self.container.grid(row=0, column=0, sticky="nsew") 
        tkw.grid_configure(self.frame_top)
        
#        self.frame_top.grid_rowconfigure(0, weight=1)
#        self.frame_top.grid_columnconfigure(0, weight=1)
        
        #----------------------------------------------------------------------
        # Frame mid
        self.frame_add = tk.LabelFrame(self.frame_mid)
        self.frame_loaded = tk.LabelFrame(self.frame_mid)
        
        # Grid
        self.frame_add.grid(row=0, column=0, sticky="nsew")
        self.frame_loaded.grid(row=0, column=1, sticky="nsew")
        
        # Gridconfigure 
        tkw.grid_configure(self.frame_mid, nr_columns=2)
#        self.frame_mid.grid_rowconfigure(0, weight=1)
#        self.frame_mid.grid_columnconfigure(0, weight=1)
#        self.frame_mid.grid_columnconfigure(1, weight=1)
        
        #----------------------------------------------------------------------
        # Frame mid
        self.frame_info = tk.LabelFrame(self.frame_bot) 
        self.frame_info.grid(row=0, column=0, sticky="nsew")
        tkw.grid_configure(self.frame_bot)
#        self.frame_bot.grid_rowconfigure(0, weight=1)
#        self.frame_bot.grid_columnconfigure(0, weight=1)

        self.info_widget = tkw.LabelFrameLabel(self.frame_info)
        self.info_widget.set_text('Test info line')

        
        self._set_frame_add_file()
        self._set_frame_loaded_files()
        
        
    #===========================================================================
    def startup_pages(self):
        # Tuple that store all pages
#         all_pages = (PageStart, 
#                      PageCTD, 
#                      PageFerryboxRoute, 
#                      PageFerrybox)
        
        self.pages_started = dict((page, False) for page in all_pages)
        
        
        # Dictionary to store all frame classes
        self.frames = {}
        
        # Looping all pages to make them active. 
        for Page in all_pages:  # Capital P to emphasize class
            # Destroy old page if called as an update
            try:
                self.frames[Page].destroy()
                print(Page, u'Destroyed')
            except:
                pass
            frame = Page(self.container, self)
            frame.grid(row=0, column=0, sticky="nsew")

            self.container.rowconfigure(0, weight=1)
            self.container.columnconfigure(0, weight=1) 
            
            self.frames[Page] = frame
            
        self.activate_binding_keys()
        
        # Show start page at startup
#         self.show_frame(PageStart)

    
    #===========================================================================
    def _set_load_frame(self):
        self._set_frame_add_file() 
        self._set_frame_loaded_files()
        
        
    #===========================================================================
    def _set_frame_add_file(self):
        """
        Created     20180821    by Magnus 
        """
        #----------------------------------------------------------------------
        # Three main frames 
        frame = self.frame_add
        frame_data = tk.LabelFrame(frame, text='Data file')
        frame_settings = tk.LabelFrame(frame, text='Settings file')
        frame_sampling_type = tk.Frame(frame)
        
        # Grid 
        padx=5 
        pady=5
        frame_data.grid(row=0, column=0, sticky='nsew', padx=padx, pady=pady)
        frame_settings.grid(row=1, column=0, sticky='nsew', padx=padx, pady=pady) 
        frame_sampling_type.grid(row=2, column=0, sticky='nsew', padx=padx, pady=pady) 
        
        # Gridconfigure 
        tkw.grid_configure(frame, nr_rows=3)
#        frame.grid_rowconfigure(0, weight=1)
#        frame.grid_rowconfigure(1, weight=1)
#        frame.grid_rowconfigure(2, weight=1)
#        frame.grid_columnconfigure(0, weight=1)
        
        #----------------------------------------------------------------------
        # Data frame 
        self.button_get_ferrybox_data_file = ttk.Button(frame_data, text='Ferrybox', command=lambda: self._get_data_file_path('ferrybox'))
        self.button_get_fixed_platform_data_file = ttk.Button(frame_data, text='Fixed platform', command=lambda: self._get_data_file_path('fixed platform'))
        self.button_get_ctd_data_file = ttk.Button(frame_data, text='CTD-profile', command=lambda: self._get_data_file_path('ctd'))
        
        self.stringvar_data_file = tk.StringVar()
        self.entry_data_file = tk.Entry(frame_data, textvariable=self.stringvar_data_file, state='disabled')
        
        
        # Grid 
        padx=5
        pady=5
        self.button_get_ferrybox_data_file.grid(row=0, column=0, padx=padx, pady=pady, sticky='nsew')
        self.button_get_fixed_platform_data_file.grid(row=0, column=1, padx=padx, pady=pady, sticky='nsew') 
        self.button_get_ctd_data_file.grid(row=0, column=2, padx=padx, pady=pady, sticky='nsew')
        
        self.entry_data_file.grid(row=1, column=0, columnspan=5, padx=padx, pady=pady, sticky='nsew')
        
        
        # Gridconfigure 
        tkw.grid_configure(frame_data, nr_rows=2, nr_columns=3)
#        frame_data.grid_rowconfigure(0, weight=1)
#        frame_data.grid_rowconfigure(1, weight=1)
#        frame_data.grid_columnconfigure(0, weight=1)
#        frame_data.grid_columnconfigure(1, weight=1)
#        frame_data.grid_columnconfigure(2, weight=1)
        
        
        #----------------------------------------------------------------------
        # Settings frame
        self.button_get_settings_file = ttk.Button(frame_settings, text='Get settings file:', command=self._get_settings_file_path)
        
        self.stringvar_settings_file = tk.StringVar()
        self.entry_settings_file = tk.Entry(frame_settings, textvariable=self.stringvar_settings_file, state='disabled')
        
        #Grid 
        self.button_get_settings_file.grid(row=0, column=0, padx=padx, pady=pady, sticky='w')
        self.entry_settings_file.grid(row=1, column=0, padx=padx, pady=pady, sticky='nsew')
        
        # Gridconfigure 
        tkw.grid_configure(frame_settings, nr_rows=2)
#        frame_settings.grid_rowconfigure(0, weight=1)
#        frame_settings.grid_rowconfigure(1, weight=1)
#        frame_settings.grid_columnconfigure(0, weight=1)
        
        
        
        #----------------------------------------------------------------------
        # Sampling type frame
        self.combobox_widget_sampling_type = tkw.ComboboxWidget(frame_sampling_type, 
                                                                items=sorted(self.session.platform_types), 
                                                                title='Sampling type', 
                                                                prop_compobox={'width':20}, 
                                                                column=0, 
                                                                columnspan=1, 
                                                                row=0, 
                                                                sticky='w')
        
        # Load file button
        self.button_load_file = ttk.Button(frame_sampling_type, text='Load file', command=self._load_file)
        self.button_load_file.grid(row=0, column=1, padx=padx, pady=pady, sticky='se')
        self.button_load_file.configure(state='disabled')
        
        # Gridconfigure 
        tkw.grid_configure(frame_sampling_type, nr_columns=2)
#        frame_sampling_type.grid_rowconfigure(0, weight=1)
#        frame_sampling_type.grid_columnconfigure(0, weight=1)
#        frame_sampling_type.grid_columnconfigure(1, weight=1)
        

    #===========================================================================
    def _set_frame_loaded_files(self):
        """
        Created     20180821    by Magnus 
        """
        frame = self.frame_loaded 
        
#        prop = {'width': 90, 
#                'height': 5}
#        
#        r = 0 
        
        self.listbox_widget_loaded_files = tkw.ListboxWidget(frame, 
                                                             include_delete_button='Remove source')
#        self.listbox_widget_loaded_files = tkw.ListboxSelectionWidget(frame, 
#                                                                      sort_selected=True, 
#                                                                      vertical=True, 
#                                                                      prop_items=prop, 
#                                                                      prop_selected=prop, 
#                                                                      row=r, 
#                                                                      columnspan=2)
        tkw.grid_configure(frame)

        # self.boxen.loaded_files_widget = listbox_widget_loaded_files

    # ===========================================================================
    def _get_open_directory(self):
        if self.boxen.open_directory:
            open_directory = self.boxen.open_directory
        else:
            open_directory = self.settings[u'directory'][u'Input directory']


    #===========================================================================
    def _get_data_file_path(self, platform_type):
        """
        Created     20180821    by Magnus 
        """
        open_directory = self._get_open_directory()
            
        file_path = filedialog.askopenfilename(initialdir=open_directory, 
                                                 filetypes=[('GISMO-file ({})'.format(platform_type), '*.txt')])
                                                 
        if file_path:
            old_platform_type = self.combobox_widget_sampling_type.get_value() 
            self.combobox_widget_sampling_type.set_value(platform_type)
            self.stringvar_data_file.set(file_path)
            
            # Check settings file path
            settings_file_path = self.stringvar_settings_file.get()
            if not settings_file_path and platform_type != old_platform_type:
                self.stringvar_settings_file.set(self.settings['directory']['Default {} settings'.format(platform_type)])
            
            self.button_load_file.configure(state='normal')
        else:
            self.button_load_file.configure(state='disabled')
    
    
    #===========================================================================
    def old_get_data_file_path(self):
        if core.Boxen().open_directory:
            open_directory = core.Boxen().open_directory
        else:
            open_directory = self.settings[u'directory'][u'Input directory']
            
        file_path = filedialog.askopenfilename(initialdir=open_directory, 
                                                 filetypes=[('GISMO-file','*.txt')])
                                                 
        if file_path:
            self.stringvar_file_ferrybox.set(file_path)
            
            # Check settings file path
            settings_file_path = self.stringvar_settings_file_ferrybox.get()
            if not settings_file_path: 
                self.stringvar_settings_file_ferrybox.set(self.settings['directory']['Default gismo settings'])
            
            
    #===========================================================================
    def _get_settings_file_path(self):

        open_directory = self._get_open_directory()
            
        file_path = filedialog.askopenfilename(initialdir=open_directory, 
                                                filetypes=[('core.Settings-file','*.ini')])
                                                 
        if file_path:
            self.stringvar_settings_file_ferrybox.set(file_path)
            
            
    #===========================================================================
    def _load_file(self):
        self.reset_help_information()
        data_file_path = self.stringvar_data_file.get()
        settings_file_path = self.stringvar_settings_file.get() 
        sampling_type = self.combobox_widget_sampling_type.get_value()
        
        if not all([data_file_path, settings_file_path]): 
            self.update_help_information('No file selected!', fg='red')
            return 
        
        
        # Load file 
        self.update_help_information('Loading file...please wait...', fg='red') 
        all_ok = self.session.load_file(sampling_type=sampling_type, 
                                        file_path=data_file_path, 
                                        settings_file_path=settings_file_path, 
                                        reload=False)
        
        if not all_ok: 
            self.update_help_information('Could not load file!', bg='red')
            return 
            
        loaded_files = [] 
        for sampling_type in self.session.platform_types:
            for st in self.session.get_file_id_list(sampling_type): 
                loaded_files.append('{}: {}'.format(sampling_type, st))
        self.listbox_widget_loaded_files.update_items(loaded_files)
        self.update_help_information('File loaded! Please continue.')
        
#        self.listbox_widget_loaded_files.add_item(file_path)
        
        
    #===========================================================================
    def old_set_load_frame(self):
        frames = []
        if 'gui.page_time_series' in sys.modules:
            frames.append('Time series files')
        if 'gui.page_ctd' in sys.modules:
            frames.append('CTD files')
        frames.append('Sample files')
        
        self.notebook_load = tkw.NotebookWidget(self.load_frame, frames=frames)
        
        if 'gui.page_ferrybox' in sys.modules:
            self._set_load_ferrybox_frame()
        if 'gui.page_ctd' in sys.modules:
            self._set_load_ctd_frame()
        self._set_load_sample_frame()
        
        
    #===========================================================================
    def old_set_load_ferrybox_frame(self):
        frame = self.notebook_load.frame_ferrybox_files
        
        entry_width = 100
        padx=5
        pady=5
        r=0
        
        #----------------------------------------------------------------------
        self.button_get_file = ttk.Button(frame, text='Get file:', command=self._get_file_path_ferrybox)
        self.button_get_file.grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        self.stringvar_file_ferrybox = tk.StringVar()
        self.entry_file = tk.Entry(frame, textvariable=self.stringvar_file_ferrybox, width=entry_width, state='disabled')
        self.entry_file.grid(row=r, column=1, padx=padx, pady=pady, sticky='w')
        r+=1
        
        #----------------------------------------------------------------------
        self.button_get_settings_file_ferrybox = ttk.Button(frame, text='Get settings file:', command=self._get_settings_file_path_ferrybox)
        self.button_get_settings_file_ferrybox.grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        self.stringvar_settings_file_ferrybox = tk.StringVar()
        self.entry_settings_file = tk.Entry(frame, textvariable=self.stringvar_settings_file_ferrybox, width=entry_width, state='disabled')
        self.entry_settings_file.grid(row=r, column=1, padx=padx, pady=pady, sticky='w')
        r+=1
        
        #----------------------------------------------------------------------
        # Load file button
        self.button_load_file = ttk.Button(frame, text='Load file', command=self._load_file)
        self.button_load_file.grid(row=r, column=1, padx=padx, pady=pady, sticky='e')
        
        
        r+=1
        self.loaded_files_combobox_widget = tkw.ComboboxWidget(frame, 
                                                               title='Active file:', 
                                                               prop_compobox={'width':entry_width}, 
                                                               column=1, 
                                                               columnspan=1, 
                                                               sticky='w')
    
    
    #===========================================================================
    def old_set_load_ctd_frame(self):
        frame = self.notebook_load.frame_ctd_files
        
        entry_width = 80
        padx=5
        pady=5
        r=0
        
        self.button_load_ctd = ttk.Button(frame, text='Load CTD files', command=self._load_ctd)
        self.button_load_ctd.grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        r+=1
        
        prop = {'width': 90, 
                'height': 5}
        self.listbox_widget_ctd = tkw.ListboxSelectionWidget(frame, 
                                                             sort_selected=True, 
                                                             vertical=True, 
                                                             prop_items=prop, 
                                                             prop_selected=prop, 
                                                             row=r, 
                                                             columnspan=2)
        r+=1
        
        #----------------------------------------------------------------------
        self.button_get_settings_file_ctd = ttk.Button(frame, text='Get settings file:', command=self._get_settings_file_path_ctd)
        self.button_get_settings_file_ctd.grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        self.stringvar_settings_file_ctd = tk.StringVar()
        self.entry_settings_file_ctd = tk.Entry(frame, textvariable=self.stringvar_settings_file_ctd, width=entry_width, state='disabled')
        self.entry_settings_file_ctd.grid(row=r, column=1, padx=padx, pady=pady, sticky='w')
        self.stringvar_settings_file_ctd.set(self.settings['directory']['Default ctd settings'])
        core.Boxen().current_ctd_settings = gismo.PlatformSettings(self.stringvar_settings_file_ctd.get())
        r+=1
    
    
    #===========================================================================
    def old_set_load_sample_frame(self):
        frame = self.notebook_load.frame_sample_files
        
        entry_width = 100
        padx=5
        pady=5
        r=0
        
        #----------------------------------------------------------------------
        self.button_get_file_sample = ttk.Button(frame, text='Get file:', command=self._get_sample_file_path)
        self.button_get_file_sample.grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        self.stringvar_file_sample = tk.StringVar()
        self.entry_file_sample = tk.Entry(frame, textvariable=self.stringvar_file_sample, width=entry_width, state='disabled')
        self.entry_file_sample.grid(row=r, column=1, padx=padx, pady=pady, sticky='w')
        r+=1
        
        #----------------------------------------------------------------------
        self.button_get_settings_file_sample = ttk.Button(frame, text='Get settings file:', command=self._get_settings_file_path_sample)
        self.button_get_settings_file_sample.grid(row=r, column=0, padx=padx, pady=pady, sticky='w')
        
        self.stringvar_settings_file_sample = tk.StringVar()
        self.entry_settings_file_sample = tk.Entry(frame, textvariable=self.stringvar_settings_file_sample, width=entry_width, state='disabled')
        self.entry_settings_file_sample.grid(row=r, column=1, padx=padx, pady=pady, sticky='w')
        r+=1
        
        #----------------------------------------------------------------------
        # Load file button
        self.button_load_file_sample = ttk.Button(frame, text='Load sample file', command=self._load_sample_file)
        self.button_load_file_sample.grid(row=r, column=1, padx=padx, pady=pady, sticky='e')
        
        
        r+=1
        self.loaded_files_combobox_widget_sample = tkw.ComboboxWidget(frame, 
                                                                           title='Active sample file:', 
                                                                           prop_compobox={'width':entry_width}, 
                                                                           column=1, 
                                                                           columnspan=1, 
                                                                           sticky='w')
                                                               
    #===========================================================================
    def old_load_ferrybox(self):
        self.update_help_information('Loading file...please wait...')
        file_path = self.stringvar_file_ferrybox.get()
        settings_file_path = self.stringvar_settings_file_ferrybox.get()
        
        if not all([file_path, settings_file_path]):
            return
            
        core.Boxen().add_ferrybox_file(file_path=file_path, 
                                           settings_file_path=settings_file_path)
        
        self.update_files_information()
        self.update_help_information('Done!')
    
    
    #===========================================================================
    def old_load_ctd(self):
        
        if core.Boxen().open_directory:
            open_directory = core.Boxen().open_directory
        else:
            open_directory = self.settings[u'directory'][u'Input directory']
        file_paths = filedialog.askopenfilenames(initialdir=open_directory, 
                                                 filetypes=[('CTD gismo-files','*.txt')])
        
        settings_file_path = self.stringvar_settings_file_ctd.get() 
        
        self.update_help_information('Loading ctd files...please wait...')
        if file_paths:
            core.Boxen().add_ctd_files(file_paths=file_paths, 
                                  settings_file_path=settings_file_path)
            self.listbox_widget_ctd.add_items(file_paths)
        self.update_help_information('Done!')
        return
        
#         self.update_help_information('Loading ctd files...please wait...')
#         settings_file_path = self.stringvar_settings_file.get()
#         
#         if not all([file_path, settings_file_path]):
#             return
#             
#         core.Boxen().add_ctd_files(file_path=file_path, 
#                          settings_file_path=settings_file_path)
#         
#         self.update_files_information()
#         self.update_help_information('Done!')
        
        
        
    #===========================================================================
    def old_get_file_path_ferrybox(self):
        if core.Boxen().open_directory:
            open_directory = core.Boxen().open_directory
        else:
            open_directory = self.settings[u'directory'][u'Input directory']
            
        file_path = filedialog.askopenfilename(initialdir=open_directory, 
                                                 filetypes=[('GISMO-file','*.txt')])
                                                 
        if file_path:
            self.stringvar_file_ferrybox.set(file_path)
            
            # Check settings file path
            settings_file_path = self.stringvar_settings_file_ferrybox.get()
            if not settings_file_path: 
                self.stringvar_settings_file_ferrybox.set(self.settings['directory']['Default ferrybox settings'])
            
            
    #===========================================================================
    def old_get_settings_file_path_ferrybox(self):
        if core.Boxen().open_directory:
            open_directory = core.Boxen().open_directory
        else:
            open_directory = self.settings[u'directory'][u'Data directory']
            
        file_path = filedialog.askopenfilename(initialdir=open_directory, 
                                                 filetypes=[('core.Settings-file','*.ini')])
                                                 
        if file_path:
            self.stringvar_settings_file_ferrybox.set(file_path)
    
    
    #===========================================================================
    def old_load_sample_file(self):
#         print 'LOADING'
        self.update_help_information('Loading sample file...please wait...')
        file_path = self.stringvar_file_sample.get()
        settings_file_path = self.stringvar_settings_file_sample.get()
        
        if not all([file_path, settings_file_path]):
            return
        core.Boxen().add_sample_file(file_path=file_path, 
                                    settings_file_path=settings_file_path)
                                  
        self.update_files_information()
        self.update_help_information('Done!')
        
    #===========================================================================
    def old_get_sample_file_path(self):
        if core.Boxen().open_directory:
            open_directory = core.Boxen().open_directory
        else:
            open_directory = self.settings[u'directory'][u'Input directory']
            print('open_directory', open_directory)
            
        file_path = filedialog.askopenfilename(initialdir=open_directory, 
                                                 filetypes=[('sample-file','*.txt')])
                                                 
        if file_path:
            self.stringvar_file_sample.set(file_path)
            
            # Check settings file path
            settings_file_path = self.stringvar_settings_file_sample.get()
            if not settings_file_path: 
                self.stringvar_settings_file_sample.set(self.settings['directory']['Default sample settings'])
            
    #===========================================================================
    def old_get_settings_file_path_sample(self):
        if core.Boxen().open_directory:
            open_directory = core.Boxen().open_directory
        else:
            open_directory = self.settings[u'directory'][u'Data directory']
            print('open_directory', open_directory)
            
        file_path = filedialog.askopenfilename(initialdir=open_directory, 
                                                 filetypes=[('sample settings-file','*.ini')])
                                                 
        if file_path:
            self.stringvar_file_sample.set(file_path)
            
    #===========================================================================
    def old_get_settings_file_path_ctd(self):
        if core.Boxen().open_directory:
            open_directory = core.Boxen().open_directory
        else:
            open_directory = self.settings[u'directory'][u'Data directory']
            print('open_directory', open_directory)
            
        file_path = filedialog.askopenfilename(initialdir=open_directory, 
                                                 filetypes=[('ctd settings-file','*.ini')])
                                                 
        if file_path:
            self.stringvar_file_ctd.set(file_path)
            core.Boxen().current_ctd_settings = gismo.PlatformSettings(file_path)
    
    
    
    
    #===========================================================================
    def _quick_run_F1(self, event):
        try:
            self.show_frame(gui.PageCTD)
        except:
            pass
            
    #===========================================================================
    def _quick_run_F2(self, event):
        pass
            
    #===========================================================================
    def _quick_run_F3(self, event):
        pass
    
    #===========================================================================
    def activate_binding_keys(self):
        """
        Load binding keys
        """
        self.bind("<Home>", lambda event: self.show_frame(gui.PageStart))
        self.bind("<Escape>", lambda event: self.show_frame(gui.PageStart))
        
        self.bind("<F1>", self._quick_run_F1)
        self.bind("<F2>", self._quick_run_F2)
        self.bind("<F3>", self._quick_run_F3)
        
        # Pages
        self.bind("<Control-f>", lambda event: self.show_frame(gui.PageFerrybox))
        self.bind("<Control-r>", lambda event: self.show_frame(gui.PageFerryboxRoute))

    
    
    
    
    #==========================================================================
    def add_working_indicator(self):
        pass
#         self.update_help_information(u'Loading...')
#         self.working_indicator = tk.Label(self, text=u'Loading...', 
#                                           fg=u'red', 
#                                           font=("Helvetica", 16, u'italic'))
#         self.working_indicator.grid(row=0, column=0)
       
    #==========================================================================
    def delete_working_indicator(self): 
        pass
#         self.update_help_information(None)
#         self.working_indicator.destroy()
        
    
    #===========================================================================
    def update_files_information(self):
        """
        Updates the file information window (at the bottom left of the screen). 
        """
        self.loaded_files_combobox_widget.update_items(sorted(core.Boxen().loaded_ferrybox_files))
        self.loaded_files_combobox_widget_sample.update_items(sorted(core.Boxen().loaded_sample_files))
        
        
        
#         self.file_info_text.config(state=u'normal')
#         self.file_info_text.delete('1.0','end')
#         self.file_info_text.insert('end', string) 
#         self.file_info_text.config(state=u'disabled')
        
    
    #===========================================================================
    def update_help_information(self, text=u'', **kwargs):
        """
        Created     20180822    by Magnus
        """ 
        self.info_widget.set_text(text, **kwargs)
        
        
    #===========================================================================
    def reset_help_information(self):
        """
        Created     20180822    by Magnus
        """ 
        self.info_widget.reset()
        
    
    #===========================================================================
    def update_all(self):
        
        for page_name, frame in self.frames.iteritems():
            try:
                if self.pages_started[page_name]:
                    frame.update_page()
            except:
                pass
        try:
            self.update_series_information() 
        except:
            pass
    
    
    
    #===========================================================================
    def _set_menubar(self):
        """
        Method sets up the menu bar at the top och the Window.
        """
        menubar = tk.Menu(self)
        
        #-----------------------------------------------------------------------
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=u'Home', 
                              command=lambda: self.show_frame(gui.PageStart))
        file_menu.add_separator()
        file_menu.add_command(label=u'Quit', command=self.quit_toolbox)
        menubar.add_cascade(label=u'File', menu=file_menu)
        
        
        #-----------------------------------------------------------------------
        # Page menu
        goto_menu = tk.Menu(menubar, tearoff=0)
        print('sys.modules', sys.modules)
        #-----------------------------------------------------------------------
        if 'gui.page_ferrybox' in sys.modules:
            goto_menu.add_command(label=u'Ferrybox', 
                                      command=lambda: self.show_frame(gui.PageFerrybox))
        
        #-----------------------------------------------------------------------
        if 'gui.page_ferrybox_route' in sys.modules:
            goto_menu.add_command(label=u'Ferrybox route', 
                                  command=lambda: self.show_frame(gui.PageFerryboxRoute))
        
        #-----------------------------------------------------------------------
        if 'gui.page_ctd' in sys.modules:
            goto_menu.add_command(label='CTD', 
                                  command=lambda: self.show_frame(gui.PageCTD))
 
        
        menubar.add_cascade(label=u'Goto', menu=goto_menu)
        

        #-----------------------------------------------------------------------
        # core.Settings menu
#         settings_menu = tk.Menu(menubar, tearoff=0)
#         settings_menu.add_command(label=u'Toolbox settings', 
#                                   command=lambda: self.show_frame(Pagecore.Settings))

        
        
        #-----------------------------------------------------------------------
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=u'About')
        menubar.add_cascade(label=u'Help', menu=help_menu)
        
        #-----------------------------------------------------------------------
        # Insert menu
        self.config(menu=menubar)


    #===========================================================================
    def show_frame(self, page):
        """
        This method brings the given Page to the top of the GUI. 
        Before "raise" call frame startup method. 
        This is so that the Page only loads ones.
        """
#         if page == PageAdmin and not self.admin_mode:
#             page = PagePassword
        
        load_page = True
        frame = self.frames[page]
        title = self._get_title(page)
        if not self.pages_started[page]:
            frame.startup()
            self.pages_started[page] = True
            
        frame.update_page()
#             try:
#                 frame.update()
#             except:
#                 Log().information(u'%s: Could not update page.' % title)
                
        #-----------------------------------------------------------------------
        if load_page:
            frame.tkraise()
            tk.Tk.wm_title(self, u'GISMO Toolbox: %s' % title)
            self.previous_page = self.active_page
            self.active_page = page
            
            # Check page history
            if page in self.page_history:
                self.page_history.pop()
                self.page_history.append(page)
                
                
        try:
            if self.active_page == gui.PageCTD:
                self.notebook_load.select_frame('CTD files')
                
        except:
            pass
        
            
    #===========================================================================
    def goto_previous_page(self, event):
        self.page_history
        if self.previous_page:
            self.show_frame(self.previous_page) 
        
    #===========================================================================
    def previous_page(self, event):
        
        self.page_history.index(self.active_page)
        
    
    #===========================================================================
    def update_app(self):
        """
        Updates all information about loaded series. 
        """
        
        self.update_all()
    

        
        
    #===========================================================================
    def quit_toolbox(self):
        
        if self.settings.settings_are_modified:
            save_settings = tkMessageBox.askyesnocancel(u'Save core.Settings?', 
                                  u"""
                                  You have made one or more changes to the 
                                  toolbox settings during this session.
                                  Do you want to change these changes permanent?
                                  """)
            if save_settings==True:
                self.settings.save_settings()
                self.settings.settings_are_modified = False
            else:
                return
        
        self.destroy()  # Closes window
        self.quit()     # Terminates program
        
    #===========================================================================
    def _get_title(self, page):
        if page in self.titles:
            return self.titles[page]
        else:
            return u''
    
    #===========================================================================
    def _create_titles(self):
        self.titles = {}
        
        try:
            self.titles[gui.PageFerrybox] =  u'Ferrybox'
        except:
            pass
        
        try:
            self.titles[gui.PageFerryboxRoute] =  u'Ferrybox route'
        except:
            pass
        
        try:
            self.titles[gui.PageCTD] =  u'CTD'
        except:
            pass



"""
================================================================================
================================================================================
================================================================================
"""


class Boxen(object):
    """
    Updated 20180927    by Magnus Wenzer

    Class to hold constants and other fun stuff.
    """

    # ==========================================================================
    def __init__(self, *args, **kwargs):
        self.open_directory = kwargs.get('open_directory', '')
        self.loaded_files_widget = None

    # ==========================================================================
    def set_open_directory(self, directory):
        if os.path.exists(directory):
            self.open_directory = directory




"""            
================================================================================
================================================================================
================================================================================
"""

"""
================================================================================
================================================================================
================================================================================
"""

"""
================================================================================
================================================================================
================================================================================
"""
def main():
    """
    Updated 20181002    by Magnus Wenzer
    """
    root_directory = os.path.dirname(os.path.abspath(__file__))
    users_directory = os.path.join(root_directory, 'users')
    input_directory = os.path.join(root_directory, 'input')
    log_directory = os.path.join(root_directory, 'log')
    default_settings_file_path = os.path.join(root_directory, 'system/settings.ini')

    app = App(user='default',
              root_directory=root_directory,
              users_directory=users_directory,
              log_directory=log_directory,
              input_directory=input_directory,
              default_settings_file_path=default_settings_file_path)
    if not app.all_ok:
        return 
    app.focus_force()
    app.mainloop()
    return app
    
if __name__ == '__main__':
    app = main()






