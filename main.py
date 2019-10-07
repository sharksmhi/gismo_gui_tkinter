# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

# To use basemap you might need to install Microsoft Visual C++: https://visualstudio.microsoft.com/visual-cpp-build-tools/
import plugins
# print(plugins.MODULE_LIST)
import tkinter as tk
# print(MODULE_LIST)
# from tkinter import ttk
# from tkinter import filedialog
#
import os
import sys
import socket
import importlib
#
# import matplotlib.pyplot as plt
#
import gui
import core
#
# from libs.sharkpylib.gismo import GISMOsession
#
# from libs.sharkpylib import gismo
from libs.sharkpylib import loglib
import libs.sharkpylib.tklib.tkinter_widgets as tkw
#
# from libs.sharkpylib.gismo.exceptions import *
from core.exceptions import *
#
# import threading
#
ALL_PAGES = dict()
ALL_PAGES['PageStart'] = gui.PageStart
ALL_PAGES['PageAbout'] = gui.PageAbout

# Initiate plugins
PLUGINS = {}
for plugin in plugins.PLUGIN_LIST:
    PLUGINS[plugin] = importlib.import_module('plugins.{}'.format(plugin), '.')
    plugin_app = PLUGINS[plugin].app.App
    ALL_PAGES[plugin] = plugin_app
    ALL_PAGES[plugin] = plugin_app

APP_TO_PAGE = dict()
for plugin_name, plugin_app in ALL_PAGES.items():
    APP_TO_PAGE[plugin_app] = plugin_name


    # PLUGINS[plugin] = eval('plugins.{}'.format(plugin))
    # eval('ALL_PAGES.add(plugins.{}.App)'.format(plugin))

# TODO: Check required constants in plugins


class MainApp(tk.Tk):
    """
    This class contains the main window (page), "container", for 
    the GISMOtoolbox application.
    Additional pages in the application are stored under self.frames. 
    The container is the parent frame that is passed to other pages.
    self is also passed to the other pages objects and should there be given the name
    "self.controller". 
    Toolboxsettings and logfile can be reached in all page objects by calling
    "self.controller.settings" and "self.controller.logfile" respectively.
    """

    # ===========================================================================
    def __init__(self,
                 users_directory='',
                 root_directory='',
                 log_directory='',
                 mapping_files_directory='',
                 default_settings_file_path='',
                 *args, **kwargs):
        """
        Updated 20181002
        """
        self.version = '2019.10.1'

        tk.Tk.__init__(self, *args, **kwargs)
        self.withdraw()

        if not all([users_directory, root_directory, log_directory]):
            raise AttributeError

        # Load settings and constants (singletons)
        self.app_directory = os.path.dirname(os.path.abspath(__file__))
        self.root_directory = root_directory
        self.users_directory = users_directory
        self.log_directory = log_directory
        self.mapping_files_directory = mapping_files_directory

        # Setting upp GUI logger
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        # for file_name in os.listdir(self.log_directory):
        #     if file_name.endswith('.log'):
        #         try:
        #             os.remove(os.path.join(self.log_directory, file_name))
        #         except:
        #             pass

        # self.logger = loglib.get_logger(name='gismo_main')
        # TODO: When to clear log files?
        self.logger = loglib.get_logger(name='gismo_main',
                                        logfiles=[dict(level='DEBUG',
                                                       file_path=os.path.join(self.log_directory,
                                                                              'main_debug.log')),
                                                  dict(level='WARNING',
                                                       file_path=os.path.join(self.log_directory,
                                                                              'main_warning.log')),
                                                  dict(level='ERROR',
                                                       file_path=os.path.join(self.log_directory,
                                                                              'main_error.log'))
                                                  ])
        # self.logger_object = Logger(name='gismo_gui', level='DEBUG')
        # self.logger_object.add_logfile(file_path=os.path.join(self.log_directory, 'gismo_gui_debug.log'), level='DEBUG')
        # self.logger_object.add_logfile(file_path=os.path.join(self.log_directory, 'gismo_gui_warning.log'),
        #                                level='WARNING')
        # self.logger_object.add_logfile(file_path=os.path.join(self.log_directory, 'gismo_gui_error.log'), level='ERROR')
        # self.logger = self.logger_object.get_logger()
        self.logger.debug('=' * 100)
        # # Format
        # formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(plugin)s (row=%(lineno)d)\t%(message)s')
        #
        #
        # # Main gui logger
        # gui_logger = logging.getLogger('gui_logger')
        # gui_logger.setLevel(logging.DEBUG)
        #
        # # File logger
        # logger_file_path = os.path.join(self.log_directory, 'gismo_gui_tkinter.log')
        # file_handler = logging.FileHandler(logger_file_path)
        # file_handler.setLevel(logging.WARNING)
        # file_handler.setFormatter(formatter)
        #
        # # Console logger
        # # console = logging.StreamHandler()
        # # console.setLevel(logging.ERROR)
        # # console.setFormatter(formatter)
        #
        # # Add handlers
        # gui_logger.addHandler(file_handler)
        # # gui_logger.addHandler(console)
        #
        #
        # gui_logger.info('Starting application')

        # Load paths
        self.paths = core.Paths(self.app_directory)

        # Load settings files object
        # self.settings_files = core.SettingsFiles(self.paths.directory_settings_files)
