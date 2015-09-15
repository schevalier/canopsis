#!/usr/bin/env python
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

from unittest import TestCase, main

from random import randint

from canopsis.common.utils import path
from canopsis.check.archiver import (
    Archiver, OFF, ONGOING, STEALTHY, FLAPPING, CANCELED, StatusConfiguration
)


ARCHIVER = None


def setFields(_map, **kwargs):
    for key in kwargs:
        _map[key] = kwargs[key]


class KnownValues(TestCase):
    def setUp(self):
        self.archiver = Archiver(
            db='test',
            autolog=True
        )

    def _test_01_check_statuses(self):

        rk = 'test_03_check_statuses'
        ts = 14389

        devent = {
            'rk': rk,
            'status': 0,
            'timestamp': ts,
            'state': 0
        }

        event = {
            'rk': rk,
            'status': 0,
            'timestamp': ts + 11,
            'state': 0,
            'last_state_change': ts - 389
        }

        # Check that event stays off even if it appears
        # more than the bagot freq in the stealthy/bagot interval
        for x in range(1, 50):
            self.archiver.check_statuses(event, devent)
            devent = event.copy()
            setFields(event, timestamp=(event['timestamp'] + 1))
            self.assertEqual(event['status'], OFF)

        # Set state to alarm, event should be On Going
        setFields(event, state=1)
        self.archiver.check_statuses(event, devent)
        self.assertEqual(event['status'], ONGOING)
        devent = event.copy()

        # Set state back to Ok, event should be Stealthy
        setFields(event, state=0)
        self.archiver.check_statuses(event, devent)
        self.assertEqual(event['status'], STEALTHY)
        devent = event.copy()

        # Move TS out of stealthy range, event should be On Going
        setFields(event, state=1, timestamp=event['timestamp'] + 1000)
        self.archiver.check_statuses(event, devent)
        self.assertEqual(event['status'], ONGOING)
        devent = event.copy()

        # Check that the event is at Bagot when the requirments are met
        for x in range(1, 14):
            if x % 2:
                setFields(event, state=0 if event['state'] else 1)
            self.archiver.check_statuses(event, devent)
            setFields(event, timestamp=(event['timestamp'] + 1))
            if devent['bagot_freq'] >= self.archiver.flapping_freq:
                self.assertEqual(event['status'], FLAPPING)
            devent = event.copy()

        # Check that the event is On Going if out of the Bagot time interval
        setFields(event, state=1, timestamp=event['timestamp'] + 4000)
        self.archiver.check_statuses(event, devent)
        self.assertEqual(event['status'], STEALTHY)
        devent = event.copy()


class TestStatusConfiguration(TestCase):
    """Test the StatusConfiguration object.
    """

    def setUp(self):

        self.value = randint(-100, 100)
        self.name = '{0}'.format(self.value)
        self.status_conf = StatusConfiguration(
            {
                self.name: {
                    StatusConfiguration.CODE: self.value,
                    StatusConfiguration.TASK: path(setFields)
                }
            }
        )

    def test_value(self):
        """Test the value method.
        """

        value = self.status_conf.value(self.name)

        self.assertEqual(value, self.value)

    def test_unknownvalue(self):
        """Test with an unknown name.
        """

        self.assertRaises(
            StatusConfiguration.Error,
            self.status_conf.value, TestStatusConfiguration.__name__
        )

    def test_name(self):
        """Test with a known name.
        """

        name = self.status_conf.name(self.value)

        self.assertEqual(name, self.name)

    def test_unknownname(self):
        """Test with an unknown value.
        """

        self.assertRaises(
            StatusConfiguration.Error, self.status_conf.name, self.value + 1
        )

    def test_task_by_name(self):
        """Test wit a known task by name.
        """

        task = self.status_conf.task(self.name)

        self.assertEqual(task, setFields)

    def test_task_by_value(self):
        """Test wit a known task by value.
        """

        task = self.status_conf.task(self.value)

        self.assertEqual(task, setFields)

    def test_task_by_dict(self):
        """Test wit a known task by dict.
        """

        status = {StatusConfiguration.CODE: self.value}

        task = self.status_conf.task(status)

        self.assertEqual(task, setFields)

    def test_unknowntask_by_name(self):
        """Test wit an unknown task by name.
        """

        self.assertRaises(
            StatusConfiguration.Error,
            self.status_conf.task, TestStatusConfiguration.__name__
        )

    def test_unknowntask_by_value(self):
        """Test wit an unknown task by value.
        """

        self.assertRaises(
            StatusConfiguration.Error, self.status_conf.task, self.value + 1
        )

    def test_unknowntask_by_dict(self):
        """Test wit an unknown task by dict.
        """

        status = {StatusConfiguration.CODE: self.value + 1}

        self.assertRaises(
            StatusConfiguration.Error, self.status_conf.task, status
        )

if __name__ == "__main__":
    main()
