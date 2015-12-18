# -*- coding: utf-8 -*-
# --------------------------------
# Copyright (c) 2015 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------

from canopsis.event.base import Event
from canopsis.configuration.configurable.decorator import conf_paths
from canopsis.configuration.configurable.decorator import add_category
from canopsis.configuration.model import Parameter


CONF_PATH = 'event/log.conf'
CATEGORY = 'LOG'
CONTENT = [
    Parameter('level'),
    Parameter('facility')
]


class Log(Event):
    LEVEL = 'level'  #: level field name
    FACILITY = 'facility'  #: facility field name

    DEFAULT_LEVEL = 'info'
    DEFAULT_FACILITY = Event.DEFAULT_CONNECTOR
    DEFAULT_EVENT_TYPE = 'log'  #: log event type

    @property
    def level(self):
        if Log.LEVEL not in self:
            self.level = None

        return self[Log.LEVEL]

    @level.setter
    def level(self, value):
        if value is None:
            value = self.DEFAULT_LEVEL

        self[Log.LEVEL] = value

    @property
    def facility(self):
        if Log.FACILITY not in self:
            self.facility = None

        return self[Log.FACILITY]

    @facility.setter
    def facility(self, value):
        if value is None:
            value = self.DEFAULT_FACILITY

        self[Log.FACILITY] = value

    @classmethod
    def get_configurable(cls):
        confcls = Event.get_configurable()

        conf_decorator = conf_paths(CONF_PATH)
        cat_decorator = add_category(CATEGORY, content=CONTENT)

        return conf_decorator(cat_decorator(confcls))
