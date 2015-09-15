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

from canopsis.old.account import Account
from canopsis.old.record import Record
from canopsis.old.rabbitmq import Amqp
from canopsis.middleware.registry import MiddlewareRegistry
from canopsis.common.utils import get_first
from canopsis.common.init import basestring
from canopsis.event import get_routingkey
from canopsis.engines.core import publish
from canopsis.configuration.configurable.decorator import (
    add_category, conf_paths
)
from canopsis.configuration.parameters import Parameter
from canopsis.task.core import register_task, get_task
from canopsis.check.manager import CheckManager

from copy import deepcopy

OFF = 0
ONGOING = 1
STEALTHY = 2
FLAPPING = 3
CANCELED = 4

CONF_PATH = 'check/archiver.conf'
CATEGORY = 'ARCHIVER'


class StatusConfiguration(dict):
    """Manage status configuration.

    A status configuration links status task and code with a name.
    """

    class Error(Exception):
        """Handle StatusConfiguration errors.
        """

    CODE = 'code'  #: status code property name.
    TASK = 'task'  #: status task property name.

    def __init__(self, status):

        super(StatusConfiguration, self).__init__(status)

        self.status_name_by_code = {}

        for name in self:
            params = self[name]
            self.status_name_by_code[params[self.CODE]] = name

    def value(self, name):
        """Get status value related to input name.

        :param str name: status name.
        :return: status code corresponding to input name.
        :rtype: int
        """

        result = None

        try:
            value = self[name]
        except KeyError:
            raise StatusConfiguration.Error(
                'Status {0} not registered in {1}'.format(name, self)
            )
        else:
            try:
                result = value[StatusConfiguration.CODE]
            except KeyError:
                raise StatusConfiguration.Error(
                    'Status {0} has no code in {1}'.format(name, value)
                )

        return result

    def name(self, code):
        """Get status name from input status code.

        :param int code: status code.
        :return: related status name.
        :rtype: str
        """

        try:
            result = self.status_name_by_code[code]

        except KeyError:
            raise StatusConfiguration.Error(
                'Code {0} does not exist in {1}'.format(code, self)
            )

        else:
            return result

    def task(self, status):
        """Get task related to input status name/code.

        :param status: status from where get the right task to process it.
        :type status: int or str or dict
        :return: task function able to process an event with input status.
        :rtype: function
        """

        value = status

        if isinstance(status, dict):
            name = self.name(status[StatusConfiguration.CODE])
            value = self[name]

        elif isinstance(status, int):
            name = self.name(status)
            value = self[name]

        elif isinstance(status, basestring):
            try:
                value = self[status]
            except KeyError:
                raise StatusConfiguration.Error(
                    'Status {0} not registered in {1}'.format(status, self)
                )

        try:
            taskpath = value[StatusConfiguration.TASK]

        except KeyError:
            raise StatusConfiguration.Error(
                'No task registered in {0} ({1})'.format(status, value)
            )

        else:
            result = get_task(taskpath)

            if result is None:
                raise StatusConfiguration.Error(
                    'No task registered to {0} in {1}'.format(status, value)
                )

            return result


