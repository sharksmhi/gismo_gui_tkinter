#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

#----------------------------------------------------------
import sys

# from .gui_helpers import grid_configure


#----------------------------------------------------------
from .communicate import add_compare_to_timeseries_plot

from .communicate import flag_data_profile
from .communicate import flag_data_time_series

from .communicate import get_flag_widget

# from .communicate import update_compare_widget
from .communicate import update_highlighted_profile_in_plot
from .communicate import update_limits_in_axis_float_widget
from .communicate import update_limits_in_axis_time_widget
from .communicate import update_profile_plot
from .communicate import update_range_selection_widget
from .communicate import update_scatter_route_map
from .communicate import update_time_series_plot

from .communicate import save_limits_from_axis_float_widget
from .communicate import save_limits_from_axis_time_widget
from .communicate import save_user_info_from_flag_widget
from .communicate import set_valid_time_in_time_axis

from .communicate import plot_map_background_data

from .communicate import get_file_id

#----------------------------------------------------------
from .widgets import AxisSettingsBaseWidget
from .widgets import AxisSettingsFloatWidget
from .widgets import AxisSettingsTimeWidget
from .widgets import CompareWidget
from .widgets import MovableText
from .widgets import RangeSelectorFloatWidget
from .widgets import RangeSelectorTimeWidget
from .widgets import SaveWidget
from .widgets import SaveWidgetHTML
from .widgets import show_information
from .widgets import show_warning
from .widgets import show_error
from .widgets import InformationPopup
from .widgets import EntryPopup


#----------------------------------------------------------

from .page_start import PageStart
# from .page_ferrybox import PageFerrybox
# from .page_fixed_platforms import PageFixedPlatforms
from .page_user import PageUser
from .page_about import PageAbout
from .page_time_series import PageTimeSeries
from .page_metadata import PageMetadata
from .page_profile import PageProfile

# print('GUI IMPORT')
# for key in sorted(sys.modules.keys()):
#     print(key, sys.modules[key])

