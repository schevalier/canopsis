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


CONF_PATH = 'event/ack.conf'


class Ack(Event, AuthoredEventMixin, ReferenceEventMixin):

    DEFAULT_EVENT_TYPE = 'ack'

    @classmethod
    def get_configurable(cls):
        confcls = Event.get_configurable()

        conf_decorator = conf_paths(CONF_PATH)
        cat_decorator = add_category('ACK')

        return conf_decorator(cat_decorator(confcls))


class AckRemove(Event, AuthoredEventMixin, ReferenceEventMixin):

    DEFAULT_EVENT_TYPE = 'ackremove'

    @classmethod
    def get_configurable(cls):
        confcls = Event.get_configurable()

        conf_decorator = conf_paths(CONF_PATH)
        cat_decorator = add_category('ACKREMOVE')

        return conf_decorator(cat_decorator(confcls))
