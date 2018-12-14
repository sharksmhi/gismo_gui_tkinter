# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

# To use basemap you might need to install Microsoft Visual C++: https://visualstudio.microsoft.com/visual-cpp-build-tools/


import tkinter as tk 
from tkinter import ttk
from tkinter import filedialog

import os
import sys

import matplotlib.pyplot as plt

import gui
import core

from libs.sharkpylib.gismo import GISMOsession

from libs.sharkpylib import gismo
import libs.sharkpylib.tklib.tkinter_widgets as tkw

from libs.sharkpylib.gismo.exceptions import *
from core.exceptions import *

import threading
import logging

all_pages = set()

all_pages.add(gui.PageStart)

#============================================================================
# Timeseries pages
all_pages.add(gui.PageFerrybox)
all_pages.add(gui.PageFixedPlatforms)
all_pages.add(gui.PageUser)
all_pages.add(gui.PageAbout)
all_pages.add(gui.PageTimeSeries)


#============================================================================



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
                 default_settings_file_path='',
                 sampling_types_factory=None,
                 qc_routines_factory=None,
                 *args, **kwargs):
        """
        Updated 20181002
        """

        tk.Tk.__init__(self, *args, **kwargs)

        self.withdraw()

        if not all([users_directory, root_directory, log_directory, sampling_types_factory, qc_routines_factory]):
            raise AttributeError

        # Load settings and constants (singletons)
        self.app_directory = os.path.dirname(os.path.abspath(__file__))
        self.root_directory = root_directory
        self.users_directory = users_directory
        self.log_directory = log_directory

        # Load paths
        self.paths = core.Paths(self.app_directory)

        # Load settings files object
        self.settings_files = core.SettingsFiles(self.paths.directory_settings_files)
        
        # Initiate logging
        log_file = os.path.join(self.log_directory, 'gismo.log')
        logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG) 
        logging.info('=== NEW RUN ===')       
        

        self.settings = core.Settings(default_settings_file_path=default_settings_file_path,
                                      root_directory=self.root_directory)

        # Load user
        self.user_manager = core.UserManager(os.path.join(self.root_directory, 'users'))
        startup_user = self.settings.get('user', {}).get('Startup user', 'default')
        self.user_manager.set_user(startup_user, create_if_missing=True)
        self.user = self.user_manager.user
        self.info_popup = gui.InformationPopup(self)
        plt.style.use(self.user.layout.setdefault('plotstyle', self.user.layout.setdefault('plotstyle', self.settings['default']['plotstyle'])))

        # self.boxen = Boxen(open_directory=self.settings['directory']['Input directory'])
        # self.boxen = core.Boxen(self, root_directory=self.root_directory)
        self.session = GISMOsession(root_directory=self.root_directory,
                                    users_directory=self.users_directory,
                                    log_directory=self.log_directory,
                                    user=user,
                                    sampling_types_factory=sampling_types_factory,
                                    qc_routines_factory=qc_routines_factory,
                                    save_pkl=False)

        
#        CMEMSparameters(self.settings['directory']['CMEMS parameters'])
#        CMEMSstations(self.settings['directory']['CMEMS stations'])
        self.default_platform_settings = None
        # self.default_platform_settings = gismo.sampling_types.SamplingTypeSettings(self.settings['directory']['Default ferrybox settings'],
        #                                                                            root_directory=self.root_directory)
        
        screen_padx = self.settings['general']['Main window indent x']
        screen_pady = self.settings['general']['Main window indent y']
        

        # Override "close window (x)". 
        # Override "close window (x)".
        # If this is not implemented the program is not properly closed.
        self.protocol('WM_DELETE_WINDOW', self.quit_toolbox)
        
        # Set geometry, title etc.
#        self.geometry(u'%sx%s+0+0' % (self.winfo_screenwidth(), 
#                                     self.winfo_screenheight()))
        self.geometry('%sx%s+0+0' % (self.winfo_screenwidth()-screen_padx,
                                     self.winfo_screenheight()-screen_pady))
#         tk.Tk.iconbitmap(self, default=u'D:/Utveckling/w_sharktoolbox/data/logo.ico')
        # TODO: Icon does not work
        self._create_titles()

        self.all_ok = True
        
        self.active_page = None
        self.previous_page = None
        self.admin_mode = False
        self.progress_running = False
        self.progress_running_toplevel = False

        self.latest_loaded_sampling_type = ''
        
