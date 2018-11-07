#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2016-2017 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

"""
================================================================================
================================================================================
================================================================================
""" 
def grid_configure(frame, rows={}, columns={}):
    """
    Put weighting on the given frame. Rows and collumns that ar not in rows and columns will get weight 1.
    """
    for r in range(30):
        if r in rows:
            frame.grid_rowconfigure(r, weight=rows[r])
        else:
            frame.grid_rowconfigure(r, weight=1)
    
    for c in range(30):
        if c in columns:
            frame.grid_columnconfigure(c, weight=columns[c])
        else:
            frame.grid_columnconfigure(c, weight=1)