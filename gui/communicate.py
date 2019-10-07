#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).


def sync_user_and_time_widgets(user_sub_object=None,
                               time_widget_start=None,
                               time_widget_end=None,
                               source=None,
                               **kwargs):
    """
    Sync user and time widgets.
    :param user_sub_object: object of class UserSettings
    :param time_widget_from:
    :param time_widget_to:
    :param source: Where to take information
    :param kwargs:
    :return:
    """
    min_range = time_widget_start.from_time
    max_range = time_widget_start.to_time

    if source in ['full range', 'full_range']:
        min_value = min_range
        max_value = max_range
    # Get limits from source
    elif source in ['user', 'user_object']:
        min_value = user_sub_object.get('time_start')
        max_value = user_sub_object.get('time_end')
    elif source in ['time_widget', 'widget', 'time_widgets', 'widgets']:
        min_value = time_widget_start.get_time_object()
        max_value = time_widget_end.get_time_object()

    if not min_value:
        min_value = min_range
    if not max_value:
        max_value = max_range

    if not all([min_value, max_value]):
        return

    min_value = max(min_value, min_range)
    max_value = min(max_value, max_range)

    # Set limits in user
    user_sub_object.set('time_start', min_value)
    user_sub_object.set('time_end', max_value)

    # Set limits in time widgets
    time_widget_start.set_time(datetime_object=min_value)
    time_widget_end.set_time(datetime_object=max_value)