# TODO: See if root directory and Settings are necessary
        self.settings = core.Settings(default_settings_file_path=default_settings_file_path,
                                      root_directory=self.root_directory)

        self._load_user()

        # # if startup_user
        # self.user_manager.set_user(startup_user)
        #
        #
        # if startup_user == 'default':  # not in self.user_manager.get_user_list():
        #     self.user_manager.set_user('default', create_if_missing=True)
        #     self.settings.change_setting('user', 'Startup user', self.computer_name)
        #     self.settings.save_settings()
        # self.user_manager.set_user(self.computer_name, create_if_missing=True)
        # self.user = self.user_manager.user

        # plt.style.use(self.user.layout.setdefault('plotstyle', self.user.layout.setdefault('plotstyle',
        #                                                                                    self.settings['default'][
        #                                                                                        'plotstyle'])))

        # self.boxen = Boxen(open_directory=self.settings['directory']['Input directory'])
        # self.boxen = core.Boxen(self, root_directory=self.root_directory)
        # self.session = GISMOsession(root_directory=self.root_directory,
        #                             users_directory=self.users_directory,
        #                             log_directory=self.log_directory,
        #                             mapping_files_directory=self.mapping_files_directory,
        #                             settings_files_directory=self.settings_files_directory,
        #                             user=user,
        #                             sampling_types_factory=sampling_types_factory,
        #                             qc_routines_factory=qc_routines_factory,
        #                             save_pkl=False)

        #        CMEMSparameters(self.settings['directory']['CMEMS parameters'])
        #        CMEMSstations(self.settings['directory']['CMEMS stations'])
        # self.default_platform_settings = None
        # self.default_platform_settings = gismo.sampling_types.SamplingTypeSettings(self.settings['directory']['Default ferrybox settings'],
        #                                                                            root_directory=self.root_directory)

        screen_padx = self.settings['general']['Main window indent x']
        screen_pady = self.settings['general']['Main window indent y']

        self.info_popup = gui.InformationPopup(self)

        # Override "close window (x)".
        # Override "close window (x)".
        # If this is not implemented the program is not properly closed.
        self.protocol('WM_DELETE_WINDOW', self.quit_toolbox)

        # Set geometry, title etc.
        #        self.geometry(u'%sx%s+0+0' % (self.winfo_screenwidth(),
        #                                     self.winfo_screenheight()))
        self.geometry('%sx%s+0+0' % (self.winfo_screenwidth() - screen_padx,
                                     self.winfo_screenheight() - screen_pady))
        #         tk.Tk.iconbitmap(self, default=u'D:/Utveckling/w_sharktoolbox/data/logo.ico')
        # TODO: Icon does not work
        self._create_titles()

        self.all_ok = True

        self.active_page = None
        self.previous_page = None
        # self.admin_mode = False
        self.progress_running = False
        self.progress_running_toplevel = False

        self.latest_loaded_sampling_type = ''

        #        self.sv = tk.StringVar()
        self._set_frame()

        # Make menu at the top
        self._set_menubar()

        self.startup_pages()

        # Show start page given in settings.ini
        self.page_history = ['PageAbout']
        self.show_frame('PageStart')

        self.update_all()
        self.deiconify()

    def get_root_window_position(self):
        return dict(x=self.winfo_x(),
                    y=self.winfo_y(),
                    w=self.winfo_width(),
                    h=self.winfo_height())

    def _load_user(self):
        # Load user
        self.user_manager = core.UserManager(os.path.join(self.app_directory, 'users'))
        self.computer_name = 'my_computer'
        try:
            self.computer_name = socket.gethostname()
        except:
            pass
        default_user = self.settings.get('user', {}).get('Startup user', 'default')
        startup_user = self.computer_name
        self.user_manager.set_user('default', create_if_missing=True)
        self.user = self.user_manager.user
        if default_user == 'default':
            if startup_user not in self.user_manager.get_user_list():
                self.user_manager.add_user(startup_user, default_user)
        else:
            startup_user = default_user
        # print('startup_user', startup_user)
        self.settings.change_setting('user', 'Startup user', startup_user)
        self.settings.save_settings()
        self.user_manager.set_user(startup_user, create_if_missing=True)
        self.user = self.user_manager.user

    # ==========================================================================
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

        # ----------------------------------------------------------------------
        # Frame top
        # Create container in that will hold (show) all frames
        self.container = tk.Frame(self.frame_top)
        self.container.grid(row=0, column=0, sticky="nsew")
        tkw.grid_configure(self.frame_top)

        # ----------------------------------------------------------------------
        # Frame mid
        self.frame_mid_left = tk.Frame(self.frame_mid)
        self.frame_mid_right = tk.Frame(self.frame_mid)

        # Grid
        self.frame_mid_left.grid(row=0, column=0, sticky="nsew")
        self.frame_mid_right.grid(row=0, column=1, sticky="nsew")

        # Gridconfigure
        tkw.grid_configure(self.frame_mid, nr_columns=2)

        # ----------------------------------------------------------------------
        # Frame bot
        self._set_frame_bot()

    def _set_frame_bot(self):
        self.frame_info = tk.Frame(self.frame_bot)
        self.frame_info.grid(row=0, column=0, sticky="nsew")

        # ttk.Separator(self.frame_bot, orient=tk.VERTICAL).grid(row=0, column=1, sticky='ns')
        # TODO: Progressbar deactivated. Threading not working as expected.
        self.frame_progress = tk.Frame(self.frame_bot)
        # self.frame_progress.grid(row=0, column=2, sticky="nsew")
        self.progress_widget = tkw.ProgressbarWidget(self.frame_progress, sticky='nsew')

        self.info_widget = tkw.LabelFrameLabel(self.frame_info, pack=False)

        tkw.grid_configure(self.frame_info)
        # tkw.grid_configure(self.frame_progress)

        tkw.grid_configure(self.frame_bot)
        # tkw.grid_configure(self.frame_bot, nr_columns=3, c0=20, c2=4)

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
            self.progress_widget_toplevel = tkw.ProgressbarWidget(self.frame_toplevel_progress, sticky='nsew',
                                                                  in_rows=True)
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

    # ===========================================================================
    def startup_pages(self):
        # Tuple that store all pages

        self.pages_started = {}

        # Dictionary to store all frame classes
        self.frames = {}

        # Looping all pages to make them active.
        for page_name, Page in ALL_PAGES.items():  # Capital P to emphasize class
            # Destroy old page if called as an update
            try:
                self.frames[page_name].destroy()
                print(page_name, u'Destroyed')
            except:
                pass
            frame = Page(self.container, self)
            frame.grid(row=0, column=0, sticky="nsew")

            self.container.rowconfigure(0, weight=1)
            self.container.columnconfigure(0, weight=1)

            self.frames[page_name] = frame

        self.activate_binding_keys()


    # ===========================================================================
    def _quick_run_F1(self, event):
        pass

    # ===========================================================================
    def _quick_run_F2(self, event):
        pass

    # ===========================================================================
    def _quick_run_F3(self, event):
        pass

    # ===========================================================================
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
        self.bind("<Control-u>", lambda event: self.show_frame(gui.PageUser))

    def update_help_information(self, text='', **kwargs):
        """
        Created     20180822
        """
        kw = dict(bg=self.cget('bg'),
                  fg='black')
        kw.update(kwargs)
        self.info_widget.set_text(text, **kw)
        self.logger.debug(text)

    def reset_help_information(self):
        """
        Created     20180822
        """
        self.info_widget.reset()

    def update_all(self):

        for page_name, frame in self.frames.items():
            if self.pages_started.get(page_name):
                frame.update_page()

    def _set_menubar(self):
        """
        Method sets up the menu bar at the top och the Window.
        """
        self.menubar = tk.Menu(self)

        # -----------------------------------------------------------------------
        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label=u'Home',
                                   command=lambda: self.show_frame('PageStart'))
        self.file_menu.add_separator()
        self.file_menu.add_command(label=u'Quit', command=self.quit_toolbox)
        self.menubar.add_cascade(label=u'File', menu=self.file_menu)

        # -----------------------------------------------------------------------
        # Plugins menu
        self.plugins_menu = tk.Menu(self.menubar, tearoff=0)
        # -----------------------------------------------------------------------

        # ======================================================================================
        for name, plugin in PLUGINS.items():
            title = plugin.INFO.get('title')
            special_menu = tk.Menu(self.plugins_menu, tearoff=0)
            for sub_page in PLUGINS[name].INFO.get('sub_pages', []):
                special_menu.add_command(label=sub_page.get('title'),
                                         command=lambda x=name, y=sub_page.get('name'): self.show_subframe(x, y))
            self.plugins_menu.add_cascade(label=title, menu=special_menu)

        self.menubar.add_cascade(label='Plugins', menu=self.plugins_menu)
        # ======================================================================================

        # for name in PLUGINS:
        #     sub_pages_menu_list = []
        #     title = self.titles.get(name)
        #     self.plugins_menu.add_command(label=title,
        #                                   command=lambda x=name: self.show_frame(x))
        #     for subpage in PLUGINS[name].INFO.get('subpages', []):
        #         sub_name = subpage.get(name)
        #         sub_pages_menu = tk.Menu(self.plugins_menu, tearoff=0)
        #         sub_pages_menu.add_command(label=subpage.get('name'),
        #                                    command=lambda: self.show_subframe(name, sub_name))
        #
        #         sub_pages_menu_list.append(sub_pages_menu)
        #
        #     self.plugins_menu.add_cascade(label=title, menu=sub_pages_menu_list)
        #
        # self.menubar.add_cascade(label='Plugins', menu=self.plugins_menu)

        # -----------------------------------------------------------------------
        # Users menu
        self.user_menu = tk.Menu(self.menubar, tearoff=0)

        self._update_menubar_users()

        self.menubar.add_cascade(label='Users', menu=self.user_menu)

        # -----------------------------------------------------------------------
        # Help menu
        self.info_menu = tk.Menu(self.menubar, tearoff=0)
        self.info_menu.add_command(label='About',
                                   command=lambda: self.show_frame('PageAbout'))
        self.menubar.add_cascade(label='Info', menu=self.info_menu)

        # -----------------------------------------------------------------------
        # Insert menu
        self.config(menu=self.menubar)

    def _get_user_page_class(self, plugin_name):
        """
        Returns the class of the user page (PageUser) for the given plugin_name.
        If no plugin_app is given then the active page (active plugin) is checked for user page.
        If user page cannot be found None is returned.
        :param plugin:
        :return:
        """
        user_page_class = None
        if plugin_name:
            plugin_module = PLUGINS.get(plugin_name, None)
            if plugin_module:
                user_page_class = plugin_module.INFO.get('user_page_class', None)
            return user_page_class

    def get_app_class(self, plugin=None):
        """
        Returns the class of the app (App) for the given plugin.
        If user page cannot be found None is returned.
        :param plugin:
        :return:
        """
        if not plugin:
            return None
        return ALL_PAGES.get(plugin)
        # if plugin and 'plugins' in plugin.__name__:
        #     app_class = plugin.
        #     app_class = eval('{}.app.App'.format(plugin.__name__))
        #     return app_class
        # else:
        #     return None


    def _update_menubar_users(self):
        # delete old entries
        for k in range(100):
            try:
                self.user_menu.delete(0)
            except:
                break
        # Add items
        # print('self.active_page', self.active_page)
        # User settings
        user_page = self._get_user_page_class(self.active_page)
        if user_page:
            self.user_menu.add_command(label='User settings',
                                       command=lambda: self.show_plugin_user_page(self.active_page))
            # self.user_menu.entryconfig('User settings', state='normal')
        else:
            # Set random Page and disable
            self.user_menu.add_command(label='User settings',
                                       command=lambda: self.show_frame(gui.PageStart))
            self.user_menu.entryconfig('User settings', state='disabled')

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

        widget_source_user = tkw.ComboboxWidget(popup_frame, title='Create copy of user', items=current_user_list,
                                                **grid)
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
        self.make_user_updates()

    def make_user_updates(self):
        self.update_all()

    def _update_program_title(self):
        tk.Tk.wm_title(self, 'GISMOtoolbox (user: {}) :: {}'.format(self.user.name, self._get_title(self.active_page)))

    # ===========================================================================
    def show_plugin_user_page(self, active_page):
        """
        Method to display user pages in the given plugin.
        :param plugin:
        :return:
        """
        self.show_frame(active_page)
        user_page = self._get_user_page_class(active_page)
        self.frames[active_page].show_frame(user_page)

    def show_subframe(self, main_page, sub_page):
        print(0)
        self.show_frame(main_page)
        print(1)
        self.frames[main_page].show_frame(sub_page)
        print(2)

    # ===========================================================================
    def show_frame(self, page_name=None, page=None):
        """
        This method brings the given Page to the top of the GUI.
        Before "raise" call frame startup method.
        Before "raise" call frame startup method.
        This is so that the Page only loads ones.
        """
        #         if page == PageAdmin and not self.admin_mode:
        #             page = PagePassword

        load_page = True
        if page:
            page_name = APP_TO_PAGE[page]
        frame = self.frames[page_name]
        # self.withdraw()
        if not self.pages_started.get(page_name):
            # self.run_progress_in_toplevel(frame.startup, 'Opening page, please wait...')
            frame.startup()
            self.pages_started[page_name] = True
        # print('CALL UPDATE PAGE', frame)
        frame.update_page()
        # self.deiconify()
        #             try:
        #                 frame.update()
        #             except:
        #                 Log().information(u'%s: Could not update page.' % title)

        # -----------------------------------------------------------------------
        if load_page:
            frame.tkraise()
            self.previous_page = self.active_page
            self.active_page = page_name
            self._update_program_title()
            # Check page history
            if page_name in self.page_history:
                self.page_history.pop()
                self.page_history.append(page_name)

        self._update_menubar_users()

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

    # ===========================================================================
    def goto_previous_page(self, event):
        if self.previous_page:
            self.show_frame(self.previous_page)

            # ===========================================================================

    def previous_page(self, event):
        self.page_history.index(self.active_page)

    # ===========================================================================
    def update_app(self):
        """
        Updates all information about loaded series.
        """

        self.update_all()

    # ===========================================================================
    def quit_toolbox(self):
        # TODO: Not implemented. Should we?
        if self.settings.settings_are_modified:
            save_settings = tk.messagebox.askyesnocancel(u'Save core.Settings?',
                                                        u"""
                                                        You have made one or more changes to the 
                                                        toolbox settings during this session.
                                                        Do you want to change these changes permanent?
                                                        """)
            if save_settings == True:
                self.settings.save_settings()
                self.settings.settings_are_modified = False
            else:
                return

        self.destroy()  # Closes window
        self.quit()  # Terminates program

    # ===========================================================================
    def _get_title(self, page):
        if page in self.titles:
            return self.titles[page]
        else:
            return ''

    # ===========================================================================
    def _create_titles(self):
        self.titles = {}

        for name, plugin in PLUGINS.items():
            self.titles[name] = plugin.INFO.get('title')

    def get_plugins(self):
        return PLUGINS




