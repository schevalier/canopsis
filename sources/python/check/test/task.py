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

        self.stealthy_time = 3600
        self.flapping_time = self.stealthy_time * 2
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


class TestProcessStatus(TestCase):
    """Common test class for process_* functions.

    This class uses a local TestArchiver such as the archiver attribute.
    """

    def setUp(self):

        self.archiver = TestArchiver()


class UpdateStatusTestCase(TestProcessStatus):
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
            archiver=self.archiver
        )

        self.assertEqual(
            new_status,
            {
                Archiver.VALUE: ONGOING,
                Archiver.STATE: state,
                Archiver.TIMESTAMP: timestamp,
                Archiver.LAST_STATE_CHANGE: timestamp
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
            archiver=self.archiver
        )

        self.assertEqual(
            new_status,
            {
                Archiver.VALUE: ONGOING,
                Archiver.STATE: state,
                Archiver.TIMESTAMP: timestamp,
                Archiver.LAST_STATE_CHANGE: timestamp
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
            archiver=self.archiver
        )

        self.assertEqual(
            new_status,
            {
                Archiver.VALUE: ONGOING,
                Archiver.STATE: state,
                Archiver.TIMESTAMP: timestamp,
                Archiver.LAST_STATE_CHANGE: timestamp
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
            archiver=self.archiver
        )

    def test_last_statechange(self):
        """Check calculus of the last_state_change.
        """

        timestamp = time()
        state = rand()
        status = {Archiver.STATE: state + 1, Archiver.VALUE: OFF}
        new_status = update_status(
            state=state, status=status, timestamp=timestamp,
            archiver=self.archiver
        )

        self.assertEqual(
            new_status[Archiver.LAST_STATE_CHANGE], timestamp
        )

    def test_last_statechange_no_state(self):
        """Check calculus of the last_state_change.
        """

        timestamp = time()
        state = rand()
        status = {Archiver.VALUE: OFF}
        new_status = update_status(
            state=state, status=status, timestamp=timestamp,
            archiver=self.archiver
        )

        self.assertEqual(
            new_status[Archiver.LAST_STATE_CHANGE], timestamp
        )

    def test_nolast_statechange(self):
        """Check calculus of the last_state_change.
        """

        timestamp = time()
        state = rand()
        status = {
            Archiver.STATE: state,
            Archiver.LAST_STATE_CHANGE: 0,
            Archiver.VALUE: OFF
        }
        new_status = update_status(
            state=state, status=status, timestamp=timestamp,
            archiver=self.archiver
        )

        self.assertEqual(
            new_status[Archiver.LAST_STATE_CHANGE], 0
        )


class CrititicyTestCase(TestCase):
    pass


class ProcessSupervisionStatusTestCase(TestCase):
    pass


class ProcessStatusCanceledTestCase(TestProcessStatus):
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


class ProcessStatusFlappingTestCase(TestProcessStatus):
    """Test the process_status_flapping function.
    """

    def test_stillflapping(self):
        """Test with old flapping status.
        """

        timestamp = time()
        status = {
            Archiver.FLAPPING_FREQ: 1,
            Archiver.PENDING_TIME: timestamp + self.archiver.flapping_time - 1,
            Archiver.STATE: 0,
            Archiver.VALUE: FLAPPING
        }
        newstatus = process_status_flapping(
            state=1,
            timestamp=timestamp, status=status, archiver=self.archiver
        )

        self.assertEqual(newstatus[Archiver.VALUE], FLAPPING)

    def test_noflapping_off(self):
        """Test end of flapping with OFF status.
        """

        timestamp = time()
        status = {
            Archiver.FLAPPING_FREQ: 1,
            Archiver.PENDING_TIME: timestamp + self.archiver.flapping_time - 1,
            Archiver.STATE: 0,
            Archiver.VALUE: FLAPPING
        }
        newstatus = process_status_flapping(
            state=0,
            timestamp=timestamp, status=status, archiver=self.archiver
        )

        self.assertEqual(newstatus[Archiver.VALUE], OFF)

    def test_noflapping_ongoing(self):
        """Test end of flapping with OFF status.
        """

        timestamp = time()
        status = {
            Archiver.FLAPPING_FREQ: 1,
            Archiver.PENDING_TIME: timestamp + self.archiver.flapping_time - 1,
            Archiver.STATE: 1,
            Archiver.VALUE: FLAPPING
        }
        newstatus = process_status_flapping(
            state=1,
            timestamp=timestamp, status=status, archiver=self.archiver
        )

        self.assertEqual(newstatus[Archiver.VALUE], ONGOING)


class ProcessStatusOffTestCase(TestProcessStatus):
    """Test the process_status_off function.
    """

    def test_off(self):
        """Test with the off status.
        """

        status = process_status_off(archiver=self.archiver)

        self.assertEqual(status, OFF)

    def test_ongoing(self):
        """Test with an ongoing status.
        """

        timestamp = time()

        new_status = process_status_off(
            archiver=self.archiver, timestamp=timestamp, state=1
        )

        self.assertEqual(
            new_status, {Archiver.VALUE: ONGOING, Archiver.STATE: 1}
        )


class ProcessStatusOngoingTestCase(TestProcessStatus):

    def test_off(self):
        """Test off status after both flapping and stealhy times.
        """

        timestamp = time()
        status = {
            Archiver.VALUE: ONGOING,
            Archiver.TIMESTAMP: timestamp,
            Archiver.PENDING_TIME: 0
        }
        new_status = process_status_ongoing(
            archiver=self.archiver, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[Archiver.VALUE], OFF)

    def test_ongoing(self):
        """Test ongoing status after both flapping and stealhy times.
        """

        timestamp = time()
        status = {
            Archiver.VALUE: ONGOING,
            Archiver.TIMESTAMP: timestamp,
            Archiver.PENDING_TIME: 0
        }
        new_status = process_status_ongoing(
            state=1,
            archiver=self.archiver, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[Archiver.VALUE], ONGOING)

    def test_stealthy(self):
        """Test stealthy status.
        """

        timestamp = time()
        status = {
            Archiver.VALUE: ONGOING,
            Archiver.TIMESTAMP: timestamp
        }
        new_status = process_status_ongoing(
            archiver=self.archiver, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[Archiver.VALUE], STEALTHY)

    def test_stealthy_with_pending_time(self):
        """Test stealthy status.
        """

        timestamp = time()
        status = {
            Archiver.VALUE: ONGOING,
            Archiver.TIMESTAMP: timestamp,
            Archiver.PENDING_TIME: timestamp
        }
        new_status = process_status_ongoing(
            archiver=self.archiver, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[Archiver.VALUE], STEALTHY)

    def test_flapping(self):
        """Test flapping status.
        """

        timestamp = time()
        status = {
            Archiver.VALUE: ONGOING,
            Archiver.TIMESTAMP: timestamp,
            Archiver.FLAPPING_FREQ: self.archiver.flapping_freq,
            Archiver.PENDING_TIME: timestamp - self.archiver.stealthy_time - 1
        }
        new_status = process_status_ongoing(
            archiver=self.archiver, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[Archiver.VALUE], FLAPPING)
        self.assertEqual(
            new_status[Archiver.FLAPPING_FREQ], self.archiver.flapping_freq + 1
        )

    def test_incflapping(self):
        """Test increment counter of flapping status.
        """

        timestamp = time()
        status = {
            Archiver.VALUE: ONGOING,
            Archiver.TIMESTAMP: timestamp,
            Archiver.FLAPPING_FREQ: self.archiver.flapping_freq - 2,
            Archiver.PENDING_TIME: timestamp - self.archiver.stealthy_time - 1
        }
        new_status = process_status_ongoing(
            archiver=self.archiver, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[Archiver.VALUE], OFF)
        self.assertEqual(
            new_status[Archiver.FLAPPING_FREQ], self.archiver.flapping_freq - 1
        )

    def test_noflapping_overtime(self):
        """Test to leave flapping cause expired flapping time.
        """

        timestamp = time()
        status = {
            Archiver.VALUE: ONGOING,
            Archiver.TIMESTAMP: timestamp,
            Archiver.FLAPPING_FREQ: self.archiver.flapping_freq,
            Archiver.PENDING_TIME: timestamp - self.archiver.flapping_time - 1
        }
        new_status = process_status_ongoing(
            archiver=self.archiver, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[Archiver.VALUE], OFF)
        self.assertEqual(
            new_status[Archiver.FLAPPING_FREQ], self.archiver.flapping_freq
        )

    def test_noflapping_ongoing(self):
        """Test to leave flapping in an ongoing status.
        """

        timestamp = time()
        status = {
            Archiver.VALUE: ONGOING,
            Archiver.TIMESTAMP: timestamp,
            Archiver.FLAPPING_FREQ: self.archiver.flapping_freq,
            Archiver.PENDING_TIME: timestamp - self.archiver.flapping_time - 1
        }
        new_status = process_status_ongoing(
            state=1,
            archiver=self.archiver, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[Archiver.VALUE], ONGOING)


class ProcessStatusStealthyTestCase(TestProcessStatus):
    pass


if __name__ == '__main__':
    main()
