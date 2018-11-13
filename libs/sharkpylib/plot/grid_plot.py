'''
Created on 4 jun 2016

@author:
'''

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import matplotlib.dates as mdates
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
 
 
"""
===============================================================================
===============================================================================
"""
class GridPlotMW():
     
    #==========================================================================
    def __init__(self, 
                 grid_layout=['3300c3', '3310c2'], 
                 plot_type='hh', **kwargs):
                      
        self.grid_layout = grid_layout
        self.plot_type = plot_type
        
        self.fig = plt.figure(**kwargs)
        self.ax = {}
        for k, sub in enumerate(grid_layout):
            if 'r' not in sub:
                sub = sub + 'r1'
            if 'c' not in sub:
                sub = sub + 'c1'
                 
            sub_list = list(sub)
            rl, cl, r, c = map(int, sub_list[:4])       
             
            rs = int(sub_list[sub_list.index('r')+1])
            cs = int(sub_list[sub_list.index('c')+1])
             
            sx = None
            sy = None
            if 'sx' in sub: 
                try:
                    sx = self.ax[int(sub_list[sub.index('sx') + 2])][1]
                except:
                    print('Not a valid sharex')
                 
            if 'sy' in sub: 
                try:
                    sy = self.ax[int(sub_list[sub.index('sy') + 2])][1]
                except:
                    print('Not a valid sharey')
             
            self.ax[k+1] = {}
            if self.plot_type[k] in ['p', 'b']:
                self.ax[k+1][1] = plt.subplot2grid((rl,cl), (r,c), rowspan=rs, colspan=cs, sharex=sx, sharey=sy, projection='polar')
            else:
                self.ax[k+1][1] = plt.subplot2grid((rl,cl), (r,c), rowspan=rs, colspan=cs, sharex=sx, sharey=sy)
             
#             if not self.fig:
#                 self.fig = plt.gcf()
                 
         
    #==========================================================================
    def subplot_adjust(self, *args, **kwargs): 
        self.fig.subplots_adjust(*args, **kwargs)
        plt.show()
     
    #==========================================================================
    def add_plot(self, ax_nr, side, x, y, month_format=None, year_format=None, **kwargs):
        if ax_nr not in self.ax:
            print('Not a valid axes number: %s' % ax_nr)
            return
        if side not in [1, 2]:
            return
        if side == 2 and side not in self.ax[ax_nr]:
            if self.plot_type[ax_nr-1] == u'h':
                self.ax[ax_nr][2] = self.ax[ax_nr][1].twinx()
            elif self.plot_type[ax_nr-1] == u'v':
                self.ax[ax_nr][2] = self.ax[ax_nr][1].twiny()
         
        ax = self.ax[ax_nr][side]
        
        ax.plot(x, y, **kwargs)         
        
        if any([month_format, year_format]):
            try:
                # Time
                if month_format:
                    months = mdates.MonthLocator()  # every month
                    month_format = mdates.DateFormatter(month_format)
                    ax.xaxis.set_major_formatter(month_format)
                    ax.xaxis.set_major_locator(months)
                elif year_format:
                    years = mdates.YearLocator()   # every year
                    year_format = mdates.DateFormatter(year_format)
                    ax.xaxis.set_major_formatter(year_format)
                    ax.xaxis.set_major_locator(years)
 
#                 days = mdates.DayLocator()  # every day
#                 ax.xaxis.set_minor_locator(days)
       
            except:
                print('Could not change time format')
                
        self.fig.show()
         
         
    #==========================================================================
    def add_bearing_plot(self, ax_nr, side, bearing, magnitude, *args, **kwargs):
        if self.plot_type[ax_nr-1] == 'b':
            angle = np.deg2rad(np.array(bearing))
            ax = self.ax[ax_nr][side]
            ax.set_theta_zero_location('N')
            ax.set_theta_direction(-1)
            ax.plot(angle, magnitude, *args, **kwargs)
            self.fig.show()
    
    #==========================================================================
    def set_title(self, ax_nr=1, string=u'', **kwargs):
        self.ax[ax_nr][1].set_title(string, **kwargs)
        plt.show()

    #==========================================================================
    def set_xlabel(self, ax_nr, side, x_label, *args, **kwargs):
        # Get first color plotted
        ax = self.ax[ax_nr][side]
        color = ax.lines[0].get_color()
        ax.set_xlabel(x_label, color=color, *args, **kwargs)
        for tl in ax.get_xticklabels():
            tl.set_color(color)
             
    #==========================================================================
    def set_ylabel(self, ax_nr, side, y_label, *args, **kwargs):
        # Get first color plotted
        ax = self.ax[ax_nr][side]
        color = ax.lines[0].get_color()
        ax.set_ylabel(y_label, color=color, *args, **kwargs)
        for tl in ax.get_yticklabels():
            tl.set_color(color)
            
    #==========================================================================
    def hide_xticks(self, ax_nr):
        ax = self.ax[ax_nr][1]
        ax.get_xaxis().set_visible(False)