#        self.sv = tk.StringVar()
        self._set_frame()

        
        # Make menu at the top
        self._set_menubar()

        self.startup_pages()
        
        
        # Show start page given in settings.ini
        self.page_history = [gui.PageStart]
        self.show_frame(gui.PageStart)
        # self.show_frame(gui.PageUser)
        # self.show_frame(gui.PageFerrybox)
        # self.show_frame(gui.PageFixedPlatforms)

        self.update()
        self.deiconify()

    #==========================================================================
    def _set_frame(self):
        self.frame_top = tk.Frame(self)
        self.frame_mid = tk.Frame(self)
        self.frame_bot = tk.Frame(self)

        
        # Grid
        self.frame_top.grid(row=0, column=0, sticky="nsew")
        self.frame_mid.grid(row=1, column=0, sticky="nsew")
        self.frame_bot.grid(row=2, column=0, sticky="nsew")
        
        # Gridconfigure 
        tkw.grid_configure(self, nr_rows=3, r0=100, r1=5, r2=1)
        
        #----------------------------------------------------------------------
        # Frame top
        # Create container in that will hold (show) all frames
        self.container = tk.Frame(self.frame_top)
        self.container.grid(row=0, column=0, sticky="nsew") 
        tkw.grid_configure(self.frame_top)

        
        #----------------------------------------------------------------------
        # Frame mid
        self.frame_add = tk.LabelFrame(self.frame_mid)
        self.frame_loaded = tk.LabelFrame(self.frame_mid, text='Loaded files')
        
        # Grid
        self.frame_add.grid(row=0, column=0, sticky="nsew")
        self.frame_loaded.grid(row=0, column=1, sticky="nsew")
        
        # Gridconfigure 
        tkw.grid_configure(self.frame_mid, nr_columns=2)
        
        #----------------------------------------------------------------------
        # Frame bot
        self._set_frame_bot()
        
        self._set_frame_add_file()
        self._set_frame_loaded_files()

    def _set_frame_bot(self):
        self.frame_info = tk.Frame(self.frame_bot)
        self.frame_info.grid(row=0, column=0, sticky="nsew")

        ttk.Separator(self.frame_bot, orient=tk.VERTICAL).grid(row=0, column=1, sticky='ns')

        self.frame_progress = tk.Frame(self.frame_bot)
        self.frame_progress.grid(row=0, column=2, sticky="nsew")

        self.info_widget = tkw.LabelFrameLabel(self.frame_info, pack=False)
        self.info_widget.set_text('Test info line')

        self.progress_widget = tkw.ProgressbarWidget(self.frame_progress, sticky='nsew')

        tkw.grid_configure(self.frame_info)
        tkw.grid_configure(self.frame_progress)
        tkw.grid_configure(self.frame_bot, nr_columns=3, c0=20, c2=4)

    def run_progress(self, run_function, message=''):

        def run_thread():
            self.progress_widget.run_progress(run_function, message=message)
            # try:
            #     self.progress_widget.run_progress(run_function, message=message)
            # except Exception as e:
            #     print(e)
            #     raise

        if self.progress_running:
            gui.show_information('Progress is running', 'A progress is running, please wait until it is finished!')
            return
        self.progress_running = True
        # run_thread = lambda: self.progress_widget.run_progress(run_function, message=message)
        threading.Thread(target=run_thread).start()
        self.progress_running = False

    def run_progress_in_toplevel(self, run_function, message=''):
        """
        Rins progress in a toplevel window.
        :param run_function:
        :param message:
        :return:
        """
        def run_thread():
            self.frame_toplevel_progress = tk.Toplevel(self)
            self.progress_widget_toplevel = tkw.ProgressbarWidget(self.frame_toplevel_progress, sticky='nsew', in_rows=True)
            self.frame_toplevel_progress.update_idletasks()
            self.progress_widget_toplevel.update_idletasks()
            print('running')
            self.progress_widget.run_progress(run_function, message=message)
            self.frame_toplevel_progress.destroy()

        if self.progress_running_toplevel:
            gui.show_information('Progress is running', 'A progress is running, please wait until it is finished!')
            return
        self.progress_running = True
        # run_thread = lambda: self.progress_widget.run_progress(run_function, message=message)
        threading.Thread(target=run_thread).start()
        self.progress_running = False

    #===========================================================================
    def startup_pages(self):
        # Tuple that store all pages
        
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
        frame_sampling_type = tk.LabelFrame(frame, text='Sampling type')
        frame_platform_depth = tk.LabelFrame(frame, text='Platform depth')
        frame_load = tk.Frame(frame)
        
        # Grid 
        padx=5 
        pady=5
        frame_data.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=padx, pady=pady)
        frame_settings.grid(row=1, column=0, sticky='nsew', padx=padx, pady=pady)
        frame_sampling_type.grid(row=1, column=1, sticky='nsew', padx=padx, pady=pady)
        frame_platform_depth.grid(row=1, column=2, sticky='nsew', padx=padx, pady=pady)
        frame_load.grid(row=1, column=3, sticky='nsew', padx=padx, pady=pady)

        # Gridconfigure 
        tkw.grid_configure(frame, nr_rows=2, nr_columns=4, r0=50)
