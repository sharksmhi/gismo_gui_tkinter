#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import folium


class FoliumMap(object):
    """  """
    def __init__(self, lat=58.8, lon=17.6, **kwargs):
        self.map = folium.Map(location=[lat, lon], zoom_start=kwargs.get('zoom_start', 5))

    def add_circle_marker(self, lat, lon, **kwargs):
        kw = dict(radius=3,
                  fill=True,
                  fill_color='#f95151',
                  color='#f95151',
                  popup=kwargs.get('popup', '{} : {}'.format(lat, lon)))
        kw.update(kwargs)

        if type(lat) == list:
            for la, lo in zip(lat, lon):
                marker = folium.CircleMarker([la, lo], **kw)
                marker.add_to(self.map)
        else:
            marker = folium.CircleMarker([lat, lon], **kw)
            marker.add_to(self.map)

    def show_in_notebook(self):
        return self.map
