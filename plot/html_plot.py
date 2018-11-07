# -*- coding: utf-8 -*-
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on Wed Aug  8 12:05:15 2018

@author:
""" 
import plotly.graph_objs as go 
import plotly.offline as ply 
#import plotly.plotly as ply

class PlotlyPlot():
    """
    Class uses plotly to plot data. 
    """
    def __init__(self, 
                 **kwargs): 
        
        self.data = []
        self.set_layout(**kwargs) 
    
    
    #==========================================================================
    def _get_plot_name(self, plot_type='', **kwargs):
        default_plot_name = '{}_{}_plot'.format(len(self.data)+1, plot_type)
        return kwargs.get('name', default_plot_name)
        
    
    #==========================================================================
    def get_figure(self): 
        return dict(data=self.data, 
                   layout=self.layout)
        
        
    #==========================================================================
    def set_layout(self, **kwargs): 
        self.layout = dict(title = kwargs.get('title', 'title'), 
                           xaxis = dict(title = kwargs.get('xaxis_title', 'xaxis')), 
                           yaxis = dict(title = kwargs.get('yaxis_title', 'yaxis'))) 
        
        
    #==========================================================================
    def add_bar_data(self, x, y, **kwargs): 
        
        trace = go.Bar(x=x, 
                       y=y, 
                       name = self._get_plot_name('bar', **kwargs),
        )

        
        self.data.append(trace) 
        self.layout['barmode'] = kwargs.get('barmode', 'group') # stack
        
        
    #==========================================================================
    def add_box_data(self, x=None, y=None, **kwargs): 
        
        trace = go.Box(
                    x=x, 
                    y=y,
                    name=self._get_plot_name('bar', **kwargs),
                    marker=dict(
                        color=kwargs.get('marker_color', None)
                    ), 
                    boxpoints=kwargs.get('boxpoints', None),

                )
        self.data.append(trace) 
        

        
    #==========================================================================
    def get_position(self, pos, space_percent=5): 
        """
        pos is a four digit number or str that shows where to place the chart. 
        First two are the grid and the last to are the desired position. 
        """ 
        padding = space_percent/100. 
        
        pos = list(str(pos)) 
        nr_x = int(pos[0])
        nr_y = int(pos[1])
        pos_x = int(pos[2])
        pos_y = int(pos[3])
        
        dx = 1./nr_x
        dy = 1./nr_y
        
        x_list = []
        for x in range(nr_x): 
            x_list.append([dx*x+padding, dx*(x+1)-padding])
            
        y_list = []
        for y in range(nr_y): 
            y_list.append([dy*y+padding, dy*(y+1)-padding])
            
#        print('-'*30)
#        print(x_list)
#        print(y_list)
#        print(x_list[pos_x-1], y_list[pos_y-1]) 
        return [x_list[pos_x-1], y_list[pos_y-1]]
        
        
    
    #==========================================================================
    def add_pie_data(self, x, y, pos=1111, **kwargs): 
        
        x_pos, y_pos = self.get_position(pos)
        trace = go.Pie(labels=x, 
                       values=y, 
                       name = self._get_plot_name('pie', **kwargs), 
                       domain = {'x': x_pos, 
                                 'y': y_pos}
        )

        
        self.data.append(trace) 
        
        
    #==========================================================================
    def add_scatter_data(self, x, y, **kwargs): 
    
        trace = go.Scatter(x = x, 
                           y = y, 
                           name = self._get_plot_name('scatter', **kwargs),
                           mode = kwargs.get('mode', 'lines'), 
                           line = dict(color = kwargs.get('line_color', None), 
                                       width = kwargs.get('line_width', 2), 
                                       dash = kwargs.get('dash', 'solid'))
                           ) 
        
        self.data.append(trace) 
        
        
    
        
    
    #==========================================================================
    def add_profile_dataframe(self, df, depth_par='DEPH', **kwargs): 
        """
        All parameters in df are plotted with depth_par as y-axis. 
        "label_mapping" and "unit_mapping" can be given as kwargs. 
        """
        kw = dict(mode='lines+markers')
        kw.update(kwargs)
        for col in df.columns: 
            if col == depth_par:
                continue 
            if df[col].dtype != float:
                continue 
            
            # Set label
            if kwargs.get('label_mapping'):
                name = kwargs['label_mapping'](col)
            else:
                name = col 
            
            # Add unit 
            if kwargs.get('unit_mapping'):
                name = name + ' ({})'.format(kwargs['unit_mapping'](col)) 
            
            # Add plot 
            self.add_scatter_data(df[col], df[depth_par], name=name, **kw)
        
        
    #==========================================================================
    def plot_to_file(self, file_path): 
        fig =  self.get_figure()
        # Plot to file 
        ply.plot(fig, filename=file_path) 
        
        
    #==========================================================================
    def plot_in_notebook(self): 
#        print(ply)
        ply.init_notebook_mode(connected=True)
        fig = self.get_figure()
        ply.iplot(fig)
        