# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import cmocean

class Colormaps(object):
    def __init__(self, default_cmap='jet'):
        self.default_cmap = default_cmap
        cmapname_list = cmocean.cm.cmapnames[:]
        self.cmap_mapping = {}
        for cmap in sorted(cmapname_list):
            cmap_string = 'cmocean.cm.{}'.format(cmap)
            self.cmap_mapping[cmap_string] = eval(cmap_string)

        # self.cmap_mapping = {'cmocean.cm.haline': cmocean.cm.haline,
        #                      'cmocean.cm.thermal': cmocean.cm.thermal,
        #                      'cmocean.cm.oxy': cmocean.cm.oxy}

    def get_list(self):
        return sorted(self.cmap_mapping)

    def get(self, cmap):
        return self.cmap_mapping.get(cmap, self.default_cmap)