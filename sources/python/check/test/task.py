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

from canopsis.check.archiver import (
    Archiver, OFF, ONGOING, STEALTHY, FLAPPING, CANCELED, StatusConfiguration
)

from time import time

from canopsis.common.utils import path
from canopsis.check.task import (
    criticity, process_status_canceled, process_status_flapping,
    process_status_off, process_status_ongoing, process_status_stealthy,
    process_supervision_status, update_status
)

from random import randint

from unittest import TestCase, main


def rand(lower=0, upper=100):
    """Get a random number in [lower, upper].

    :param int lower: lower bound. 0 by default.
    :param int upper: upper bound. 100 by default.
    :return: a random integer in [lower, upper].
    :rtype: int
    """

    return randint(lower, upper)


class TestArchiver(object):
    """Archiver to use in order to success tests.
    """

    def __init__(self):

        super(TestArchiver, self).__init__()

        self.flapping_time = 3600
        self.stealthy_time = 3600
        self.flapping_freq = 5
        self.status_conf = StatusConfiguration(
            {
                'off': {
                    StatusConfiguration.CODE: OFF,
                    StatusConfiguration.TASK: path(process_status_off)
                },
                'canceled': {
                    StatusConfiguration.CODE: CANCELED,
                    StatusConfiguration.TASK: path(process_status_canceled)
                },
                'flapping': {
                    StatusConfiguration.CODE: FLAPPING,
                    StatusConfiguration.TASK: path(process_status_flapping)
                },
                'stealthy': {
                    StatusConfiguration.CODE: STEALTHY,
                    StatusConfiguration.TASK: path(process_status_stealthy)
                },
                'ongoing': {
                    StatusConfiguration.CODE: ONGOING,
                    StatusConfiguration.TASK: path(process_status_ongoing)
                }
            }
        )


class UpdateStatusTestCase(TestCase):
    """Test the update_status function.
    """

    def test_strstatus(self):
        """Test with a str such as status.
        """

        state = rand()
        status = 'ongoing'
        timestamp = time()

        new_status = update_status(
            state=state, status=status, timestamp=timestamp,
            archiver=TestArchiver()
        )

        self.assertEqual(
            new_status,
            {
                Archiver.VALUE: ONGOING,
                Archiver.STATE: state,
                Archiver.TIMESTAMP: timestamp
            }
        )

    def test_intstatus(self):
        """Test with an integer such as a status.
        """

        state = rand()
        status = ONGOING
        timestamp = time()

        new_status = update_status(
            state=state, status=status, timestamp=timestamp,
            archiver=TestArchiver()
        )

        self.assertEqual(
            new_status,
            {
                Archiver.VALUE: ONGOING,
                Archiver.STATE: state,
                Archiver.TIMESTAMP: timestamp
            }
        )

    def test_dictstatus(self):
        """Test with a dict such as a status.
        """

        state = rand()
        status = {Archiver.VALUE: ONGOING}
        timestamp = time()

        new_status = update_status(
            state=state, status=status, timestamp=timestamp,
            archiver=TestArchiver()
        )

        self.assertEqual(
            new_status,
            {
                Archiver.VALUE: ONGOING,
                Archiver.STATE: state,
                Archiver.TIMESTAMP: timestamp
            }
        )

    def test_wrongtypestatus(self):
        """Test with a wrong status.
        """

        state = rand()
        status = object()
        timestamp = time()

        self.assertRaises(
            Archiver.Error,
            update_status,
            state=state, status=status, timestamp=timestamp,
            archiver=TestArchiver()
        )


class CrititicyTestCase(TestCase):
    pass


class ProcessSupervisionStatusTestCase(TestCase):
    pass


class ProcessStatusCanceledTestCase(TestCase):
    """Test the process_status_canceled function.
    """

    def test_off(self):
        """Test with the off status.
        """

        status = process_status_canceled(state=0)

        self.assertEqual(status, OFF)

    def test_ongoing(self):
        """Test with an ongoing status.
        """

        status = process_status_canceled(state=1)

        self.assertEqual(status, ONGOING)


class ProcessStatusFlappingTestCase(TestCase):
    pass


class ProcessStatusOffTestCase(TestCase):
    """Test the process_status_off function.
    """


class ProcessStatusOngoingTestCase(TestCase):
    pass


class ProcessStatusStealthyTestCase(TestCase):
    pass


if __name__ == '__main__':
    main()