#         ax.set_xticks([])
        plt.show()
        
    #==========================================================================
    def hide_yticks(self, ax_nr, side=1):
        ax = self.ax[ax_nr][side]
        ax.set_yticks([])
        plt.show()
    
    #==========================================================================
    def set_xticks(self, ax_nr=1, side=1, *args, **kwargs):
        ax = self.ax[ax_nr][side]
        ax.set_xticks(*args, **kwargs)
        plt.show()
        
    #==========================================================================
    def set_yticks(self, ax_nr=1, side=1, ticks=None, *args, **kwargs):
        if ticks:
            ax = self.ax[ax_nr][side]
            ax.set_yticks(ticks, **kwargs)
            plt.show()
            
    #==========================================================================
    def set_xlim(self, ax_nr=1, side=1, xlim=None):
        if xlim:
            ax = self.ax[ax_nr][side]
            ax.set_xlim(xlim)
            plt.show()
            
    #==========================================================================
    def set_ylim(self, ax_nr=1, side=1, ylim=None):
        if ylim:
            ax = self.ax[ax_nr][side]
            ax.set_ylim(ylim)
            plt.show()
    
    #==========================================================================
    def set_xticksize(self, ax_nr, fontsize=10):
        self.ax[ax_nr][1]
        # print(ax_nr, self.ax)
        for tick in self.ax[ax_nr][1].xaxis.get_major_ticks():
            tick.label.set_fontsize(fontsize) 
        plt.show()
        
    #==========================================================================
    def set_yticksize(self, ax_nr, fontsize=10):
        self.ax[ax_nr][1]
        for tick in self.ax[ax_nr][1].yaxis.get_major_ticks():
            tick.label.set_fontsize(fontsize) 
        if 2 in self.ax[ax_nr]:
            for tick in self.ax[ax_nr][2].yaxis.get_major_ticks():
                tick.label.set_fontsize(fontsize) 
        plt.draw()
        plt.show()
        
            
    #==========================================================================
    def add_multicursor(self, ax_nrs=[], horizontal=False, vertical=False, **kwargs):
        
        ax_list = []
        for ax_nr in ax_nrs:
            ax_list.append(self.ax[ax_nr][1])
        self.multi_cursors[str(ax_nrs)] = widgets.MultiCursor(self.fig.canvas,
                                                                  ax_list, 
                                                                  horizOn=horizontal, 
                                                                  vertOn=vertical, **kwargs)
        plt.show()
            
    #==========================================================================
    def add_zoomed_axes(self, from_ax_nr=1, to_ax_nr=2, rect_props=dict(alpha=0.5, facecolor='red')):
        
        self.ax[from_ax_nr]['span'] = widgets.SpanSelector(self.ax[from_ax_nr][1], 
                                    lambda xmin, xmax, from_ax=from_ax_nr, to_ax=to_ax_nr: self._on_span_select(xmin, xmax, from_ax, to_ax), 
                                    'horizontal', useblit=True,
                    rectprops=rect_props)
        
    #==========================================================================
    def save_pdf(self, file_path=u'plot.pdf', **kwargs):
        pdf_pages = PdfPages(file_path)
        pdf_pages.savefig(self.fig, **kwargs)
        pdf_pages.close()
    
    #==========================================================================
    def _on_span_select(self, xmin, xmax, from_ax_nr, to_ax_nr):
        
        target_ax = self.ax[to_ax_nr][1]
        target_line = self.ax[to_ax_nr][1].lines[0]
        
        try:
            line_1_xdata = self.ax[from_ax_nr][1].lines[0].get_xdata()
            line_1_ydata = self.ax[from_ax_nr][1].lines[0].get_ydata()
            # print(line_1_xdata)
            
            indmin, indmax = np.searchsorted(line_1_xdata, (xmin, xmax))
            indmax = min(len(line_1_xdata) - 1, indmax)
         
            thisx = line_1_xdata[indmin:indmax]
            thisy = line_1_ydata[indmin:indmax]
            target_line.set_data(thisx, thisy)
            target_ax.set_xlim(thisx[0], thisx[-1])
            target_ax.set_ylim(thisy.min(), thisy.max())
            self.fig.canvas.draw()
        except:
            print('The selected area is to narrow')
"""
================================================================================
================================================================================
"""
if __name__ == '__main__':
     
     
#     p = GridPlotMW(grid_layout=['3300c3', '3311c2r2'], plot_type='hb')
    p = GridPlotMW(grid_layout=['3300c3', '3311c2r2'], plot_type='hh')
 
    x = [1,2,3,4]
    y1 = [2,3,9,4]
    y2 = [5,3,2,5] 
    bearing = [80, 20, 190, 270]
    mag = [3,2,6,4]       
     
     
    p.add_plot(1, 1, x, y1, color='r')
    p.add_plot(1, 2, x, y2, color='green')
     
    p.add_plot(2, 1, bearing, mag, 'or', markersize=6)
    p.subplot_adjust(hspace=0.5, top=0.95)
     
     
    #p.plot(2, 1, x, y1, '--', color='darkgreen', linewidth=4)
    #p.plot(2, 2, x, y2)
     
    p.set_ylabel(1, 1, 'ylabel')
    p.set_ylabel(1, 2, 'ylabel2')
    p.set_title(1, u'hej')
    
    p.set_xticksize(1, fontsize=10)
    p.set_yticksize(1, fontsize=10)
         

            
            
            
            
            