@conf_paths(CONF_PATH)
@add_category(CATEGORY)
class Archiver(MiddlewareRegistry):

    class Error(Exception):
        """Handle Archiver errors.
        """

    # status keys
    STATUS = 'status'  #: status event field name.
    VALUE = 'value'  #: status value key name
    STATE = 'state'  #: state value key name
    TIMESTAMP = 'timestamp'  #: timestamp value key name
    LAST_STATE_CHANGE = 'last_state_change'  #: last state change ts key name

    #: pending time when an alert state becomes stable
    PENDING_TIME = 'pending_time'
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

        super(Archiver, self).__init__(*args, **kwargs)

        # set storages
        self[Archiver.EVENTS_STORAGE] = events_storage
        self[Archiver.EVENTS_LOG_STORAGE] = events_log_storage
        self[Archiver.CONF_STORAGE] = conf_storage
        self[Archiver.STATUS_STORAGE] = status_storage

        # set attributes
        self.stealthy_show = stealthy_show
        self.stealthy_time = stealthy_time
        self.flapping_freq = flapping_freq
        self.flapping_time = flapping_time
        self.restore_event = restore_event
        self.exclusion_fields = exclusion_fields
        self.status_conf = status_conf

        self.autolog = autolog

        self.account = Account(user="root", group="root")

        self.amqp = Amqp(
            logging_level=self.log_lvl,
            logging_name='archiver-amqp'
        )

        self.reset_stealthy_event_duration = time()

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

        self._status = value

    @property
    def flapping_freq(self):
        return self._flapping_freq

    @flapping_freq.setter
    def flapping_freq(self, value):
        self._flapping_freq = value

    @property
    def flapping_time(self):
        return self._flapping_time

    @flapping_time.setter
    def flapping_time(self, value):
        self._flapping_time = value

    @property
    def restore_event(self):
        return self._restore_event

    @restore_event.setter
    def restore_event(self, value):
        self._restore_event = value

    @property
    def exclusion_fields(self):
        return self._exclusion_fields

    @exclusion_fields.setter
    def exclusion_fields(self, value):
        self._exclusion_fields = value

    def reload_configuration(self):

        # reconfigure this Archiver
        self.apply_configuration()

        state_config = get_first(self[Archiver.CONF_STORAGE].find_elements(
            {'crecord_type': 'statusmanagement'}
        ))

        getconf = state_config.get
        if state_config is not None:
            self.flapping_freq = getconf('flapping_freq', self.flapping_freq)
            self.flapping_time = getconf('flapping_time', self.flapping_time)
            self.stealthy_time = getconf('stealthy_time', self.stealthy_time)
            self.stealthy_show = getconf('stealthy_show', self.stealthy_show)
            self.restore_event = getconf('restore_event', self.restore_event)

    def reset_status_event(self, reset_type):
        """Trigger event status reset to off/on going status if event are in
        FLAPPING or STEALTHY status.

        :param reset_type: event status to consider and change.
        :type int: This is en enum, can be either FLAPPING or STEALTHY
        """

        def _publish_event(event):
            rk = event.get('rk', get_routingkey(event))
            self.logger.info("Sending event {0}".format(rk))
            publish(
                event=event, rk=rk, publisher=self.amqp
            )

        if reset_type not in [FLAPPING, STEALTHY]:
            self.logger.info('wrong reset type given, will not process.')
            return

        # Dynamic method parameter depends on reset type input
        compare_property = {
            FLAPPING: 'last_state_change',
            STEALTHY: 'ts_first_stealthy'
        }[reset_type]

        configuration_delay = {
            FLAPPING: self.flapping_time,
            STEALTHY: self.stealthy_show
        }[reset_type]

        event_cursor = self[Archiver.EVENTS_STORAGE].find_elements(
            query={'crecord_type': 'event', 'status': reset_type}
        )

        # Change all potention reset type events
        for event in event_cursor:
            # This is a flapping event.
            is_show_delay_passed = \
                time() - event[compare_property] >= configuration_delay

            # Check the stealthy intervals
            if is_show_delay_passed:

                self.logger.info(
                    'Event {0} no longer in status {1}'.format(
                        event['rk'],
                        reset_type
                    )
                )

                new_status = ONGOING if event['state'] else OFF
                self.set_status(event, new_status)
                event['pass_status'] = 1
                _publish_event(event)

    def is_flapping(self, event):
        """
        Args:
            event map of the current evet
        Returns:
            ``True`` if the event is flapping
            ``False`` otherwise
        """

        ts_curr = event['timestamp']
        ts_first_flapping = event.get('ts_first_flapping', 0)
        ts_diff_flapping = ts_curr - ts_first_flapping
        freq = event.get('flapping_freq', -1)

        result = ts_diff_flapping <= self.flapping_time and freq >= self.flapping_freq

        return result

    def is_stealthy(self, event, d_status):
        """
        Args:
            event map of the current evet
            d_status status of the previous event
        Returns:
            ``True`` if the event is stealthy
            ``False`` otherwise
        """

        ts_diff = event['timestamp'] - event['ts_first_stealthy']
        result = ts_diff <= self.stealthy_time and d_status != STEALTHY
        return result

    def set_status(self, event, status, devent=None):
        """
        Args:
            event map of the current event
            status status of the current event
        """

        log = 'Status is set to {} for event {}'.format(status, event['rk'])
        flapping_freq = event.get('flapping_freq', 0)
        values = {
            OFF: {
                'freq': flapping_freq,
                'name': 'Off'
            },
            ONGOING: {
                'freq': flapping_freq,
                'name': 'On going'
            },
            STEALTHY: {
                'freq': flapping_freq,
                'name': 'Stealthy'
            },
            FLAPPING: {
                'freq': flapping_freq + 1,
                'name': 'Bagot'
            },
            CANCELED: {
                'freq': flapping_freq,
                'name': 'Cancelled'
            }
        }

        self.logger.debug(log.format(values[status]['name']))

        # This is an additional check as stealthy
        # status is not properly managed until now
        if status != STEALTHY:
            event['status'] = status

        elif devent['state'] != 0 and event['state'] == 0:
            delta = time() - event['last_state_change']

            if delta < self.stealthy_time:
                event['status'] = status

        event['flapping_freq'] = values[status]['freq']

        if status not in [STEALTHY, FLAPPING]:
            event['ts_first_stealthy'] = 0

    def put_status(self, rk, status, data=None):

        if data is None:
            data = {}

        data[Archiver.STATUS] = status

        self[Archiver.STATUS_STORAGE][rk] = data

    def check_stealthy(self, devent, ts):
        """
        Args:
            devent map of the previous event
            ts timestamp of the current event
        Returns:
            ``True`` if the event should stay stealthy
            ``False`` otherwise
        """
        result = False

        if devent['status'] != STEALTHY:
            result = (ts - devent['ts_first_stealthy']) <= self.stealthy_show

        return result

    def check_statuses(self, event, devent):
        """
        Args:
            event map of the current event
            devent map of the previous evet
        """

        if event.get('pass_status', 0):
            event['pass_status'] = 0
            return

        event_ts = event['timestamp']

        event['flapping_freq'] = devent.get('flapping_freq', 0)
        event['ts_first_stealthy'] = devent.get('ts_first_stealthy', 0)
        event['ts_first_flapping'] = devent.get('ts_first_flapping', 0)
        dstate = devent['state']
        # Increment frequency if state changed and set first occurences
        if (
                (not dstate and event['state']) or
                dstate and not event['state']
        ):

            if event['state']:
                event['ts_first_stealthy'] = event_ts
            else:
                event['ts_first_stealthy'] = event_ts

            event['flapping_freq'] += 1

            if not event['ts_first_flapping']:
                event['ts_first_flapping'] = event_ts

        # Out of flapping interval, reset variables
        if event['ts_first_flapping'] - event_ts > self.flapping_time:
            event['ts_first_flapping'] = 0
            event['flapping_freq'] = 0

        # If not canceled, proceed to check the status
        if (
                devent.get('status', ONGOING) != CANCELED or
                (
                    dstate != event['state']
                    and (
                        self.restore_event or
                        event['state'] == OFF or
                        dstate == OFF
                    )
                )
        ):
            # Check the stealthy intervals
            if self.check_stealthy(devent, event_ts):

                if self.is_flapping(event):
                    self.set_status(event, FLAPPING)

                else:
                    self.set_status(event, STEALTHY, devent=devent)

            # Else proceed normally
            elif event['state'] == OFF:
                # If still non-alert, can only be OFF
                if (
                        not self.is_flapping(event)
                        and not self.is_stealthy(event, devent['status'])
                ):
                    self.set_status(event, OFF)

                elif self.is_flapping(event):
                    self.set_status(event, FLAPPING)

                elif self.is_stealthy(event, devent['status']):
                    self.set_status(event, STEALTHY, devent=devent)

            else:
                # If not flapping/stealthy, can only be ONGOING
                if (
                        not self.is_flapping(event)
                        and not self.is_stealthy(event, devent['status'])
                ):
                    self.set_status(event, ONGOING)

                elif self.is_flapping(event):
                    self.set_status(event, FLAPPING)

                elif self.is_stealthy(event, devent['status']):

                    if devent['status'] == OFF:
                        self.set_status(event, ONGOING)

                    else:
                        self.set_status(event, STEALTHY, devent=devent)

        else:
            self.set_status(event, CANCELED)

    def check_event(self, _id, event):
        """
            This method aims to buffer and process incoming events.
            Processing is done on buffer to reduce database operations.
        """

        result = None

        # As this was not done until now... setting event primary key
        event['_id'] = _id
        # copy the event
        event = deepcopy(event)

        # get old event
        devent = self[Archiver.EVENTS_STORAGE].get(_id=_id)
        # set changed and new_event flags
        changed = new_event = devent is None

        # get state and state type
        state = event['state']
        state_type = event['state_type']

        # get the right now moment
        now = int(time())
        # and ensure timestamp equals timestamp
        event.setdefault('timestamp', now)

        if new_event:

            devent = {}
            # No old record
            event['ts_first_stealthy'] = 0
            old_state = state

        else:

            old_state = devent['state']
            old_state_type = devent['state_type']
            event['last_state_change'] = devent.get(
                'last_state_change',
                event['timestamp']
            )

            if state != old_state:
                event['previous_state'] = old_state
                changed = True

            elif state_type != old_state_type:
                changed = True

            self.check_statuses(event, devent)

        if changed:
            # Tests if change is from alert to non alert
            if (
                    'last_state_change' in event
                    and (state == 0 or (state > 0 and old_state == 0))
            ):

                event['previous_state_change_ts'] = event['last_state_change']

            event['last_state_change'] = event['timestamp']

        if new_event:
            # insert the new event
            record = Record(event)
            record.type = 'event'
            event = record.dump()
            self[Archiver.EVENTS_STORAGE].put_element(element=event)

        else:
            change = {}

            # keep ack information if status does not reset event
            if 'ack' in devent:

                if event['status'] == 0:
                    change['ack'] = {}

                else:
                    change['ack'] = devent['ack']

            # keep cancel information if status does not reset event
            if 'cancel' in devent:

                if event['status'] not in [0, 1]:
                    change['cancel'] = devent['cancel']

                else:
                    change['cancel'] = {}

            # Remove ticket information in case state is back to normal
            # (both ack and ticket declaration case)
            if 'ticket_declared_author' in devent and event['status'] == 0:

                change['ticket_declared_author'] = None
                change['ticket_declared_date'] = None

            # Remove ticket information in case state is back to normal
            # (ticket number declaration only case)
            if 'ticket' in devent and event['status'] == 0:

                del devent['ticket']

                if 'ticket_date' in devent:
                    del devent['ticket_date']

            # Generate diff change from old event to new event
            for key in event:

                if key not in self.exclusion_fields:

                    if (
                            key in event and
                            key in devent and
                            devent[key] != event[key]
                    ):
                        change[key] = event[key]

                    elif key in event and key not in devent:
                        change[key] = event[key]

            # Manage keep state key that allow
            # from UI to keep the choosen state
            # into until next ok state
            event_reset = False

            # When a event is ok again, dismiss keep_state statement
            if devent.get('keep_state') and event['state'] == 0:
                change['keep_state'] = False
                event_reset = True

            # assume we do not just received a keep state and
            # if keep state was sent previously
            # then override state of new event
            if 'keep_state' not in event:

                if not event_reset and devent.get('keep_state'):
                    change['state'] = devent['state']

            # Keep previous output
            if 'keep_state' in event:
                change['change_state_output'] = event['output']
                change['output'] = devent.get('output', '')

            if change:
                self[Archiver.EVENTS_STORAGE].update_elements(data=change)

        # I think that is the right condition to log
        have_to_log = event.get('previous_state', state) != state
        if have_to_log:

            # store ack information to log collection
            if 'ack' in devent:
                event['ack'] = devent['ack']

            _id = '{0}.{1}'.format(_id, time())
            event['_id'] = _id

            if getattr(event, 'type', None) != 'event':
                record = Record(event)
                record.type = 'event'
                event = record.dump()
            self[Archiver.EVENTS_LOG_STORAGE].put_element(element=event)

        # Half useless retro compatibility
        if 'state' in event and event['state']:
            result = _id

        return result

    def get_event(self, rk):
        """Get an event related to input rk.

        :param str rk: event rk to find.
        :return: ``rk`` event.
        :rtype: dict
        """

        return self[Archiver.EVENTS_STORAGE].get(_id=rk)

    def archive_event(self, event):
        """Store an event.

        :param dict event: event to store.
        """

        self[Archiver.EVENTS_STORAGE][event['rk']] = event

    def set_status(self, entityid, status):
        """Set entity status properties.

        :param str entityid: entity id.
        :param status: entity status to set.
        :type status: dict or str
        :param dict extra: extra properties to associate with the status.
        """

        if isinstance(status, basestring):
            status = {'value': status}

        self[Archiver.STATUS_STORAGE][entityid] = status

    def get_status(self, entityid):
        """Get entity status properties.

        :param str entityid: entity id.
        :return: entity status value.
        :rtype: str
        """

        return self[Archiver.STATUS_STORAGE].get(_id=entityid)

    def _conf(self, *args, **kwargs):

        result = super(Archiver, self)._conf(*args, **kwargs)

        content = [
            Parameter(Archiver.FLAPPING_FREQ, int, 10),
            Parameter(Archiver.FLAPPING_TIME, int, 3600),
            Parameter(Archiver.STEALTHY_TIME, int, 360),
            Parameter(Archiver.STEALTHY_SHOW, int, 360),
            Parameter(Archiver.RESTORE_EVENT, Parameter.bool, True),
            Parameter(Archiver.EXCLUSION_FIELDS, Parameter.array, []),
            Parameter(
                Archiver.STATUS_CONF,
                parser=lambda value: StatusConfiguration(
                    Parameter.hashmap(value)
                )
            )
        ]

        result.add_unified_category(name=CATEGORY, new_content=content)

        return result