#        frame.grid_rowconfigure(0, weight=1)
#        frame.grid_rowconfigure(1, weight=1)
#        frame.grid_rowconfigure(2, weight=1)
#        frame.grid_columnconfigure(0, weight=1)
        
        #----------------------------------------------------------------------
        # Data frame

        self.button_get_ferrybox_data_file = tk.Button(frame_data, text='Ferrybox CMEMS',
                                                       command=lambda: self._get_data_file_path('Ferrybox CMEMS'))
        self.button_get_fixed_platform_data_file = tk.Button(frame_data, text='Fixed platform CMEMS',
                                                             command=lambda: self._get_data_file_path('Fixed platforms CMEMS'))
        self.button_get_ctd_data_file = tk.Button(frame_data, text='CTD-profile',
                                                  command=lambda: self._get_data_file_path('CTD SHARK'))
        self.button_get_sampling_file = tk.Button(frame_data, text='Sampling data',
                                                  command=lambda: self._get_data_file_path('PhysicalChemical SHARK'))

        tkw.disable_widgets(self.button_get_ctd_data_file)
        
        self.stringvar_data_file = tk.StringVar()
        self.entry_data_file = tk.Entry(frame_data, textvariable=self.stringvar_data_file, state='disabled')
        
        
        # Grid 
        padx=5
        pady=5
        self.button_get_ferrybox_data_file.grid(row=0, column=0, padx=padx, pady=pady, sticky='nsew')
        self.button_get_fixed_platform_data_file.grid(row=0, column=1, padx=padx, pady=pady, sticky='nsew')
        self.button_get_ctd_data_file.grid(row=0, column=2, padx=padx, pady=pady, sticky='nsew')
        self.button_get_sampling_file.grid(row=0, column=3, padx=padx, pady=pady, sticky='nsew')
        
        self.entry_data_file.grid(row=1, column=0, columnspan=5, padx=padx, pady=pady, sticky='nsew')
        
        
        # Gridconfigure 
        tkw.grid_configure(frame_data, nr_rows=2, nr_columns=4)

        #----------------------------------------------------------------------
        # Settings frame
        self.combobox_widget_settings_file = tkw.ComboboxWidget(frame_settings,
                                                                items=[],
                                                                title='',
                                                                prop_combobox={'width': 40},
                                                                column=0,
                                                                columnspan=1,
                                                                row=0,
                                                                sticky='nsew')
        self._update_settings_combobox_widget()

        self.button_import_settings_file = ttk.Button(frame_settings, text='Import settings file', command=self._import_settings_file)
        self.button_import_settings_file.grid(row=0, column=1, padx=padx, pady=pady, sticky='nsew')
        tkw.grid_configure(frame_settings, nr_rows=1, nr_columns=2)

        #----------------------------------------------------------------------
        # Sampling type frame
        self.combobox_widget_sampling_type = tkw.ComboboxWidget(frame_sampling_type, 
                                                                items=sorted(self.session.get_sampling_types()),
                                                                title='',
                                                                prop_combobox={'width': 30},
                                                                column=0, 
                                                                columnspan=1, 
                                                                row=0, 
                                                                sticky='nsew')

        # Platform depth frame
        self.entry_widget_platform_depth = tkw.EntryWidget(frame_platform_depth, entry_type='int',
                                                           prop_entry=dict(width=5), row=0, column=0,
                                                           padx=padx, pady=pady, sticky='nsew')
        self.entry_widget_platform_depth.disable_widget()
        tk.Label(frame_platform_depth, text='meters').grid(row=0, column=1, padx=padx, pady=pady, sticky='nsew')
        tkw.grid_configure(frame_platform_depth)

        # Gridconfigure
        tkw.grid_configure(frame_sampling_type)

        # Load file button
        self.button_load_file = tk.Button(frame_load, text='Load file', command=self._load_file, bg='lightgreen', font=(30))
        self.button_load_file.grid(row=0, column=0, padx=padx, pady=pady, sticky='nsew')
        self.button_load_file.configure(state='disabled')
        tkw.grid_configure(frame_load)

    def _update_settings_combobox_widget(self):
        self.combobox_widget_settings_file.update_items(self.settings_files.get_list())

    #===========================================================================
    def _set_frame_loaded_files(self):
        """
        Created     20180821
        """
        frame = self.frame_loaded 
        
