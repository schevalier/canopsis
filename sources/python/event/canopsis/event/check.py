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

from canopsis.event.base import Event, AuthoredEventMixin, ReferenceEventMixin
from canopsis.configuration.configurable.decorator import conf_paths
from canopsis.configuration.configurable.decorator import add_category
from canopsis.configuration.model import Parameter


CONF_PATH = 'event/check.conf'
CATEGORY = 'CHECK'
CONTENT = [
    Parameter('state', int)
]


class Check(Event):
    STATE = 'state'  #: state field name

    OK = 0  #: ok state value
    MINOR = 1  #: minor state value
    MAJOR = 2  #: major state value
    CRITICAL = 3  #: critical state value

    DEFAULT_STATE = OK
    DEFAULT_EVENT_TYPE = 'check'  #: check event type

    @property
    def state(self):
        if Check.STATE not in self:
            self.state = None

        return self[Check.STATE]

    @state.setter
    def state(self, value):
        if value is None:
            value = self.DEFAULT_STATE

        self[Check.STATE] = value

    @classmethod
    def get_configurable(cls):
        confcls = Event.get_configurable()

        conf_decorator = conf_paths(CONF_PATH)
        cat_decorator = add_category(CATEGORY, content=CONTENT)

        return conf_decorator(cat_decorator(confcls))


class ChangeState(Check, AuthoredEventMixin, ReferenceEventMixin):

    DEFAULT_EVENT_TYPE = 'changestate'

    @classmethod
    def get_configurable(cls):
        confcls = Check.get_configurable()

        conf_decorator = conf_paths(CONF_PATH)
        cat_decorator = add_category('CHANGESTATE')

        return conf_decorator(cat_decorator(confcls))
