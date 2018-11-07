#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2016-2017 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

#----------------------------------------------------------
from .gui_helpers import grid_configure


#----------------------------------------------------------
from .communicate import add_sample_data_to_boxen
from .communicate import add_sample_data_to_plot

from .communicate import flag_data_profile
from .communicate import flag_data_time_series

from .communicate import get_flag_widget

from .communicate import update_compare_widget
from .communicate import update_highlighted_profile_in_plot
from .communicate import update_limits_in_axis_float_widget
from .communicate import update_limits_in_axis_time_widget
from .communicate import update_plot_limits_from_settings
from .communicate import update_profile_plot
from .communicate import update_range_selection_widget
from .communicate import update_scatter_route_map
from .communicate import update_time_series_plot

from .communicate import save_limits_from_axis_float_widget
from .communicate import save_limits_from_axis_time_widget 
from .communicate import save_limits_from_plot_object
from .communicate import set_valid_time_in_time_axis


#----------------------------------------------------------
from .widgets import AxisSettingsBaseWidget
from .widgets import AxisSettingsFloatWidget
from .widgets import AxisSettingsTimeWidget
from .widgets import CompareWidget
from .widgets import MovableText 
from .widgets import RangeSelectorFloatWidget
from .widgets import RangeSelectorTimeWidget
from .widgets import SaveWidget


#----------------------------------------------------------
try:
    from .page_ctd import PageCTD
except:
    pass

try:
    from .page_timeseries import PageTimeSeries
except:
    pass

try:
    from .page_ferrybox_route import PageFerryboxRoute
except:
    pass

from .page_start import PageStart
    
    
    
    