#        prop = {'width': 90, 
#                'height': 5}
#        
#        r = 0 
        prop_listbox = {'height': 4}
        self.listbox_widget_loaded_files = tkw.ListboxWidget(frame,
                                                             include_delete_button='Remove source',
                                                             prop_listbox=prop_listbox,
                                                             callback_delete_button=self._delete_source,
                                                             padx=1,
                                                             pady=1)
#        self.listbox_widget_loaded_files = tkw.ListboxSelectionWidget(frame, 
#                                                                      sort_selected=True, 
#                                                                      vertical=True, 
#                                                                      prop_items=prop, 
#                                                                      prop_selected=prop, 
#                                                                      row=r, 
#                                                                      columnspan=2)
        tkw.grid_configure(frame)

        # self.boxen.loaded_files_widget = listbox_widget_loaded_files

    def _delete_source(self, file_id, *args, **kwargs):
        file_id = file_id.split(':')[-1].strip()
        print('_delete_source'.upper(), file_id)
        self.session.remove_file(file_id)
        self.update_all()


    #===========================================================================
    def _get_data_file_path(self, sampling_type):
        """
        Created     20180821
        """
        open_directory = self._get_open_directory()
            
        file_path = filedialog.askopenfilename(initialdir=open_directory, 
                                               filetypes=[('GISMO-file ({})'.format(sampling_type), '*.txt')])

        if file_path:
            self._set_open_directory(file_path)
            old_sampling_type = self.combobox_widget_sampling_type.get_value() 
            self.combobox_widget_sampling_type.set_value(sampling_type)
            self.stringvar_data_file.set(file_path)
            
            # Check settings file path
            settings_file_path = self.combobox_widget_settings_file.get_value()
            # if not settings_file_path and sampling_type != old_sampling_type:
            # print('sampling_type', sampling_type)
            # print(self.settings['directory']['Default {} settings'.format(sampling_type)])
            # print('-')
            # print(self.combobox_widget_settings_file.items)
            # print(self.settings['directory']['Default {} settings'.format(sampling_type)])
            self.combobox_widget_settings_file.set_value(self.settings['directory']['Default {} settings'.format(sampling_type)])

            # User settings
            self.latest_loaded_sampling_type = sampling_type
            user_settings_file = self.user.settingsfile.get(sampling_type)
            if user_settings_file:
                self.combobox_widget_settings_file.set_value(user_settings_file)

            self.button_load_file.configure(state='normal')
            self.info_popup.show_information(core.texts.data_file_selected(username=self.user.name))

            if 'fixed platform' in sampling_type.lower():
                self.entry_widget_platform_depth.enable_widget()
                temp_file_id = os.path.basename(file_path)[:10]
                depth = self.user.sampling_depth.setdefault(temp_file_id, 1)
                self.entry_widget_platform_depth.set_value(depth)
            else:
                self.entry_widget_platform_depth.disable_widget()
        else:
            self.button_load_file.configure(state='disabled')
            self.entry_widget_platform_depth.disable_widget()
            
    #===========================================================================
    def _import_settings_file(self):

        open_directory = self._get_open_directory()
            
        file_path = filedialog.askopenfilename(initialdir=open_directory, 
                                                filetypes=[('GISMO Settings file','*.ini')])
        self._set_open_directory(file_path)

        self.settings_files.import_file(file_path)
        self._update_settings_combobox_widget()

    def _get_open_directory(self):
        return self.user.path.setdefault('open_directory', self.settings['directory']['Input directory'])

    def _set_open_directory(self, directory):
        if os.path.isfile(directory):
            directory = os.path.dirname(directory)
        self.user.path.set('open_directory', directory)


    #===========================================================================
    def _load_file(self):

        def load_file(**kwargs):
            self.update_help_information('')
            self.button_load_file.configure(state='disabled')

            data_file_path = self.stringvar_data_file.get()
            settings_file = self.combobox_widget_settings_file.get_value()
            settings_file_path = self.settings_files.get_path(settings_file)
            sampling_type = self.combobox_widget_sampling_type.get_value()

            self.session.load_file(sampling_type=sampling_type,
                                   data_file_path=data_file_path,
                                   settings_file_path=settings_file_path,
                                   reload=False,
                                   root_directory=self.root_directory,
                                   **kwargs)

            # Update user settings
            if self.latest_loaded_sampling_type:
                self.user.settingsfile.set(self.latest_loaded_sampling_type,
                                           self.combobox_widget_settings_file.get_value())

            # Remove data file text
            self.stringvar_data_file.set('')

            self._update_loaded_files_widget()
            self.update_all()
            self.button_load_file.configure(state='normal')

            self.update_help_information('File loaded! Please continue.')

        self.reset_help_information()
        data_file_path = self.stringvar_data_file.get()
        settings_file = self.combobox_widget_settings_file.get_value()
        settings_file_path = self.settings_files.get_path(settings_file)

        sampling_type = self.combobox_widget_sampling_type.get_value()
        
        if not all([data_file_path, settings_file_path]): 
            self.update_help_information('No file selected!', fg='red')
            return

        # Load file
        try:
            load_file()
            # self.run_progress(load_file, message='Loading file...please wait...')
        except GISMOExceptionMissingPath as e:
            gui.show_information('Invalid path',
                                 'The path "{}" given in i settings file "{} can not be found'.format(e.message,
                                                                                                      settings_file_path))
            self.update_help_information('Please try again with a different settings file.')

        except GISMOExceptionMissingInputArgument as e:
            # print(e.message, '#{}#'.format(e.message), type(e.message))
            if 'depth' in e.message:
                platform_depth = self.entry_widget_platform_depth.get_value()
                if not platform_depth:
                    gui.show_information('No depth found!', 'You need to provide platform depth for this sampling type!')
                    return
                load_file(depth=platform_depth)

        except Exception:
            gui.show_information('Load file error',
                                 'Something went wrong when trying to load file. Maybe you have provided the wrong Settings file?')



            # # Load file
            # try:
            #     self.update_help_information('Loading file...please wait...', fg='red')
            #     all_ok = self.session.load_file(sampling_type=sampling_type,
            #                                     file_path=data_file_path,
            #                                     settings_file_path=settings_file_path,
            #                                     reload=False)
            #
            # except GISMOExceptionMissingPath as e:
            #     gui.show_information('Invalid path',
            #                          'The path "{}" given in i settings file "{} can not be found'.format(e.message,
            #                                                                                               settings_file_path))
            #     self.update_help_information('Please try again with a different settings file.')
            #     return
            #
            # self._update_loaded_files_widget()
            #
            # self.update_all()
            #
            # # Update user settings
            # if self.latest_loaded_sampling_type:
            #     self.user.settingsfile.set(self.latest_loaded_sampling_type,
            #                                self.combobox_widget_settings_file.get_value())
            #
            # self.update_help_information('File loaded! Please continue by selecting a parameter.')

    def _update_loaded_files_widget(self):
        loaded_files = [] 
        for sampling_type in self.session.get_sampling_types():
            for file_id in self.session.get_file_id_list(sampling_type):
                loaded_files.append('{}: {}'.format(sampling_type, file_id))
        self.listbox_widget_loaded_files.update_items(loaded_files)


    def get_loaded_files_list(self):
        """
        Returns a list with the items in self.listbox_widget_loaded_files
        :return:
        """
        return self.listbox_widget_loaded_files.items[:]

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
        self.bind("<Control-b>", lambda event: self.show_frame(gui.PageFixedPlatforms))

    
    
    
    
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
        Created     20180822
        """ 
        self.info_widget.set_text(text, **kwargs)
        
        
    #===========================================================================
    def reset_help_information(self):
        """
        Created     20180822
        """ 
        self.info_widget.reset()
        
    
    #===========================================================================
    def update_all(self):
        
        for page_name, frame in self.frames.items():
            if self.pages_started[page_name]:
                print('page_name', page_name)
                frame.update_page()
            # try:
            #     if self.pages_started[page_name]:
            #         frame.update_page()
            # except:
            #     pass
    
    #===========================================================================
    def _set_menubar(self):
        """
        Method sets up the menu bar at the top och the Window.
        """
        self.menubar = tk.Menu(self)
        
        #-----------------------------------------------------------------------
        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label=u'Home',
                                   command=lambda: self.show_frame(gui.PageStart))
        self.file_menu.add_separator()
        self.file_menu.add_command(label=u'Quit', command=self.quit_toolbox)
        self.menubar.add_cascade(label=u'File', menu=self.file_menu)
        
        
        #-----------------------------------------------------------------------
        # Goto menu
        self.goto_menu = tk.Menu(self.menubar, tearoff=0)
        #-----------------------------------------------------------------------

        if 'gui.page_ferrybox' in sys.modules:
            self.goto_menu.add_command(label='Ferrybox',
                                       command=lambda: self.show_frame(gui.PageFerrybox))
        if 'gui.page_fixed_platforms' in sys.modules:
            self.goto_menu.add_command(label='Fixed platforms',
                                       command=lambda: self.show_frame(gui.PageFixedPlatforms))
        if 'gui.page_time_series' in sys.modules:
            self.goto_menu.add_command(label='Time series',
                                       command=lambda: self.show_frame(gui.PageTimeSeries))

        self.menubar.add_cascade(label='Goto', menu=self.goto_menu)

        # -----------------------------------------------------------------------
        # Users menu
        self.user_menu = tk.Menu(self.menubar, tearoff=0)

        self._update_menubar_users()

        self.menubar.add_cascade(label='Users', menu=self.user_menu)

        #-----------------------------------------------------------------------
        # Help menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label='About',
                                   command=lambda: self.show_frame(gui.PageAbout))
        self.menubar.add_cascade(label='Help', menu=self.help_menu)
        
        #-----------------------------------------------------------------------
        # Insert menu
        self.config(menu=self.menubar)

    def _update_menubar_users(self):
        # delete old entries
        for k in range(100):
            try:
                self.user_menu.delete(0)
            except:
                break
        # Add items

        # User settings
        self.user_menu.add_command(label='User settings',
                                   command=lambda: self.show_frame(gui.PageUser))
        self.user_menu.add_separator()

        # All users
        for user in self.user_manager.get_user_list():
            self.user_menu.add_command(label='Change to user: {}'.format(user),
                                       command=lambda x=user: self._change_user(x))
        self.user_menu.add_separator()

        # New user
        self.user_menu.add_command(label='Create new user',
                                   command=self._create_new_user)

        # Import user
        # self.user_menu.add_command(label='Import user',
        #                            command=None)


    def _create_new_user(self):

        def _create_user():
            source_user = widget_source_user.get_value().strip()
            new_user_name = widget_new_user_name.get_value().strip()
            if not new_user_name:
                gui.show_information('Create user', 'No user name given!')
                return
            if not source_user:
                source_user = None
            try:
                self.user_manager.add_user(new_user_name, source_user)
                if intvar_load_user.get():
                    self._change_user(new_user_name)
                self._update_menubar_users()
            except GUIExceptionUserError as e:
                gui.show_error('Creating user', '{}\nUser not created. Try again!'.format(e.message))
            popup_frame.destroy()

        def _cancel():
            popup_frame.destroy()

        popup_frame = tk.Toplevel(self)
        current_user_list = [''] + self.user_manager.get_user_list()

        grid = dict(sticky='w',
                    padx=5,
                    pady=5)

        widget_source_user = tkw.ComboboxWidget(popup_frame, title='Create copy of user', items=current_user_list, **grid)
        widget_new_user_name = tkw.EntryWidget(popup_frame, row=1, **grid)

        intvar_load_user = tk.IntVar()
        widget_checkbutton_load_user = tk.Checkbutton(popup_frame, text="Load new user", variable=intvar_load_user)
        widget_checkbutton_load_user.grid(row=1, column=1, **grid)
        intvar_load_user.set(1)

        widget_button_done = tk.Button(popup_frame, text='Create user', command=_create_user)
        widget_button_done.grid(row=2, column=0, **grid)
        widget_button_done = tk.Button(popup_frame, text='Cancel', command=_cancel)
        widget_button_done.grid(row=2, column=1, **grid)
        tkw.grid_configure(popup_frame, nr_rows=3, nr_columns=2)

    def _import_user(self):
        pass

    def _change_user(self, user_name):
        if user_name == self.user.name:
            return
        self.user_manager.set_user(user_name)
        self.user = self.user_manager.user
        self.info_popup = gui.InformationPopup(self)

        tk.Tk.wm_title(self, 'GISMO Toolbox, user: {}'.format(self.user.name))

        # Save startup user in settings
        self.settings.change_setting('user', 'Startup user', user_name)
        self.settings.save_settings()

        # Make updates
        self.make_user_updats()

    def make_user_updats(self):
        self.update_all()

    def _update_program_title(self):
        tk.Tk.wm_title(self, 'GISMOtoolbox (user: {}) :: {}'.format(self.user.name, self._get_title(self.active_page)))


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
        # self.withdraw()
        if not self.pages_started[page]:
            # self.run_progress_in_toplevel(frame.startup, 'Opening page, please wait...')
            frame.startup()
            self.pages_started[page] = True
        print('CALL UPDATE PAGE', frame)
        frame.update_page()
        # self.deiconify()
#             try:
#                 frame.update()
#             except:
#                 Log().information(u'%s: Could not update page.' % title)
                
        #-----------------------------------------------------------------------
        if load_page:
            frame.tkraise()
            self.previous_page = self.active_page
            self.active_page = page
            self._update_program_title()
            # Check page history
            if page in self.page_history:
                self.page_history.pop()
                self.page_history.append(page)
                
                
        try:
            if self.active_page == gui.PageCTD:
                self.notebook_load.select_frame('CTD files')
                
        except:
            pass
        self.update()


    def _show_frame(self, page):
        self.withdraw()
        # self._show_frame(page)
        self.run_progress_in_toplevel(lambda x=page: self._show_frame(x), 'Opening page, please wait...')
        self.deiconify()


#     def show_frame(self, page):
#         """
#         This method brings the given Page to the top of the GUI.
#         Before "raise" call frame startup method.
#         This is so that the Page only loads ones.
#         """
# #         if page == PageAdmin and not self.admin_mode:
# #             page = PagePassword
#
#         load_page = True
#         frame = self.frames[page]
#
#         self.withdraw()
#         title = self._get_title(page)
#         if not self.pages_started[page]:
#             frame.startup()
#             self.pages_started[page] = True
#
#
#         frame.update_page()
# #             try:
# #                 frame.update()
# #             except:
# #                 Log().information(u'%s: Could not update page.' % title)
#
#         #-----------------------------------------------------------------------
#         if load_page:
#             frame.tkraise()
#             tk.Tk.wm_title(self, u'GISMO Toolbox: %s' % title)
#             self.previous_page = self.active_page
#             self.active_page = page
#
#             # Check page history
#             if page in self.page_history:
#                 self.page_history.pop()
#                 self.page_history.append(page)
#
#
#         try:
#             if self.active_page == gui.PageCTD:
#                 self.notebook_load.select_frame('CTD files')
#
#         except:
#             pass
#
#         self.update()
#         self.deiconify()

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
            return ''
    
    #===========================================================================
    def _create_titles(self):
        self.titles = {}
        
        try:
            self.titles[gui.PageFerrybox] = 'Ferrybox'
        except:
            pass
        
        try:
            self.titles[gui.PageFixedPlatforms] = 'Buoy'
        except:
            pass
        
        try:
            self.titles[gui.PageCTD] = 'CTD'
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
    Updated 20181002    by
    """
    root_directory = os.path.dirname(os.path.abspath(__file__))
    users_directory = os.path.join(root_directory, 'users')
    log_directory = os.path.join(root_directory, 'log')
    default_settings_file_path = os.path.join(root_directory, 'system/settings.ini')

    if not os.path.exists(log_directory):
        os.mkdir(log_directory)

    sampling_types_factory = gismo.sampling_types.PluginFactory()
    qc_routines_factory = gismo.qc_routines.PluginFactory()

    app = App(user='default', # User here is the for example the computer name. Used only in gismo session.
              root_directory=root_directory,
              users_directory=users_directory,
              log_directory=log_directory,
              default_settings_file_path=default_settings_file_path,
              sampling_types_factory=sampling_types_factory,
              qc_routines_factory=qc_routines_factory)
    if not app.all_ok:
        return 
    app.focus_force()
    app.mainloop()
    return app
    
if __name__ == '__main__':
    app = main()






