# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on Thu Mar 16 15:37:10 2017

@author:
"""
import numpy as np
import random

from . import tkinter_widgets as tkw

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon
from matplotlib.dates import DateFormatter, DayLocator 
from matplotlib.text import Text

import tkinter as tk 

matplotlib.use(u'TkAgg')
from mpl_toolkits.basemap import Basemap
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class MapWidget(object):
    """
        Class to display a basemap-map in figure or tkinter window.
        Options in constructor are:
            parent          give tkinter frame (optional)
            figure_size     set figure size in inches
            map_reslution   set map resolution
            ..._space       set size of area aroundthe map.
            toolbar         Set True to adds standard toolbar under the map.
                Map coordinates can be given in three ways:
                series_object_list    if given, map dimensions are taken from including series position
                map_area_name         name matching predefined areas in stb_core.Settings() settings.ini
                coordinates           coordinates as [min_lon, max_lon, min_lat, max_lat]
        """
    def __init__(self,
                 parent,
                 figsize=(2, 2),
                 map_resolution=u'l',
                 toolbar=False,
                 coordinates=[9, 31, 53, 66],
                 continent_color=[0.8, 0.8, 0.8],
                 ocean_color=None,
                 projection=u'merc',
                 dpi=100,
                 user=None,
                 **kwargs):
        self.parent = parent

        #        self.frame = tk.Frame(parent)
        #        self.frame.grid(row=row, column=column)
        self.figsize = figsize
        self.dpi = dpi
        self.map_resolution = map_resolution
        self.toolbar = toolbar
        self.user = user

        self.marker_order = []
        self.markers = {}
        self.map_items = {}
        self.event_dict = {}

        self.continent_color = continent_color
        self.ocean_color = ocean_color
        self.projection = projection

        self.title = kwargs.get('title', '')

        self.subplot_space = dict()
        self.subplot_space['left'] = kwargs.get('space_left', 0.05)
        self.subplot_space['right'] = 1 - kwargs.get('space_right', 0.05)
        self.subplot_space['top'] = 1 - kwargs.get('space_top', 0.12)
        self.subplot_space['bottom'] = kwargs.get('space_bottom', 0.05)


        self.coordinates = dict()
        self.coordinates['llcrnrlat'] = kwargs.get('min_lat', 53)
        self.coordinates['urcrnrlat'] = kwargs.get('max_lat', 66)
        self.coordinates['llcrnrlon'] = kwargs.get('min_lon', 9)
        self.coordinates['urcrnrlon'] = kwargs.get('max_lon', 31)

        self.markers = dict()

        self._set_frame()
        self._draw_map()
        self._add_to_tkinter()

    def _set_frame(self):
        self.frame = tk.Frame(self.parent)
        #                 self.frame.grid(row=0, column=0)
        self.frame.grid(row=0, column=0, sticky='nsew')
        tkw.grid_configure(self.frame)

    def _draw_map(self):
        """
        Draw map. Some options for the layout (like projection continent filling etc.) are fixed here.
        """
        self.fig = Figure(figsize=self.figsize, dpi=self.dpi)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(**self.subplot_space)

        # Set title
        self.title_handle = self.fig.suptitle(self.title, fontsize=10, x=0.5, y=1.0)

        self.m = Basemap(resolution=self.map_resolution,
                         projection=self.projection,
                         ax=self.ax,
                         **self.coordinates)

        # self.m.etopo()
        # self.m.shadedrelief()
        # self.m.bluemarble()

        self.m.drawcoastlines(linewidth=0.33)
        self.m.drawcountries(linewidth=0.2)
        self.m.fillcontinents(color=self.continent_color, zorder=3)
        self.m.drawmapboundary(fill_color=self.ocean_color)

    # ==========================================================================
    def _add_to_tkinter(self):
        """
        Adds map and toolbar (if selected in constructor) to the given frame.
        """
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        # self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def add_simple_line(self, lat, lon, marker_id='simple_line', title='', **kwargs):
        """
        Adds a line to the map. lat and lon are lists or arrays.
        :param lat:
        :param lon:
        :return:
        """
        try:
            self.delete_handle(marker_id)
        except:
            pass

        x, y = self.m(lon, lat)
        handle = self.m.plot(x, y, zorder=10, **kwargs)

        self.markers[marker_id] = handle

        self.title_handle.set_text(title)

        self.canvas.draw()


    def delete_marker(self, marker_id, redraw=True):
        self.markers.pop(marker_id)
        self.canvas.draw()

    # ==========================================================================
    def delete_all_markers(self):

        for marker_id in self.markers:
            self.delete_marker(marker_id, redraw=False)
        # if self.marker_order:
        #     for marker in self.marker_order[:]:
        #         self.delete_marker(marker)

        self.canvas.draw()


"""
================================================================================
================================================================================
================================================================================
"""
class TkMap(object):
    """
    Class to display a basemap-map in figure or tkinter window. Also includes methodes to add and remove markers, texts, scatter plots etc. 
    Options in constructor are: 
        parent          give tkinter frame (optional)
        figure_size     set figure size in inches
        map_reslution   set map resolution
        ..._space       set size of area aroundthe map. 
        toolbar         Set True to adds standard toolbar under the map. 
            Map coordinates can be given in three ways:
            series_object_list    if given, map dimensions are taken from including series position
            map_area_name         name matching predefined areas in Settings() settings.ini
            coordinates           coordinates as [min_lon, max_lon, min_lat, max_lat]    
    """
     
    def __init__(self, 
                 parent, 
                 figsize=(2,2), 
                 map_resolution=u'i', 
                 left_space=0.05, 
                 right_space=0.05,
                 top_space=0.12, 
                 bottom_space=0.05, 
                 toolbar=False,  
                 boundries=None, 
                 continent_color=[0.8, 0.8, 0.8], 
                 projection=u'merc', 
                 dpi=100):
                 
        self.parent = parent
        
#        self.frame = tk.Frame(parent)
#        self.frame.grid(row=row, column=column)
        self.figsize = figsize  
        self.dpi = dpi
        self.map_resolution = map_resolution
        self.left_space = left_space 
        self.right_space = right_space
        self.top_space = top_space 
        self.bottom_space = bottom_space
        self.toolbar = toolbar
        
        self.marker_order = []
        self.markers = {}
        self.map_items = {}
        self.event_dict = {}
        self.boundries = None
        self.continent_color = continent_color
        self.projection = projection
        
        self.bindings = {}
        
        self._load_attributes()
        
        self.update_page(boundries, self.map_resolution)
        
       
    #==========================================================================
    def update_page(self, boundries, resolution):
        
        # Check existent boundries
        if boundries != self.boundries or all([resolution != self.map_resolution, resolution]):
            self.boundries = boundries
            self._get_boundries_from_coordinates(boundries)
            self.map_resolution = resolution
            
            # Destroy old frame
            try:
                self.frame.destroy()
                print(u'Figure and frame are removed in TkMap.update()')
            except:
                pass
        
            # create new frame and add fig
            self.frame = tk.Frame(self.parent)
#            self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.frame.grid(row=0, column=0, sticky='nsew')
            self.frame_toolbar = tk.Frame(self.parent)
            self.frame_toolbar.grid(row=1, column=0, sticky='nsew')
#            grid_configure(self.parent)
            self.fig = Figure(figsize=self.figsize, dpi=self.dpi)
            self._add_to_tkinter()

                
            self.delete_all_map_items()
            self._draw_map()
            
        self._update_markers()
        
        # Add event bindings
        self.fig.canvas.mpl_connect('resize_event', self._on_resize)
        for event_type in self.event_dict:
            self.fig.canvas.mpl_connect(self.event_dict[event_type][u'event_type'], 
                                        self.event_dict[event_type][u'event_function'])
    
    #==========================================================================
    def _load_attributes(self):   
        self.legend_items = {1: {u'handle':[], u'label':[]}, 
                             2: {u'handle':[], u'label':[]}, 
                             3: {u'handle':[], u'label':[]}}
        
    #==========================================================================
    def add_legend(self, 
#                    loc=u'center', 
                   position=[0.88, 0.008], 
                   color=None, 
                   number_of_markers=1, 
                   marker_color=u'white', 
                   legend_nr=1, 
                   fontsize=8):
        
        if not position:
            axbox = self.ax.get_position()
            position = [axbox.x0+0.005, axbox.y0+0.005]
        loc=u'center'

        self.legend_position = position
        self.legend = self.fig.legend(self.legend_items[legend_nr][u'handle'], 
                                        self.legend_items[legend_nr][u'label'], 
                                        ncol=len(self.legend_items[legend_nr][u'handle']), 
                                        bbox_to_anchor=position, 
                                        loc=loc,    
                                        prop={'size':fontsize}, 
                                        scatterpoints=number_of_markers)
        
        if not color:
            color = self.fig.get_facecolor()
        self.legend.get_frame().set_facecolor(color)
        self.legend.get_frame().set_edgecolor(color)
        
        if marker_color:
            for marker in self.legend.legendHandles:
                marker.set_facecolor(marker_color)
        
        self._reposition_items()
        self.redraw()
    
    #==========================================================================
    def _add_to_legend(self, legend_nr, marker_name, label):
        """
        Add legend text to marker for a potential legend. 
        """
        try:
            handle = self.markers[marker_name][u'handle']
            self.legend_items[legend_nr][u'handle'].append(handle)
            self.legend_items[legend_nr][u'label'].append(label)
        except:
            print(u'Could not add info to legend.')
           

    #==========================================================================
    def _update_markers(self):
        # Check if markers are active          
        if self.marker_order:
            markers_to_add = self.marker_order[:]
            for marker_name in markers_to_add:
                
                if 'line' in marker_name:
                    self.add_line(lat=self.markers[marker_name][u'lat'], 
                                            lon=self.markers[marker_name][u'lon'], 
                                            line_width=self.markers[marker_name][u'line_width'], 
                                            line_style=self.markers[marker_name][u'line_style'], 
                                            color=self.markers[marker_name][u'color'])

                elif 'marker' in marker_name:
                    self.add_markers(lat=self.markers[marker_name][u'lat'], 
                                            lon=self.markers[marker_name][u'lon'], 
#                                             marker_size=self.markers[marker_name][u'marker_size'], 
#                                             marker_type=self.markers[marker_name][u'marker_type'], 
#                                             fill_color=self.markers[marker_name][u'fill_color'], 
#                                             edge_color=self.markers[marker_name][u'edge_color'], 
#                                             line_width=self.markers[marker_name][u'line_width'],
                                            **self.markers[marker_name][u'kwargs'])
                
                elif 'scatter' in marker_name:
                    self.add_scatter(lat=self.markers[marker_name][u'lat'], 
                                    lon=self.markers[marker_name][u'lon'], 
                                    values=self.markers[marker_name][u'values'],
                                    divide=self.markers[marker_name][u'divide'],
                                    index=self.markers[marker_name][u'index'],
                                    marker_size=self.markers[marker_name][u'marker_size'], 
                                    marker_type=self.markers[marker_name][u'marker_type'], 
                                    color_map=self.markers[marker_name][u'color_map'], 
                                    edge_color=self.markers[marker_name][u'edge_color'], 
                                    line_width = self.markers[marker_name][u'line_width'], 
                                    **self.markers[marker_name][u'kwargs'])
                    if self.markers[marker_name][u'colorbar']:
                        self.add_colorbar(marker_name)
                      
                elif 'text' in marker_name:
                    self.add_text(lat=self.markers[marker_name][u'lat'], 
                                                  lon=self.markers[marker_name][u'lon'], 
                                                  text=self.markers[marker_name][u'text'], 
                                                  fontsize=self.markers[marker_name][u'fontsize'], 
                                                  color=self.markers[marker_name][u'color'], 
                                                  lat_offset=self.markers[marker_name][u'lat_offset'], 
                                                  lon_offset=self.markers[marker_name][u'lon_offset'], 
                                                  lat_offset_percent=self.markers[marker_name][u'lat_offset_percent'], 
                                                  lon_offset_percent=self.markers[marker_name][u'lon_offset_percent'], 
                                                  bbox=self.markers[marker_name][u'bbox'], 
                                                  ha=self.markers[marker_name][u'ha'],
                                                  va=self.markers[marker_name][u'va'])
                    
        self.redraw()
            
    #==========================================================================
    def redraw(self):
        if self.parent:
            self.canvas.draw()
        else:
            self.fig.show()

 
    #==========================================================================
    def _get_boundries_from_coordinates(self, coordinates):
        
        self.min_lon = coordinates[0]
        self.max_lon = coordinates[1]
        self.min_lat = coordinates[2]
        self.max_lat = coordinates[3]
        
    
    #==========================================================================
    def _within_boundry(self, lat, lon):
        if self.min_lon < lon < self.max_lon and self.min_lat < lat < self.max_lat:
            return True
        else:
            return False
     
    #==========================================================================
    def _draw_map(self):
        """
        Draw map. Some options for the layout (like projection continent filling etc.) are fixed here. 
        """
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=self.left_space, 
                                 right=1-self.right_space, 
                                 top=1-self.top_space, 
                                 bottom=self.bottom_space)
        
        self.m = Basemap(llcrnrlon=self.min_lon, 
                         llcrnrlat=self.min_lat, 
                         urcrnrlon=self.max_lon, 
                         urcrnrlat=self.max_lat,
                         resolution=self.map_resolution, projection=self.projection, ax=self.ax)
         
        self.m.drawcoastlines(linewidth = 0.33)
        self.m.drawcountries(linewidth = 0.2)
        self.m.fillcontinents(color=self.continent_color, zorder=3)
        

    #========================================================================== 
    def _add_to_tkinter(self):
        """
        Adds map and toolbar (if selected in constructor) to the given frame. 
        """
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
#         self.frame.grid_columnconfigure(0, weight=1)
        
        # Add toolbar
        if self.toolbar: 
            print('toolbar')
            self.map_toolbar = NavigationToolbar2TkAgg(self.canvas, self.frame_toolbar)
            self.map_toolbar.update()
            self.map_toolbar.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            
#        self.frame.rowconfigure(0, weight=100)
#        self.frame.rowconfigure(1, weight=1)
    
    #========================================================================== 
    def _reposition_items(self):
        
        ax_pos = self.ax.get_position()
        
        # Title
        if hasattr(self, u'title') and self.title:
            self.title.set_position(self._get_position_list(ax_pos, self.title_position + [0, 0])[:2])
        
        # Colorbar
        if hasattr(self, u'cbar_ax') and self.cbar_ax:
            self.cbar_ax.set_position(self._get_position_list(ax_pos, self.cbar_position))
        
        # Legend
        if hasattr(self, u'legend') and self.legend:
            self.legend.set_bbox_to_anchor(self._get_position_list(ax_pos, self.legend_position + [0, 0])[:2])


    
    #==========================================================================    
    def _get_position_list(self, ax_pos, item_pos):
        
        mx, my, mw, mh = ax_pos.x0, ax_pos.y0, ax_pos.width, ax_pos.height
        x, y, w, h = item_pos
        
        new_x = mx + mw * x
        new_y = my + mh * y
        new_w = mw * w
        new_h = mh * h
        
        return [new_x, new_y, new_w, new_h]
            
        
    #========================================================================== 
    def _on_resize(self, event):
        self._reposition_items()


        
    #========================================================================== 
    def enable_movable_text(self):
        if not hasattr(self, 'movable_text'):
            self.movable_text = MovableText(figure=self.fig)
            print('Movable text enabled')
        
    #========================================================================== 
    def disable_movable_text(self):
        try:
            self.movable_text.disconnect()
            del(self.movable_text)
            print('Movable text disabled')
        except:
            pass
         
    #========================================================================== 
    def set_title(self, title=u'', position=[0.5, 1.0], fontsize=10):
        
        if hasattr(self, 'title'):
            self.title.set_text(title)
            
        else:
            self.title_position = position
            self.title = self.fig.suptitle(title, fontsize=fontsize, x=position[0], y=position[1])
            
        self.redraw()
 
    #==========================================================================
    def add_line(self, 
                 series_list=None, 
                 lat=None, 
                 lon=None,   
                 color='black', 
                 marker_id=u'', 
                 fill_color=None,  
                 **kwargs):
            
        marker_name = '%s_line_%s' % (color, marker_id)
        marker_name_fill = marker_name + u'_fill'
        if marker_name in self.marker_order:
            self.delete_marker(marker_name)
            self.delete_marker(marker_name_fill)
             
        if series_list:
            lat, lon, statn = self._get_latit_longit_from_series(series_list)
          
        x, y = self.m(lon, lat)
        
        # Fill ploygon
        if fill_color:
            self._fill_line(x, y, fill_color, marker_name_fill)
        
        # Line color
        handle = self.m.plot(x, y, color=color, zorder=50, **kwargs)
        

        self.redraw()
         
        self.marker_order.append(marker_name)
        self.markers[marker_name] = {}
        self.markers[marker_name][u'handle'] = handle
        self.markers[marker_name][u'lat'] = lat
        self.markers[marker_name][u'lon'] = lon
        self.markers[marker_name][u'color'] = color
        self.markers[marker_name][u'fill_color'] = fill_color
        self.markers[marker_name][u'kwargs'] = kwargs

        
    #==========================================================================
    def _fill_line(self, x, y, fill_color, marker_name):
        
        handle = self.ax.add_patch(Polygon(map(list, zip(x,y)), closed=True,
                          fill=True, color=fill_color))
        
        self.marker_order.append(marker_name)
        self.markers[marker_name] = {}
        self.markers[marker_name][u'handle'] = handle
        self.markers[marker_name][u'fill_color'] = fill_color
        
    
    #==========================================================================
    def add_markers(self, 
                    series_list=None, 
                    lat=None, 
                    lon=None, 
                    marker_id=u'', 
                    marker=u'*',
                    **kwargs):
 
        if series_list != None:
            lat, lon, statn = self._get_latit_longit_from_series(series_list)
        
        marker_name = 'marker_%s' % marker_id
        
        if marker_name in self.marker_order:
            self.delete_marker(marker_name)
        
        if type(lat) != list:
            lat = [lat]
            lon = [lon]

        if not lat:
            return
        x, y = self.m(lon, lat)
        handle = self.m.plot(x, y, marker=marker, **kwargs)
        self.redraw()
        
        self.marker_order.append(marker_name)
        self.markers[marker_name] = {}
        self.markers[marker_name]['handle'] = handle
        self.markers[marker_name]['lat'] = lat
        self.markers[marker_name]['lon'] = lon
        self.markers[marker_name]['kwargs'] = kwargs
        if series_list:
            self.markers[marker_name]['series_list'] = series_list
        else:
            self.markers[marker_name]['series_list'] = [None]*len(lat)
       
    
    #==========================================================================
    def add_scatter(self, lat=[], lon=[], values=[], 
                    divide=[], index=[], marker_size=100, color_map=u'jet', marker_type=[u'*'], 
                    labels=None, edge_color=u'black', line_width=1, 
                    marker_id=u'', legend_nr=1, **kwargs):
        """
        Method to add scatter plot. 
        Possible inputs are: 
        divide: is evalueated with eval() (e.i. "<=10" can be given)
        """
        if type(marker_type) != list:
            marker_type = [marker_type]
        # Make some checks
        if divide:
            if len(divide) != len(marker_type):
                print('Map().add_scatter: number of logical expressions and number of markers does not match. No plots made.')
                return
        if index:
            if len(index) != len(marker_type):
                print('Map().add_scatter: number of index lists and number of markers does not match. No plots made.')
                return
        
        if type(marker_size)==int:
            marker_size = [marker_size]

        if len(marker_size) == 1:
            if len(divide) > 1: 
                marker_size = marker_size*len(divide)
            elif len(index) > 1: 
                marker_size = marker_size*len(index)
                
        if len(divide) > 1:
            if len(marker_size) == 1:
                marker_size = marker_size*len(divide)
                
        if isinstance(color_map, matplotlib.colors.LinearSegmentedColormap):
            pass
        elif hasattr(plt.cm, color_map):
            color_map = eval(u'plt.cm.%s' % color_map)
        else:
            color_map = plt.cm.jet
        
        color_string = u'%s' % color_map.name
           
        if not edge_color:
            edge_color = u'none'
        
#        print('lat', lat
#        print('lon', lon
        x, y = self.m(lon, lat)
        x = np.array(x)
        y = np.array(y)

        # Divide lists to plot several parts
        if index:
            x_list = []
            y_list = []
            value_list = []
            for i in index:
                x_list.append(np.array(x)[i])
                y_list.append(np.array(y)[i])
                value_list.append(np.array(values)[i])
            
            
            
        elif divide:
            x_list = [[] for i in range(len(divide))]
            y_list = [[] for i in range(len(divide))]
            value_list = [[] for i in range(len(divide))]
            
            if u'rest' in divide:
                rest_column = divide.index(u'rest')
            else:
                rest_column = None
            counter = dict((d, 0) for d in divide)
            for f, [x_val, y_val, value_val] in enumerate(zip(x, y, values)):

                if not np.isnan(value_val):
                    found_logical = False
                    for d, logical in enumerate(divide):
                        if not found_logical:
                            if d != rest_column:
                                if type(logical) == tuple:
                                    if eval(str(value_val)+logical[0]) and eval(str(value_val)+logical[1]):
                                        found_logical = True
                                    else:
                                        continue
                                else:
                                    if eval(str(value_val)+logical):
                                        counter[logical]+=1
                                        found_logical = True
                                    else:
                                        continue
                                
                                x_list[d].append(x_val)
                                y_list[d].append(y_val)
                                value_list[d].append(value_val)
                        
                    if type(rest_column)==int and not found_logical:
                        x_list[rest_column].append(x_val)
                        y_list[rest_column].append(y_val)
                        value_list[rest_column].append(value_val)

        else:
            x_list = [x]
            y_list = [y]
            value_list = [values]
        return_marker = None  
        for i in range(len(x_list)):
            marker_name = u'%s_scatter_%s_%s' % (color_string, marker_type[i], marker_id)
            if marker_name in self.marker_order:
                print('Remove marker', marker_name)
                self.delete_marker(marker_name)
            # print(x_list[0])
            # print(y_list[0])
            # print(value_list[0])
            handle = self.m.scatter(x_list[i], y_list[i], c=value_list[i], 
                                    s=marker_size[i], cmap=color_map, marker=marker_type[i], 
#                                     vmin=np.nanmin(values), vmax=np.nanmax(values),  
                                    picker=True, edgecolors=edge_color, **kwargs)


            self.marker_order.append(marker_name)
            self.markers[marker_name] = {}
            self.markers[marker_name][u'handle'] = handle
            self.markers[marker_name][u'lat'] = lat
            self.markers[marker_name][u'lon'] = lon
            self.markers[marker_name][u'values'] = values
            self.markers[marker_name][u'divide'] = divide
            self.markers[marker_name][u'index'] = index
            self.markers[marker_name][u'marker_size'] = marker_size
            self.markers[marker_name][u'marker_type'] = marker_type
            self.markers[marker_name][u'color_map'] = color_map
            self.markers[marker_name][u'edge_color'] = edge_color
            self.markers[marker_name][u'colorbar'] = None
            self.markers[marker_name][u'line_width'] = line_width
            self.markers[marker_name][u'kwargs'] = kwargs
            
            # Return a marker name that has data.
            if not return_marker and any(value_list[i]):
                return_marker = marker_name
            
            # Add to legend
            if labels:
                self._add_to_legend(legend_nr, marker_name, labels[i])
            
            
        self.redraw()
            
        return return_marker # maker name to link colorbar
        
    #==========================================================================
#     @error_handler(raise_error)
    def add_text(self, series_list=None, 
                         lat=None, lon=None, 
                         x=None, y=None, 
                         x_fraction=None, y_fraction=None, 
                         text=None, 
                         statn=None,
                         font=None,
                         fontsize=6, 
                         font_family=u'sans-serif', 
                         font_style=u'normal', 
                         font_weight=u'normal', 
                         lat_offset=0, lon_offset=0, 
                         lat_offset_percent=None, 
                         lon_offset_percent=None, 
                         color=u'black', 
                         marker_id=u'', 
                         picker=True, 
                         **kwargs):
        
        # Set font
        if not font:
            font = FontProperties()
            font.set_family(font_family)
            font.set_size(fontsize)
            font.set_style(font_style)
            font.set_weight(font_weight)
        
        marker_name = u'%s_text_%s' % (color, marker_id)
            
        if marker_name in self.marker_order:
            self.delete_marker(marker_name)
            
        if statn and not text:
            text = statn
            
        if x and y:
            if type(x) != list: x=[x]
            if type(y) != list: y=[y]
            if type(text) != list: text = [text]
                
        elif series_list:
            lat, lon, statn = self._get_latit_longit_from_series(series_list)
            if not text:
                text = statn
        
        if lat and type(lat_offset) in [float, int]:
            lat_offset = [lat_offset]*len(lat)
            
        if lon and type(lon_offset) in [float, int]:
            lon_offset = [lon_offset]*len(lon)
        
        self.markers[marker_name] = {}
        self.markers[marker_name][u'handle'] = []
        
        # It x- and y_fraction is given
        if x_fraction and y_fraction:
            handle = self.ax.text(x_fraction, y_fraction, text, fontproperties=font, color=color, 
                                      picker=picker, 
                                      transform=self.ax.transAxes, **kwargs)
            self.markers[marker_name][u'handle'].append(handle)               
        
        # If single text
        elif x != None and y != None:
            for xx, yy, texttext in zip(x,y,text):
                handle = self.ax.text(xx, yy, texttext, fontproperties=font, color=color, 
                                      picker=picker, 
                                      **kwargs)
                self.markers[marker_name][u'handle'].append(handle)
                
        if lat_offset_percent:
            lat_offset = [self.get_offset(lat_offset_percent, 0)[0]]*len(lat)
        if lon_offset_percent:
            lon_offset = [self.get_offset(0, lon_offset_percent)[1]]*len(lon)
            
        if type(text) != list:
            text = [text]
        for la, lo, la_off, lo_off, t in zip(lat, lon, lat_offset, lon_offset, text):
            # Only plot if offset is present. This is to controll offset from StationList()
#                 if la_off:
            la = la+la_off
            lo = lo+lo_off
            if self._within_boundry(la, lo):
                x, y = self.m(lo, la)
                handle = self.ax.text(x, y, t, fontproperties=font, color=color, 
                                      picker=picker, **kwargs)
                self.markers[marker_name][u'handle'].append(handle)
        self.redraw()
        
        self.marker_order.append(marker_name)
        self.markers[marker_name][u'lat'] = lat
        self.markers[marker_name][u'lon'] = lon
        self.markers[marker_name][u'text'] = text
        self.markers[marker_name][u'lat_offset'] = lat_offset
        self.markers[marker_name][u'lon_offset'] = lon_offset
        self.markers[marker_name][u'lat_offset_percent'] = lat_offset_percent
        self.markers[marker_name][u'lon_offset_percent'] = lon_offset_percent
        self.markers[marker_name][u'color'] = color
        self.markers[marker_name][u'marker_id'] = marker_id
        self.markers[marker_name][u'font'] = font
        self.markers[marker_name][u'kwargs'] = kwargs
    
    #==========================================================================
    def add_working_indicator(self):
        
        xmid = np.mean(self.ax.get_xlim())
        ymid = np.mean(self.ax.get_ylim())
        
        self.add_text(x=xmid, 
                      y=ymid, 
                      text=u'Work in progress\nplease wait...', 
                      fontsize=14, 
                      color=u'red', 
                      marker_id=u'working_indicator', 
                      ha=u'center', 
                      va=u'center')
        
        
    #==========================================================================
    def add_binding_key(self, binding_string, callback_function):
        self.bindings[binding_string] = self.fig.canvas.mpl_connect(binding_string, callback_function)
        
    #==========================================================================
    def delete_working_indicator(self):
        self.delete_marker(marker_id=u'working_indicator')
        
       
    #==========================================================================
    def get_offset(self, lat_offset_percent, lon_offset_percent):
           
        lon_min, lat_min = self.m(self.m.xmin, self.m.ymin, inverse=True)
        lon_max, lat_max = self.m(self.m.xmax, self.m.ymax, inverse=True)
        
        lon_offset = (lon_max-lon_min)*lon_offset_percent/100.
        lat_offset = (lat_max-lat_min)*lat_offset_percent/100.
        
        return lat_offset, lon_offset

    #==========================================================================
    def get_lat_lon(self, x, y):
        lon, lat = self.m(x, y, inverse=True)
        return lat, lon
    
    #==========================================================================
    def get_random_color(self):
        r = lambda: random.randint(0,255)
        return '#%02X%02X%02X' % (r(),r(),r())
    
#    #==========================================================================
#    def mark_closest_series(self, px, py, match_marker_type=u'', **kwargs):  
#        
#        # First find nearest point
#        min_dist = 100000
#        plon, plat = self.m(px, py, inverse=True)
#        if self.marker_order:
#            for marker_name in self.marker_order:
#                if 'marker' in marker_name and match_marker_type in marker_name:
#                    for lat, lon, key in zip(self.markers[marker_name][u'lat'], self.markers[marker_name][u'lon'], 
#                                        self.markers[marker_name][u'series_list']):
#                        series = Kistan().series[key]
#                        dist = stl.latlon_distance((plat, plon), (lat, lon))
#                        if dist < min_dist:
#                            min_dist = dist
#                            min_lat = lat
#                            min_lon = lon
#                            min_series_keys = [series.series_id]
#                        elif dist == min_dist:
#                            if series.series_id not in min_series_keys:
#                                min_series_keys.append(series.series_id)
#        
#            self.add_markers(lat=[min_lat], lon=[min_lon], markersize=10, color=u'blue', marker=u'*', **kwargs)
#            
#            return min_series_keys

    
    #==========================================================================
    def add_colorbar(self, 
                     marker_name, 
                     title=None, 
                     orientation=u'vertical', 
                     position=[0.85, 0.1, 0.05, 0.3], 
                     tick_side=u'right', 
                     tick_size=6, 
                     title_size=6, 
                     nr_ticks=False,
                     display_every=False, 
                     time_format=False, 
                     **kwargs):
        
        self.cbar_position = position
        self.cbar_ax = self.fig.add_axes(position)
        self._reposition_items()
        if time_format:
            if nr_ticks: 
                nt = nr_ticks
            else:
                nt = 5
            dif = np.nanmax(self.markers[marker_name][u'values']) - np.nanmin(self.markers[marker_name][u'values'])
            interval = int(np.ceil(dif/nt))
            if interval < 1:
                interval = 1
            self.cbar = self.fig.colorbar(self.markers[marker_name][u'handle'], cax=self.cbar_ax, 
                                          orientation=orientation, 
                                          ticks=DayLocator(interval=interval), 
                                          format=DateFormatter('%b %d'), 
                                          **kwargs)
        else:
            self.cbar = self.fig.colorbar(self.markers[marker_name][u'handle'], cax=self.cbar_ax, 
                                          orientation=orientation, 
                                          **kwargs)
            
            if nr_ticks:
                tick_locator = matplotlib.ticker.LinearLocator(nr_ticks)
                self.cbar.locator = tick_locator
                self.cbar.update_ticks()  
                 
            # Option to not display all ticks
            elif display_every:
                if orientation == u'vertical': 
                    for k, label in enumerate(self.cbar.ax.yaxis.get_ticklabels()):
                        if k%display_every:
                            label.set_visible(False)
                else: 
                    for k, label in enumerate(self.cbar.ax.xaxis.get_ticklabels()):
                        if k%display_every:
                            label.set_visible(False)
                        
        self.cbar.ax.yaxis.set_ticks_position(tick_side)
        self.cbar.ax.tick_params(labelsize=tick_size)

        if title:
            self.cbar.ax.set_title(title, fontsize=title_size)
        
        self.markers[marker_name][u'colorbar'] = True
        self.redraw()
        
        
    #==========================================================================
    def add_parallels(self, 
                      step=1., 
                      left_labels=False,
                      right_labels=False, 
                      fontsize=6, 
                      line_width=0.2, 
                      **kwargs):
        if 'parallels' in self.map_items:
            return
         
        # Fix labels
        labels=[False,False,False,False]
        if left_labels:
            labels[0] = True
        if right_labels:
            labels[1] = True
         
        # Check label format
        if not step%1.:
            fmt_string = u'%.0f'
        elif not step%.5 or not step%.2:
            fmt_string = u'%.1f'
        else:
            fmt_string = u'%g'
             
        # Create item
        parallels = self.m.drawparallels(np.arange(np.floor(self.min_lat), 
                                                   np.ceil(self.max_lat), 
                                                   step), 
                                              labels=labels, 
                                              linewidth=line_width, 
                                              fontsize=fontsize, 
                                              fmt=fmt_string, 
                                              **kwargs)
        self.canvas.draw()
        self.map_items[u'parallels'] = parallels            
 
    
    #==========================================================================
    def delete_parallels(self):
        self.delete_map_item('parallels')
        
        
    #==========================================================================
    def add_meridians(self, 
                      step=1., 
                      top_labels=False,
                      bottom_labels=False, 
                      fontsize=6, 
                      line_width=0.2, 
                      **kwargs):
        if 'meridians' in self.map_items:
            return
         
        # Fix labels
        labels=[False,False,False,False]
        if top_labels:
            labels[2] = True
        if bottom_labels:
            labels[3] = True
         
        # Check label format
        if not step%1.:
            fmt_string = u'%.0f'
        elif not step%.5 or not step%.2:
            fmt_string = u'%.1f'
        else:
            fmt_string = u'%g'
             
        # Create item
        meridians = self.m.drawmeridians(np.arange(np.floor(self.min_lon), 
                                                   np.ceil(self.max_lon), 
                                                   step), 
                                              labels=labels, 
                                              linewidth=line_width, 
                                              fontsize=fontsize, 
                                              fmt=fmt_string, 
                                              **kwargs)
        self.canvas.draw()
        self.map_items[u'meridians'] = meridians            
        
        
    #==========================================================================
    def delete_meridians(self):
        self.delete_map_item('meridians')
         
    #==========================================================================
    def delete_all_map_items(self):
        for item in self.map_items.keys():
            self.delete_map_item(item, update_canvas=False)
        self.canvas.draw()
        
    #==========================================================================
    def delete_map_item(self, map_item, update_canvas=True):
        if map_item in self.map_items:
            if 'dict' in str(type(self.map_items[map_item])):
                for item in self.map_items[map_item].itervalues():
                    for val in item:
                        try:
                            val.pop(0).remove()
                        except:
                            pass
            self.map_items.pop(map_item)
            if update_canvas:
                self.canvas.draw()
  
            
    #==========================================================================
    def add_event(self, event_type, event_function): 
        if self.parent:
            self.event_dict[event_type] = {}
            self.event_dict[event_type][u'event_type'] = event_type
            self.event_dict[event_type][u'event_function'] = event_function
            self.event_dict[event_type][u'object'] = self.fig.canvas.mpl_connect(event_type, 
                                                       event_function)
        else:
            print('Could not add event to Map(). No parent given.')
        

    #==========================================================================
    def delete_marker(self, marker_name=None, marker_id=None):
        """ 
        if marker_name: marker with the exakt name is removed 
        if marker_id: All markers containing the given marker_id are removed
        """
        matching_markers = []
        if marker_id:
            for mid in self.marker_order:
                if marker_id in mid:
                    matching_markers.append(mid)
        else:
            matching_markers = [marker_name]
#                     marker_name = mid

#         if marker_name in self.marker_order:   
        for marker_name in matching_markers:  
            if u'text' in marker_name:
                for handle in self.markers[marker_name][u'handle']:
                    try:
                        handle.remove()
                    except:
                        pass
            elif u'scatter' in marker_name:
                self.markers[marker_name][u'handle'].remove()

            else:
                try:
                    self.markers[marker_name][u'handle'].pop(0).remove()
                except:
                    try:
                        self.markers[marker_name][u'handle'].remove()
                    except:
                        pass
                
            self.marker_order.pop(self.marker_order.index(marker_name))
            self.markers.pop(marker_name)
            self.canvas.draw()
            
    
    #==========================================================================
    def delete_colorbar(self):
        if hasattr(self, u'cbar') and self.cbar:
            self.fig.delaxes(self.fig.axes[1])
            self.cbar = None
            self.canvas.draw()

    #==========================================================================
    def delete_legend(self):
        if hasattr(self, u'legend') and self.legend:
            self.legend.set_visible(False)
#             self.ax.legend_.remove()  
            self.legend = None
            self.legend_items = {1: {u'handle':[], u'label':[]}, 
                                 2: {u'handle':[], u'label':[]}, 
                                 3: {u'handle':[], u'label':[]}}   
            
            self.canvas.draw()
            
    #==========================================================================
    def delete_all_markers(self):
        
        if self.marker_order:
            for marker in self.marker_order[:]:
                self.delete_marker(marker)
                
        self.delete_colorbar()
        self.delete_legend()

        self.canvas.draw()
        
    #==========================================================================
    def reset_map(self):
        self.delete_all_markers()
    
    #==========================================================================
    def save_map(self, file_path, resolution=600, orientation=u'portrait', close_figure=True):
        if file_path.endswith(u'.pdf'):
            pdf_pages = PdfPages(file_path)
            pdf_pages.savefig(self.fig)
            pdf_pages.close()
        else:
            self.fig.savefig(file_path, dpi=resolution, orientation=orientation)
            if close_figure:
                plt.close()
#                 self.fig.close()
        

    #==========================================================================
    class MapSize():
        def __init__(self, ax):
            bbox = ax.get_window_extent()
            
            self.width = bbox.width
            
            


"""
================================================================================
================================================================================
================================================================================
"""
class MovableText(object):
    """ A simple class to handle Drag n Drop.

    This is a simple example, which works for Text objects only
    """
    def __init__(self, figure=None) :
        """ Create a new drag handler and connect it to the figure's event system.
        If the figure handler is not given, the current figure is used instead
        """
        self.fig = figure
#         if figure is None : figure = p.gcf()
        # simple attibute to store the dragged text object
        self.dragged = None
        self.events = {}

        # Connect events and callbacks
#         figure.canvas.mpl_connect("pick_event", self.on_pick_event)
        self.events[u'pick_event'] = self.fig.canvas.mpl_connect('pick_event', lambda event: self.on_pick_event(event))
#         self.events[u'button_press_event'] = self.fig.canvas.mpl_connect('button_pres_event', lambda event: self.on_press_event(event)) # Have to remove saved entris too.
        self.events[u'button_release_event'] = self.fig.canvas.mpl_connect('button_release_event', lambda event: self.on_release_event(event))
#         self.events[u'motion_notify_event'] = self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.on_motion_notify_event(event))
#         figure.canvas.mpl_connect("button_release_event", self.on_release_event)
        
    def on_pick_event(self, event):
        " Store which text object was picked and were the pick event occurs."
        
#         print('on_pick_event', event.mouseevent.key 
        if isinstance(event.artist, Text):
            if event.mouseevent.button == 3:
                event.artist.remove()
                self.fig.canvas.draw()
                return
            self.dragged = event.artist
            self.pick_pos = (event.mouseevent.xdata, event.mouseevent.ydata)
        return True
    
    #==========================================================================
    def on_press_event(self, event):
#         print(event.button
        if event.button == 3 and self.dragged:
            self.dragged.remove()
            self.dragged = None
            self.fig.canvas.draw()
            
    #==========================================================================
    def on_release_event(self, event):
        " Update text position and redraw"
        
#         print('on_release_event'
        if self.dragged is not None :
            old_pos = self.dragged.get_position()
            new_pos = (old_pos[0] + event.xdata - self.pick_pos[0],
                       old_pos[1] + event.ydata - self.pick_pos[1])
            self.dragged.set_position(new_pos)
            self.dragged = None
            self.fig.canvas.draw()
        return True
    
    #==========================================================================
    def on_motion_notify_event(self, event):
        " Update text position and redraw"
        
        if self.dragged is not None :
            print('on_motion_notify_event')
            old_pos = self.dragged.get_position()
            new_pos = (old_pos[0] + event.xdata - self.pick_pos[0],
                       old_pos[1] + event.ydata - self.pick_pos[1])
            self.dragged.set_position(new_pos)
            self.fig.canvas.draw()
        return True
    
    #==========================================================================
    def disconnect(self):
        for event in self.events:
            self.fig.canvas.mpl_disconnect(event)
        self.events = {}