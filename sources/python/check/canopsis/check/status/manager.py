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

from time import time

from canopsis.middleware.registry import MiddlewareRegistry
from canopsis.common.utils import get_first
from canopsis.common.init import basestring
from canopsis.configuration.configurable.decorator import (
    add_category, conf_paths
)
from canopsis.configuration.parameters import Parameter
from canopsis.check.status.conf import StatusConfiguration

OFF = 0
ONGOING = 1
STEALTHY = 2
FLAPPING = 3
CANCELED = 4

CONF_PATH = 'check/archiver.conf'
CATEGORY = 'ARCHIVER'


@conf_paths(CONF_PATH)
@add_category(CATEGORY)
class StatusManager(MiddlewareRegistry):

    class Error(Exception):
        """Handle StatusManager errors.
        """

    # status keys
    STATUS = 'status'  #: status event field name.
    VALUE = 'value'  #: status value key name.
    STATE = 'state'  #: state value key name.
    TIMESTAMP = 'timestamp'  #: timestamp value key name.
    LAST_STATE_CHANGE = 'last_state_change'  #: last state change ts key name.
    FLAPPING_TIMES = 'flapping_times'  #: flapping timestamps status key name.
    STEALTHY_TIME = 'stealthy_time'  #: stealthy time status key name.

    # attribute names
    FLAPPING_FREQ = 'flapping_freq'  #: flapping freq attribute name.
    FLAPPING_TIME = 'flapping_time'  #: flapping time attribute name.
    STEALTHY_TIME = 'stealthy_time'  #: stealthy time attribute name.
    RESTORE_EVENT = 'restore_event'  #: restore event attribute name.
    EXCLUSION_FIELDS = 'exclusion_fields'  #: exclusion fields attribute name.
    STATUS_CONF = 'status_conf'  #: status attribute name.

    DEFAULT_FLAPPING_FREQ = 10  #: default flapping freq value.
    DEFAULT_FLAPPING_TIME = 3600  #: default flapping time value.
    DEFAULT_STEALTHY_TIME = 360  #: default stealthy time value.
    DEFAULT_STEALTHY_SHOW = 360  #: default stealthy show value.
    DEFAULT_RESTORE_EVENT = True  #: default restore event value.

    EVENTS_STORAGE = 'events_storage'  #: events storage name.
    EVENTS_LOG_STORAGE = 'events_log_storage'  #: events log storage name.
    CONF_STORAGE = 'conf_storage'  #: conf storage name.
    STATUS_STORAGE = 'status_storage'  #: status storage name.

    def __init__(
            self,
            autolog=False, exclusion_fields=None, status_conf=None,
            events_storage=None, events_log_storage=None, conf_storage=None,
            status_storage=None,
            stealthy_time=DEFAULT_STEALTHY_TIME,
            stealthy_show=DEFAULT_STEALTHY_SHOW,
            flapping_freq=DEFAULT_FLAPPING_FREQ,
            flapping_time=DEFAULT_FLAPPING_TIME,
            restore_event=DEFAULT_RESTORE_EVENT,
            *args, **kwargs
    ):

        super(StatusManager, self).__init__(*args, **kwargs)

        self._status_conf = status_conf
        self._flapping_freq = flapping_freq
        self._flapping_time = flapping_time
        self._stealthy_time = stealthy_time
        self._stealthy_show = stealthy_show
        self._restore_event = restore_event
        self._exclusion_fields = (
            [] if exclusion_fields is None else exclusion_fields
        )

        # set storages
        self[StatusManager.EVENTS_STORAGE] = events_storage
        self[StatusManager.EVENTS_LOG_STORAGE] = events_log_storage
        self[StatusManager.CONF_STORAGE] = conf_storage
        self[StatusManager.STATUS_STORAGE] = status_storage

    @property
    def status_conf(self):
        """Get status configuration.

        :return: this status configuration.
        :rtype: StatusConfiguration
        """

        return self._status_conf

    @status_conf.setter
    def status_conf(self, value):
        """Change of status configuration.

        :param value: new status configuration to use.
        :type value: StatusConfiguration
        """

        self._status_conf = value

    @property
    def stealthy_time(self):
        """Get stealthy time.

        :rtype: float
        """

        return self._stealthy_time

    @stealthy_time.setter
    def stealthy_time(self, value):
        """Change of stealthy time.

        :param float value: new stealthy time to use.
        """

        self._stealthy_time = value

    @property
    def stealthy_show(self):
        """Get stealthy show.

        :rtype: float
        """

        return self._stealthy_show

    @stealthy_show.setter
    def stealthy_show(self, value):
        """Change of stealthy show.

        :param float value: new stealthy show to use.
        """

        self._stealthy_show = value

    @property
    def flapping_freq(self):
        """Get flapping frequency.

        :rtype: int
        """

        return self._flapping_freq

    @flapping_freq.setter
    def flapping_freq(self, value):
        """Change of flapping frequency.

        :param int value: new flapping frequency to use.
        """

        self._flapping_freq = value

    @property
    def flapping_time(self):
        """Get flapping time.

        :rtype: float
        """

        return self._flapping_time

    @flapping_time.setter
    def flapping_time(self, value):
        """Change of flapping time.

        :param float value: new flapping time to use.
        """

        self._flapping_time = value

    @property
    def restore_event(self):
        """Get restore event.

        :rtype: bool
        """

        return self._restore_event

    @restore_event.setter
    def restore_event(self, value):
        """Change of restore_event value.

        :param bool value: new restore_event to use.
        """

        self._restore_event = value

    @property
    def exclusion_fields(self):
        """Get exclusion fields.

        :rtype: list
        """

        return self._exclusion_fields

    @exclusion_fields.setter
    def exclusion_fields(self, value):
        """Change of exclusion_fields.

        :param list value: new exclusion_fields to use.
        """

        self._exclusion_fields = value

    def reload_configuration(self):

        # reconfigure this StatusManager
        self.apply_configuration()

        state_config = get_first(
            self[StatusManager.CONF_STORAGE].find_elements(
                {'crecord_type': 'statusmanagement'}
            )
        )

        getconf = state_config.get
        if state_config is not None:
            self.flapping_freq = getconf('flapping_freq', self.flapping_freq)
            self.flapping_time = getconf('flapping_time', self.flapping_time)
            self.stealthy_time = getconf('stealthy_time', self.stealthy_time)
            self.stealthy_show = getconf('stealthy_show', self.stealthy_show)
            self.restore_event = getconf('restore_event', self.restore_event)

    def put_status(self, entityid, status):
        """Put status in database, identified by the input entityid.

        :param str entityid: status entity id.
        :param dict status: status to put.
        """
        self[StatusManager.STATUS_STORAGE][entityid] = status

    def check_statuses(self, event, devent):
        """
        Args:
            event map of the current event
            devent map of the previous evet
        """

        raise NotImplementedError()

    def get_event(self, rk):
        """Get an event related to input rk.

        :param str rk: event rk to find.
        :return: ``rk`` event.
        :rtype: dict
        """

        return self[StatusManager.EVENTS_STORAGE].get(_id=rk)

    def find_statuses(self, query=None, expired=False):
        """Find statuses.

        :param dict query: find query to use.
        :param bool expired: find only expired statuses.
        :return: all corresponding statuses.
        :rtype: MongoCursor
        """

        if expired:
            # prepare the query in order to retrieve all expired statuses
            now = time()

            expiredquery = {
                '$or': [
                    {  # stealthy with stealthy_time lower than stealthy_show
                        StatusManager.VALUE: STEALTHY,
                        StatusManager.STEALTHY_TIME: {
                            '$lt': now - self.stealthy_show
                        }
                    },
                    {  # archiver with flapping times lower than flapping time
                        StatusManager.VALUE: FLAPPING,
                        StatusManager.FLAPPING_TIMES: {
                            '$lt': now - self.flapping_time
                        }
                    }
                ]
            }

            if query is None:
                query = expiredquery

            else:
                query = {
                    '$and': [
                        query, expiredquery
                    ]
                }

        # get statuses
        statuses = self[StatusManager.STATUS_STORAGE].find_elements(
            query=query
        )

        return statuses

    def archive_event(self, event):
        """Store an event.

        :param dict event: event to store.
        """

        self[StatusManager.EVENTS_STORAGE][event['rk']] = event

    def set_status(self, entityid, status):
        """Set entity status properties.

        :param str entityid: entity id.
        :param status: entity status to set.
        :type status: dict or str
        :param dict extra: extra properties to associate with the status.
        """

        if isinstance(status, basestring):
            status = {'value': status}

        self[StatusManager.STATUS_STORAGE][entityid] = status

    def get_status(self, entityid):
        """Get entity status properties.

        :param str entityid: entity id.
        :return: entity status value.
        :rtype: str
        """

        return self[StatusManager.STATUS_STORAGE].get(_id=entityid)

    def _conf(self, *args, **kwargs):

        result = super(StatusManager, self)._conf(*args, **kwargs)

        content = [
            Parameter(
                StatusManager.FLAPPING_FREQ, int,
                StatusManager.DEFAULT_FLAPPING_FREQ
            ),
            Parameter(
                StatusManager.FLAPPING_TIME, int,
                StatusManager.DEFAULT_FLAPPING_TIME
            ),
            Parameter(
                StatusManager.STEALTHY_TIME, int,
                StatusManager.DEFAULT_STEALTHY_TIME
            ),
            Parameter(
                StatusManager.RESTORE_EVENT, Parameter.bool,
                StatusManager.DEFAULT_RESTORE_EVENT
            ),
            Parameter(StatusManager.EXCLUSION_FIELDS, Parameter.array, []),
            Parameter(
                StatusManager.STATUS_CONF,
                parser=lambda value: StatusConfiguration(
                    Parameter.hashmap(value)
                )
            )
        ]

        result.add_unified_category(name=CATEGORY, new_content=content)

        return result
