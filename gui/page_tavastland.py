# -*- coding: utf-8 -*-
import os
import datetime
import tkinter as tk
from tkinter import messagebox

import libs.sharkpylib.tklib.tkinter_widgets as tkw

import gui

from libs.sharkpylib.ferrybox import tavastland

#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

"""
================================================================================
================================================================================
================================================================================
"""
class PageTavastland(tk.Frame):
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
        self.settings = controller.settings
        self.logger = self.controller.logger
        self.log_directory = controller.log_directory

        self.handler = None

        self.default_import_directory = self.settings['directory']['Import directory']
        self.default_export_directory = self.settings['directory']['Export directory']

    #===========================================================================
    def startup(self):
        self._set_frame()
        self.update_page()
    
    #===========================================================================
    def update_page(self):
        # TODO: Update when changing user
        pass
        
    #===========================================================================
    def _set_frame(self):
        self.grid = dict(padx=5,
                    pady=5,
                    sticky='nsew')

        self.labelframe_file_inspection = tk.LabelFrame(self, text='File_inspection')
        self.labelframe_file_inspection.grid(row=0, column=0, columnspan=3, **self.grid)

        self.labelframe_source = tk.LabelFrame(self, text='Source')
        self.labelframe_source.grid(row=1, column=0, rowspan=2, **self.grid)

        self.labelframe_options = tk.LabelFrame(self, text='Merge options')
        self.labelframe_options.grid(row=1, column=1, rowspan=2, **self.grid)

        self.labelframe_merge_data = tk.LabelFrame(self, text='Merge data')
        self.labelframe_merge_data.grid(row=1, column=2, **self.grid)

        self.labelframe_export = tk.LabelFrame(self, text='Export')
        self.labelframe_export.grid(row=2, column=2, **self.grid)

        tkw.grid_configure(self, nr_rows=3, nr_columns=3)

        self._set_frame_file_inspection()
        self._set_frame_source()
        self._set_frame_options()
        self._set_frame_merge_data()
        self._set_frame_export()

        self._set_directories()
    
    def _set_frame_file_inspection(self):
        frame = self.labelframe_file_inspection
        self.notebook_widget_files = tkw.NotebookWidget(frame, frames=['MIT files', 'CO2 files', 'Files with errors'])
        tkw.grid_configure(frame)

        self.columns_files = ['File name', 'Start time', 'End time', 'File path', 'File size (kB)']
        self.table_widget_mit = tkw.TableWidget(self.notebook_widget_files.frame_mit_files,
                                                columns=self.columns_files,
                                                int_columns=['File size (kB)'])
        self.table_widget_co2 = tkw.TableWidget(self.notebook_widget_files.frame_co2_files,
                                                columns=self.columns_files,
                                                int_columns=['File size (kB)'])
        self.table_widget_err = tkw.TableWidget(self.notebook_widget_files.frame_files_with_errors,
                                                columns=self.columns_files,
                                                int_columns=['File size (kB)'])
        tkw.grid_configure(self.notebook_widget_files.frame_mit_files)
        tkw.grid_configure(self.notebook_widget_files.frame_co2_files)
        tkw.grid_configure(self.notebook_widget_files.frame_files_with_errors)

    def _set_frame_source(self):
        frame = self.labelframe_source

        self.directory_widget_mit = tkw.DirectoryWidgetLabelframe(frame,
                                                                  label='MIT directory',
                                                                  default_directory=self.default_import_directory,
                                                                  callback=self._save_settings_to_user,
                                                                  row=0, column=0, **self.grid)

        self.directory_widget_co2 = tkw.DirectoryWidgetLabelframe(frame,
                                                                  label='CO2 directory',
                                                                  default_directory=self.default_import_directory,
                                                                  callback=self._save_settings_to_user,
                                                                  row=1, column=0, **self.grid)

        self.button_inspect_file = tk.Button(frame, text='Inspect files', command=self._inspect_files)
        self.button_inspect_file.grid(row=2, column=0, **self.grid)

        tkw.grid_configure(frame, nr_rows=3)

    def _set_frame_options(self):
        frame = self.labelframe_options
        padx=10
        pady=10
        # self.booleanvar_use_time_span = tk.BooleanVar()
        # self.booleanvar_use_time_span.set(self.user.tavastland.setdefault('use_t_span', True))

        tk.Label(frame, text='Merge data from file or time span').grid(row=0, column=0, columnspan=2,
                                                                       sticky='w', padx=padx, pady=pady)
        self.use_widget = tkw.RadiobuttonWidget(frame,
                                                items=['mit-file', 'co2-file', 'time span'],
                                                target=self._toggle_use_time_span,
                                                sticky='w', padx=padx, pady=pady, columnspan=2)
        self.use_widget.set_value('time span')

        # self.checkbutton_use_time_span = tk.Checkbutton(frame,
        #                                                 text='Select time span',
        #                                                 variable=self.booleanvar_use_time_span,
        #                                                 command=self._toggle_use_time_span)
        # self.checkbutton_use_time_span.grid(row=1, column=0, sticky='w', padx=padx, pady=pady)

        self.time_widget_start = tkw.TimeWidget(frame, title='Start time',
                                                lowest_time_resolution='day', row=2, column=0,
                                                columnspan=2, sticky='nw')
        self.time_widget_end = tkw.TimeWidget(frame, title='End time',
                                              lowest_time_resolution='day', row=3, column=0,
                                              columnspan=2, sticky='nw')

        tk.Label(frame, text='Time merge tolerance (in seconds)').grid(row=4, column=0, sticky='w', padx=padx, pady=pady)

        self.time_widget_tolerance = tkw.EntryWidget(frame,
                                                     entry_type='int',
                                                     prop_entry={'width': 5},
                                                     callback_on_focus_out=self._save_settings_to_user,
                                                     row=4, column=1, sticky='w', padx=padx, pady=pady)
        self.time_widget_tolerance.set_value(self.user.tavastland.setdefault('t_delta', '30'))

        primary_file_type = self.user.tavastland.setdefault('primary_file_type', 'mit')
        self.primary_file_type_widget = tkw.ComboboxWidget(frame,
                                                           title='Primary file type',
                                                           items=['co2', 'mit'],
                                                           default_item=primary_file_type,
                                                           callback_target=self._save_settings_to_user,
                                                           row=5,
                                                           column=0,
                                                           columnspan=2,
                                                           sticky='nw')
        tkw.grid_configure(frame, nr_rows=6, nr_columns=2)

    def _set_frame_merge_data(self):
        frame = self.labelframe_merge_data
        r = 0

        r+=1

        # remove_areas_file = self.user.tavastland.setdefault('primary_file_type', 'co2')
        # self.remove_areas_widget = tkw.ComboboxWidget(frame,
        #                                                    title='Remove areas',
        #                                                    items=['co2', 'mit'],
        #                                                    default_item=primary_file_type,
        #                                                    row=2,
        #                                                    column=0,
        #                                                    sticky='nw')
        r += 1

        self.mask_area_file_widget = tkw.DirectoryWidgetLabelframe

        self.button_merge = tk.Button(frame, text='Merge data and calculate', command=self._merge_data)
        self.button_merge.grid(row=r, column=1, **self.grid)

        r+=1
        tkw.grid_configure(frame, nr_rows=r, nr_columns=1)

    def _set_frame_export(self):
        frame = self.labelframe_export

        self.type_widget = tkw.ListboxSelectionWidget(frame, row=0, column=0, columnspan=2, sticky='nw',
                                                      callback_set_default=self._set_default_row_selection)

        self.directory_widget_export = tkw.DirectoryWidget(frame,
                                                           default_directory=self.default_export_directory,
                                                           callback=self._save_settings_to_user,
                                                           row=1, column=0, sticky='nw')

        self.button_export = tk.Button(frame, text='Export data', command=self._export_data)
        self.button_export.grid(row=2, column=1, **self.grid)

        tkw.grid_configure(frame, nr_rows=3, nr_columns=1)

    def _set_default_row_selection(self):
        self.type_widget.deselect_all()
        default_value = self.controller.user_manager.get_default_user_settings('tavastland', 'deselected_types')
        if default_value:
            self.type_widget.move_items_to_selected(default_value)

    def _toggle_use_time_span(self):
        selected = self.use_widget.get_value()
        if 'time' in selected:
            self.time_widget_start.enable_widget()
            self.time_widget_end.enable_widget()
            self.time_widget_tolerance.enable_widget()
            #self.user.tavastland.set('use_t_span', True)
        else:
            self.time_widget_start.disable_widget()
            self.time_widget_end.disable_widget()
            self.time_widget_tolerance.disable_widget()
            #self.user.tavastland.set('use_t_span', False)

    def _merge_data(self):
        """
        Merge data and export.
        :return:
        """
        try:
            self.type_widget.update_items()
            source = self.use_widget.get_value()
            if 'time' in source:
                time_start = self.time_widget_start.get_time_object()
                time_end = self.time_widget_end.get_time_object()
                # Have to add the day as well
                time_end = time_end + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)


                if not all([time_start, time_end]):
                    gui.show_information('Missing input', 'You have not made all required options to merge data. '
                                                          'Merge canceled!')
                    return

                # Check time span
                selected_time_delta = time_end - time_start
                nr_days = self.user_manager.get_default_user_settings('tavastland', 'alert_t_delta_days')
                if not nr_days:
                    nr_days = 60
                if selected_time_delta.days > self.user.tavastland.setdefault('alert_t_delta_days', nr_days):
                    if not messagebox.askyesno('Time span warning!',
                                               'Your selected time is {} days. '
                                               'This might take som time to merge. '
                                               'Do you want to continue?'.format(selected_time_delta.days)):
                        self.controller.update_help_information('Merge canceled by user do to long time span.')
                        return
                # Set time range to work with
                self.handler.set_time_range(time_start=time_start, time_end=time_end)

            elif 'mit' in source:
                selection = self.table_widget_mit.get_selected()
                if not selection:
                    gui.show_information('No file selected', 'You have not selected any mit file to use for merge. '
                                                             'Merge canceled!')
                    return
                self.handler.set_time_range(file_id=selection['File name'], file_type='mit')
            elif 'co2' in source:
                selection = self.table_widget_co2.get_selected()
                if not selection:
                    gui.show_information('No file selected', 'You have not selected any co2 file to use for merge. '
                                                             'Merge canceled!')
                    return
                self.handler.set_time_range(file_id=selection['File name'], file_type='co2')

            time_delta_seconds = self.time_widget_tolerance.get_value()
            primary_file_type = self.primary_file_type_widget.get_value()
            if not all([time_delta_seconds, primary_file_type]):
                gui.show_information('Missing input', 'You have not made all required options to merge data. '
                                                      'Merge canceled!')
                return

            self.controller.update_help_information('Merging data. Please wait...', bg='red')
            if primary_file_type == 'mit':
                second_file_type = 'co2'
            else:
                second_file_type = 'mit'

            # Set timedelta
            self.handler.set_time_delta(seconds=int(time_delta_seconds))
            # Load data within time range
            try:
                self.handler.load_data()
            except tavastland.TavastlandExceptionNoCO2data:
                self.logger.debug('No CO2 data matches the given time!')
                gui.show_information('No match', 'No CO2 data matches the given time!')
                self.controller.update_help_information('No co2 data found!')
                return

            # Merge data
            self.handler.merge_data(primary_file_type, second_file_type)
            # Calculate pCO2
            self.handler.calculate_pCO2()

            type_items = self.handler.get_types_in_merge_data()
            deselected_types = self.user.tavastland.get('deselected_types')
            self.type_widget.update_items(type_items)
            self.type_widget.move_items_to_selected(deselected_types)

        except tavastland.TavastlandException as e:
            self.controller.update_help_information('Merge failed!')
            gui.show_error('Could not merge data!', e.message)
        except tavastland.TavastlandExceptionNoMatchWhenMerging as e:
            self.controller.update_help_information('No match between mit and co2 files!')
            gui.show_error('No match!', e.message)
        else:
            self.controller.update_help_information('Merge done!', bg='green')
        finally:
            self._save_time_to_user()

    def _export_data(self):
        directory = self.directory_widget_export.get_value()
        if not directory:
            gui.show_information('Missing input', 'Missing export directory. '
                                                  'Export canceled!')
            return

        self.controller.update_help_information('Exporting merge data. Please wait...', bg='red')
        # Save data
        deselected_types = self.type_widget.get_selected()
        all_types = self.type_widget.get_all_items()
        selected_types = [t for t in all_types if t not in deselected_types]
        try:
            file_path = self.handler.save_merge_data(directory=directory, co2_types=selected_types)

            self.user.tavastland.set('deselected_types', deselected_types)

            self.controller.update_help_information('Export done!', bg='green')
        except PermissionError as e:
            gui.show_error('PermissionError', e.message)
        else:
            gui.show_information('Export data', 'Merged data has been exported:\n{}'.format(file_path))


    def _set_directories(self):
        mit_directory = self.user.tavastland.setdefault('mit_directory', self.default_import_directory)
        self.directory_widget_mit.set_directory(mit_directory, call_target=False)

        co2_directory = self.user.tavastland.setdefault('co2_directory', self.default_import_directory)
        self.directory_widget_co2.set_directory(co2_directory, call_target=False)

        export_directory = self.user.tavastland.setdefault('export_directory', self.default_export_directory)
        self.directory_widget_export.set_directory(export_directory, call_target=False)

    def _save_settings_to_user(self):
        self.user.tavastland.set('export_directory', self.directory_widget_export.get_directory(), save=False)
        self.user.tavastland.set('mit_directory', self.directory_widget_mit.get_directory(), save=False)
        self.user.tavastland.set('co2_directory', self.directory_widget_co2.get_directory(), save=False)
        self.user.tavastland.set('primary_file_type', self.primary_file_type_widget.get_value(), save=False)
        self.user.tavastland.set('t_delta', str(self.time_widget_tolerance.get_value()), save=True) # Last one

    def _save_time_to_user(self):
        # self._save_settings_to_user()
        gui.communicate.sync_user_and_time_widgets(user_sub_object=self.user.tavastland,
                                                   time_widget_start=self.time_widget_start,
                                                   time_widget_end=self.time_widget_end,
                                                   source='widgets')
    
    def _inspect_files(self):
        """
        Create tavastland.FileHandler and loads import directories. Fills the table with information.
        :return:
        """

        mit_directory = self.directory_widget_mit.get_directory()
        co2_directory = self.directory_widget_co2.get_directory()
        if not all([mit_directory, co2_directory, os.path.exists(mit_directory), os.path.exists(co2_directory)]):
            gui.show_information('Invalid directories', 'Please check inport directories!')
            return

        self.controller.update_help_information('Inspecting MIT and CO2 files. Please wait...', bg='red')

        # Initiate handler
        try:
            self.handler = tavastland.FileHandler(mit_directory=mit_directory,
                                                  co2_directory=co2_directory,
                                                  log_info=dict(name='gismo_gui'))
        except tavastland.TavastlandException as e:
            self.logger.debug('Tavastland error: {}'.format(e.message))
            gui.show_information('Tavastland error', e.message)
            self.controller.update_help_information('Could not inspect files!')
        else:
            self.table_widget_mit.reset_table()
            self.table_widget_co2.reset_table()

            # Update tables
            mit_data, mit_error_data = self._get_table_data_from_df(self.handler.dfs['mit'], 'mit')
            self.table_widget_mit.set_table(mit_data)
            co2_data, co2_error_data = self._get_table_data_from_df(self.handler.dfs['co2'], 'co2')
            self.table_widget_co2.set_table(co2_data)
            self.controller.update_help_information('MIT and/or CO2 files have been updated')

            error_data = mit_error_data + co2_error_data
            self.table_widget_err.set_table(error_data)

            # Update time widgets
            from_time, to_time = self.handler.get_min_and_max_time()
            now = datetime.datetime.now()
            if to_time > now:
                to_time = now
            self.time_widget_start.set_valid_time_span(from_time, to_time)
            self.time_widget_end.set_valid_time_span(from_time, to_time)
            gui.communicate.sync_user_and_time_widgets(user_sub_object=self.user.tavastland,
                                                       time_widget_start=self.time_widget_start,
                                                       time_widget_end=self.time_widget_end,
                                                       source='user')

    def _get_table_data_from_df(self, df, file_type):
        files_with_errors = set(self.handler.get_files_with_errors(file_type))
        data = []
        error_data = []
        for i in df.index:
            data_line = []
            # File id
            file_id = df.at[i, 'file_id']
            time_start = df.at[i, 'time_start']
            time_end = df.at[i, 'time_end']
            data_line.append(file_id)
            # Time start
            try:
                data_line.append(time_start.strftime('%Y-%m-%d %H:%M:%S'))
            except:
                # Add to error list(set)
                files_with_errors.add(file_id)
                data_line.append(time_start)

            # Time end
            try:
                data_line.append(time_end.strftime('%Y-%m-%d %H:%M:%S'))
            except:
                # Add to error list(set)
                files_with_errors.add(file_id)
                data_line.append(time_end)
            # File path
            file_path = df.at[i, 'file_path']
            data_line.append(file_path)
            # File size
            data_line.append(str(int(os.path.getsize(file_path)/1000)))

            if file_id in files_with_errors:
                error_data.append(data_line)
            else:
                data.append(data_line)
        return data, error_data
