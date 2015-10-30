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

from canopsis.middleware.registry import MiddlewareRegistry
from canopsis.configuration.configurable.decorator import conf_paths
from canopsis.configuration.configurable.decorator import add_category
from canopsis.configuration.parameters import Parameter
from canopsis.timeserie.timewindow import Period


CONF_PATH = 'logging/manager.conf'
CATEGORY = 'LOGGING'
CONTENT = [
    Parameter('rotate_period', Period.parameter)
]


@conf_paths(CONF_PATH)
@add_category(CATEGORY, content=CONTENT)
class Logging(MiddlewareRegistry):

    LOG_STORAGE = 'log_storage'
    CONTEXT_MANAGER = 'context'

    @property
    def rotate_period(self):
        if not hasattr(self, '_rotate_period'):
            self.rotate_period = None

        return self._rotate_period

    @rotate_period.setter
    def rotate_period(self, value):
        if value is None:
            value = Period(**{Period.WEEK: 1})

        self._rotate_period = value

    def __init__(
        self,
        rotate_period=None,
        log_storage=None,
        context=None,
        *args, **kwargs
    ):
        super(Logging, self).__init__(*args, **kwargs)

        if rotate_period is not None:
            self.rotate_period = rotate_period

        if log_storage is not None:
            self[Logging.LOG_STORAGE] = log_storage

        if context is not None:
            self[Logging.CONTEXT_MANAGER] = context

    def log_event(self, event):
        entity = self[Logging.CONTEXT_MANAGER].get_entity(event)
        entity_id = self[Logging.CONTEXT_MANAGER].get_entity_id(entity)

        point = (event['timestamp'], {
            'm': event['output'],
            'l': event.get('state', 0)
        })

        self[Logging.LOG_STORAGE].put(entity_id, self.rotate_period, [point])

    def grep(self, pattern, level=None, timewindow=None):
        raise NotImplementedError()
