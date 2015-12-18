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

from canopsis.configuration.configurable import Configurable
from canopsis.configuration.configurable.decorator import conf_paths
from canopsis.configuration.configurable.decorator import add_category
from canopsis.configuration.model import Parameter

from copy import deepcopy
from time import time
import socket
import os


CONF_PATH = 'event/event.conf'
CATEGORY = 'EVENT'
CONTENT = [
    Parameter('connector'),
    Parameter('connector_name'),
    Parameter('event_type'),
    Parameter('source_type'),
    Parameter('component'),
    Parameter('resource')
]


class Event(object):
    TIMESTAMP = 'timestamp'  #: timestamp field name
    CONNECTOR = 'connector'  #: connector field name
    CONNECTOR_NAME = 'connector_name'  #: connector_name field name
    EVENT_TYPE = 'event_type'  #: event_type field name
    SOURCE_TYPE = 'source_type'  #: source_type field name
    COMPONENT = 'component'  #: component field name
    RESOURCE = 'resource'  #: resource field name
    OUTPUT = 'output'  #: output field name
    LONG_OUTPUT = 'long_output'  #: long_output field name
    DISPLAY_NAME = 'display_name'  #: display_name field name
    METRICS = 'perf_data_array'  #: metrics field name

    DEFAULT_CONNECTOR = 'canopsis'
    DEFAULT_CONNECTOR_NAME = 'canopsis'
    DEFAULT_EVENT_TYPE = 'log'
    DEFAULT_SOURCE_TYPE = 'resource'
    DEFAULT_COMPONENT = socket.getfqdn()
    DEFAULT_RESOURCE = str(os.getpid())

    def __init__(self, raw=None, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)

        if raw is None:
            raw = {}

        self.data = raw

    @property
    def timestamp(self):
        if Event.TIMESTAMP not in self:
            self.timestamp = None

        return self[Event.TIMESTAMP]

    @timestamp.setter
    def timestamp(self, value):
        if value is None:
            value = int(time())

        self[Event.TIMESTAMP] = value

    @property
    def connector(self):
        if Event.CONNECTOR not in self:
            self.connector = None

        return self[Event.CONNECTOR]

    @connector.setter
    def connector(self, value):
        if value is None:
            value = self.DEFAULT_CONNECTOR

        self[Event.CONNECTOR] = value

    @property
    def connector_name(self):
        if Event.CONNECTOR_NAME not in self:
            self.connector_name = None

        return self[Event.CONNECTOR_NAME]

    @connector_name.setter
    def connector_name(self, value):
        if value is None:
            value = self.DEFAULT_CONNECTOR_NAME

        self[Event.CONNECTOR_NAME] = value

    @property
    def event_type(self):
        if Event.EVENT_TYPE not in self:
            self.event_type = None

        return self[Event.EVENT_TYPE]

    @event_type.setter
    def event_type(self, value):
        if value is None:
            value = self.DEFAULT_EVENT_TYPE

        self[Event.EVENT_TYPE] = value

    @property
    def source_type(self):
        if Event.SOURCE_TYPE not in self:
            self.source_type = None

        return self[Event.SOURCE_TYPE]

    @source_type.setter
    def source_type(self, value):
        if value is None:
            value = self.DEFAULT_SOURCE_TYPE

        self[Event.SOURCE_TYPE] = value

    @property
    def component(self):
        if Event.COMPONENT not in self:
            self.component = None

        return self[Event.COMPONENT]

    @component.setter
    def component(self, value):
        if value is None:
            value = self.DEFAULT_COMPONENT

        self[Event.COMPONENT] = value

    @property
    def resource(self):
        if Event.RESOURCE not in self:
            if self.source_type == Event.RESOURCE:
                self.resource = self.DEFAULT_RESOURCE

            else:
                self.resource = None

        return self[Event.RESOURCE]

    @resource.setter
    def resource(self, value):
        self[Event.RESOURCE] = value

    @property
    def output(self):
        if Event.OUTPUT not in self:
            self.output = None

        return self[Event.OUTPUT]

    @output.setter
    def output(self, value):
        self[Event.OUTPUT] = value

    @property
    def long_output(self):
        if Event.LONG_OUTPUT not in self:
            self.long_output = None

        return self[Event.LONG_OUTPUT]

    @long_output.setter
    def long_output(self, value):
        self[Event.LONG_OUTPUT] = value

    @property
    def display_name(self):
        if Event.DISPLAY_NAME not in self:
            self.display_name = None

        return self[Event.DISPLAY_NAME]

    @display_name.setter
    def display_name(self, value):
        self[Event.DISPLAY_NAME] = value

    @property
    def metrics(self):
        if Event.METRICS not in self:
            self.metrics = None

        return self[Event.METRICS]

    @metrics.setter
    def metrics(self, value):
        if value is None:
            value = []

        self[Event.METRICS] = value

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data

    @classmethod
    def get_configurable(cls):
        conf_decorator = conf_paths(CONF_PATH)
        cat_decorator = add_category(CATEGORY, content=CONTENT)
        confcls = conf_decorator(cat_decorator(Configurable))

        return confcls

    @classmethod
    def create(cls, metrics=None, **kwargs):
        if metrics is None:
            metrics = []

        confcls = cls.get_configurable()
        conf = confcls(**kwargs)
        evt = cls()

        extra = {
            kwarg: kwargs[kwarg]
            for kwarg in kwargs
            if not conf._is_local(evt, kwarg)
        }

        conf.configure(to_configure=evt)
        evt.metrics = [
            metric
            for metric in metrics
        ]

        result = deepcopy(evt.data)
        result.update(extra)

        return result

    @staticmethod
    def get_routing_key(event):
        rk = '{0}.{1}.{2}.{3}.{4}'.format(
            event[Event.CONNECTOR],
            event[Event.CONNECTOR_NAME],
            event[Event.EVENT_TYPE],
            event[Event.SOURCE_TYPE],
            event[Event.COMPONENT]
        )

        if event[Event.SOURCE_TYPE] == Event.RESOURCE:
            rk = '{0}.{1}'.format(rk, event[Event.RESOURCE])

        return rk


class AuthoredEventMixin:
    AUTHOR = 'author'  #: author field name

    DEFAULT_AUTHOR = Event.CONNECTOR_NAME

    @property
    def author(self):
        if AuthoredEventMixin.AUTHOR not in self:
            self.author = None

        return self[AuthoredEventMixin.AUTHOR]

    @author.setter
    def author(self, value):
        if value is None:
            value = AuthoredEventMixin.DEFAULT_AUTHOR

        self[AuthoredEventMixin.AUTHOR] = value


class ReferenceEventMixin:
    REFERER = 'ref_rk'  #: referer field name

    @property
    def referer(self):
        if ReferenceEventMixin.REFERER not in self:
            self.referer = None

        return self[ReferenceEventMixin.REFERER]

    @referer.setter
    def referer(self, value):
        self[ReferenceEventMixin.REFERER] = value