"""
================================================================================
================================================================================
================================================================================
"""


class Boxen(object):
    """
    Updated 20180927    by Magnus Wenzer

    Class to hold constants, data and other fun stuff.
    """

    # ==========================================================================
    def __init__(self, *args, **kwargs):
        self.open_directory = kwargs.get('open_directory', '')
        self.loaded_files_widget = None

    # ==========================================================================
    def set_open_directory(self, directory):
        if os.path.exists(directory):
            self.open_directory = directory


def main():
    """
    Updated 20181002    by
    """
    root_directory = os.path.dirname(os.path.abspath(__file__))
    users_directory = os.path.join(root_directory, 'users')
    log_directory = os.path.join(root_directory, 'log')
    default_settings_file_path = os.path.join(root_directory, 'system/settings.ini')
    mapping_files_directory = os.path.join(root_directory, 'data/mapping_files')

    if not os.path.exists(log_directory):
        os.mkdir(log_directory)

    app = MainApp(root_directory=root_directory,
                  users_directory=users_directory,
                  log_directory=log_directory,
                  mapping_files_directory=mapping_files_directory,
                  default_settings_file_path=default_settings_file_path)
    if not app.all_ok:
        return 
    app.focus_force()
    app.mainloop()
    return app
    
if __name__ == '__main__':
    print('Version', )
    app = main()






