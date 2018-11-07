# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
'''
Created on 4 jun 2016

@author:
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

"""
===============================================================================
===============================================================================
"""
class Plot3YAxis():
     
    #==========================================================================
    def __init__(self, ax3pos=1.05, adjus_left=0.05, adjust_right=0.9, **kwargs):

        def make_patch_spines_invisible(ax):
            ax.set_frame_on(True)
            ax.patch.set_visible(False)
            for sp in ax.spines.values():
                sp.set_visible(False)
        
        self.ax = {}    # To save axis
        self.fig = plt.figure(**kwargs)
        self.ax[1] = self.fig.add_subplot(111)
#         self.fig, self.ax[1] = plt.subplots()
        self.fig.subplots_adjust(right=adjust_right, left=adjus_left)
        
        self.ax[2] = self.ax[1].twinx()
        self.ax[3] = self.ax[1].twinx()
        
        # Offset the right spine of par2.  The ticks and label have already been
        # placed on the right by twinx above.
        self.ax[3].spines["right"].set_position(("axes", ax3pos))
        # Having been created by twinx, par2 has its frame off, so the line of its
        # detached spine is invisible.  First, activate the frame but make the patch
        # and spines invisible.
        make_patch_spines_invisible(self.ax[3])
        # Second, show the right spine.
        self.ax[3].spines["right"].set_visible(True)
        
        self.p = dict((k, []) for k in [1,2,3])     # To save plots
        
        plt.show()
        
     
    #==========================================================================
    def add_plot(self, ax_nr, x, y, month_format=None, year_format=None, **kwargs):

        p, = self.ax[ax_nr].plot(x, y, **kwargs)
        self.p[ax_nr].append(p)
        
        if any([month_format, year_format]):
            try:
                # Time
                if month_format:
                    months = mdates.MonthLocator()  # every month
                    month_format = mdates.DateFormatter(month_format)
                    self.ax[ax_nr].xaxis.set_major_formatter(month_format)
                    self.ax[ax_nr].xaxis.set_major_locator(months)
                elif year_format:
                    years = mdates.YearLocator()   # every year
                    year_format = mdates.DateFormatter(year_format)
                    self.ax[ax_nr].xaxis.set_major_formatter(year_format)
                    self.ax[ax_nr].xaxis.set_major_locator(years)
 
#                 days = mdates.DayLocator()  # every day
#                 ax.xaxis.set_minor_locator(days)
       
            except:
                print('Could not change time format')
                
        plt.show() 
    
    #==========================================================================
    def set_xlim(self, ax_nr, xlim):
        self.ax[ax_nr].set_xlim(xlim)
        plt.show() 
        
    #==========================================================================
    def set_ylim(self, ax_nr, ylim):
        self.ax[ax_nr].set_ylim(ylim)
        plt.show() 
        
    #==========================================================================
    def set_xlabel(self, ax_nr, label, *args, **kwargs):
        self.ax[ax_nr].set_xlabel(label, *args, **kwargs)
        plt.show() 
        
    #==========================================================================
    def set_ylabel(self, ax_nr, label, *args, **kwargs):
        color = self.p[ax_nr][0].get_color()
        self.ax[ax_nr].set_ylabel(label)
        self.ax[ax_nr].yaxis.label.set_color(color)
        self.ax[ax_nr].yaxis.label.set_color(color)
        self.ax[ax_nr].tick_params(axis='y', colors=color)
        plt.show() 
        
    #==========================================================================
    def add_legend(self):
        self.ax[0].add_legend()
        
    #==========================================================================
    def save_pdf(self, file_path=u'plot.pdf', **kwargs):
        pdf_pages = PdfPages(file_path)
        pdf_pages.savefig(self.fig, **kwargs)
        pdf_pages.close()
     
     
"""
================================================================================
================================================================================
"""
if __name__ == '__main__':
    x = [1,2,3,4,5]
    y1 = [5,4,3,5,3]
    y2 = [9,7,8,6,7]
    y3 = [23,56,11,99,38]
    
    p = Plot3YAxis(figsize=(12,5))
    
    p.add_plot(1, x, y1, 'r-')
    p.add_plot(2, x, y2, 'b-')
    p.add_plot(3, x, y3, 'g-')
     
    p.set_ylabel(1, 'axis1')
    p.set_ylabel(2, 'axis2')
    p.set_ylabel(3, 'axis3')
     
    p.set_ylim(3, [0, 200])













            
            
            
            
            
            
            