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

from canopsis.check.status.conf import StatusConfiguration
from canopsis.check.status.manager import (
    StatusManager as SM, OFF, ONGOING, STEALTHY, FLAPPING, CANCELED
)

from time import time

from canopsis.common.utils import path
from canopsis.check.status.task import (
    process_status_canceled, process_status_flapping, _apply_simple_status,
    process_status_off, process_status_ongoing, process_status_stealthy,
    update_status, _update_flapping
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


class TestStatusManager(object):
    """SM to use in order to success tests.
    """

    def __init__(self):

        super(TestStatusManager, self).__init__()

        self.stealthy_time = 3600
        self.stealthy_show = 3600
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

    This class uses a local TestStatusManager such as the statusmanager
    attribute.
    """

    def setUp(self):

        self.statusmanager = TestStatusManager()


class TestApplySimpleStatus(TestCase):
    """Test the function _apply_simple_status.
    """

    def test_off(self):
        """Test with an ok state.
        """

        status = {}

        _apply_simple_status(status=status, state=0)

        self.assertEqual(status[SM.VALUE], OFF)

    def test_ongoing(self):
        """Test with a nok state.
        """

        status = {}

        _apply_simple_status(status=status, state=randint(1, 1000))

        self.assertEqual(status[SM.VALUE], ONGOING)


class TestUpdateFlapping(TestProcessStatus):
    """Test the function _update_flapping.
    """

    def test_empty_status(self):
        """Test with an empty status.
        """

        status = {}

        _update_flapping(
            statusmanager=self.statusmanager, state=0, timestamp=0,
            status=status
        )

        self.assertEqual(status, {SM.VALUE: OFF})

    def test_empty_flapping_status(self):
        """Test with empty flapping status.
        """

        status = {SM.FLAPPING_TIMES: []}

        _update_flapping(
            statusmanager=self.statusmanager, state=0, timestamp=0,
            status=status
        )

        self.assertEqual(
            status, {SM.VALUE: OFF}
        )

    def test_flapping_status(self):
        """Test wit a flapping status.
        """

        timestamp = 10**10
        status = {
            SM.FLAPPING_TIMES: [
                0, 10,
                timestamp - self.statusmanager.flapping_time - 1,
                timestamp - self.statusmanager.flapping_time
            ]
        }

        for i in range(self.statusmanager.flapping_freq):
            status[SM.FLAPPING_TIMES].append(timestamp + i)

        _update_flapping(
            statusmanager=self.statusmanager, state=0, timestamp=timestamp,
            status=status
        )

        flapping_times = list(
            timestamp + i for i in range(self.statusmanager.flapping_freq)
        )
        flapping_times.insert(0, timestamp - self.statusmanager.flapping_time)

        self.assertEqual(
            status, {
                SM.FLAPPING_TIMES: flapping_times,
                SM.VALUE: FLAPPING
            }
        )


class TestUpdateStatus(TestProcessStatus):
    """Test the update_status function.
    """

    def test_dictwithoutvalue(self):
        """Test a status without value.
        """

        self.assertRaises(
            SM.Error,
            update_status,
            state=0, status={}, timestamp=0, statusmanager=self.statusmanager
        )

    def test_wrongtypestatus(self):
        """Test with a wrong status.
        """

        state = rand()
        status = object()
        timestamp = time()

        self.assertRaises(
            SM.Error,
            update_status,
            state=state, status=status, timestamp=timestamp,
            statusmanager=self.statusmanager
        )

    def test_dictstatus(self):
        """Test with a dict such as a status.
        """

        state = rand()
        status = {SM.VALUE: ONGOING}
        timestamp = time()

        new_status = update_status(
            state=state, status=status, timestamp=timestamp,
            statusmanager=self.statusmanager
        )

        self.assertEqual(
            new_status,
            {
                SM.VALUE: ONGOING,
                SM.STATE: state,
                SM.TIMESTAMP: timestamp,
                SM.LAST_STATE_CHANGE: timestamp
            }
        )

    def test_last_statechange(self):
        """Check calculus of the last_state_change.
        """

        timestamp = time()
        state = rand()
        status = {SM.STATE: state + 1, SM.VALUE: OFF}
        new_status = update_status(
            state=state, status=status, timestamp=timestamp,
            statusmanager=self.statusmanager
        )

        self.assertEqual(
            new_status[SM.LAST_STATE_CHANGE], timestamp
        )

    def test_last_statechange_no_state(self):
        """Check calculus of the last_state_change.
        """

        timestamp = time()
        state = rand()
        status = {SM.VALUE: OFF}
        new_status = update_status(
            state=state, status=status, timestamp=timestamp,
            statusmanager=self.statusmanager
        )

        self.assertEqual(
            new_status[SM.LAST_STATE_CHANGE], timestamp
        )

    def test_nolast_statechange(self):
        """Check calculus of the last_state_change.
        """

        timestamp = time()
        state = rand()
        status = {
            SM.STATE: state,
            SM.LAST_STATE_CHANGE: 0,
            SM.VALUE: OFF
        }
        new_status = update_status(
            state=state, status=status, timestamp=timestamp,
            statusmanager=self.statusmanager
        )

        self.assertEqual(
            new_status[SM.LAST_STATE_CHANGE], 0
        )


class ProcessStatusCanceledTestCase(TestCase):
    """Test the process_status_canceled function.
    """

    def setUp(self):

        super(ProcessStatusCanceledTestCase, self).setUp()

        self.status = {'test': None}

    def test_off(self):
        """Test with the off status.
        """

        status = process_status_canceled(state=0, status=self.status.copy())

        self.status[SM.VALUE] = OFF

        self.assertEqual(status, self.status)

    def test_ongoing(self):
        """Test with an ongoing status.
        """

        status = process_status_canceled(
            state=randint(1, 1000), status=self.status.copy()
        )

        self.status[SM.VALUE] = ONGOING

        self.assertEqual(status, self.status)


class _ProcessStatusOffTestCase(object):
    """Test the process_status_off function.
    """

    def test_off(self):
        """Test with the off status.
        """

        process_status_off(
            status=status, statusmanager=self.statusmanager, state=0,
            timestamp=0
        )

        self.assertEqual(status, {SM.VALUE: OFF})

    def test_ongoing(self):
        """Test with an ongoing status.
        """

        timestamp = time()
        status = {}

        new_status = process_status_off(
            status=status,
            statusmanager=self.statusmanager, timestamp=timestamp, state=1
        )

        self.assertEqual(
            new_status, {SM.VALUE: ONGOING, SM.STATE: 1}
        )


class ProcessStatusOngoingTestCase(object):

    def test_off(self):
        """Test off status after both flapping and stealhy times.
        """

        timestamp = time()
        status = {
            SM.VALUE: ONGOING,
            SM.TIMESTAMP: timestamp,
            SM.PENDING_TIME: 0
        }
        new_status = process_status_ongoing(
            statusmanager=self.statusmanager, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[SM.VALUE], OFF)

    def test_ongoing(self):
        """Test ongoing status after both flapping and stealhy times.
        """

        timestamp = time()
        status = {
            SM.VALUE: ONGOING,
            SM.TIMESTAMP: timestamp,
            SM.PENDING_TIME: 0
        }
        new_status = process_status_ongoing(
            state=1,
            statusmanager=self.statusmanager, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[SM.VALUE], ONGOING)

    def test_stealthy(self):
        """Test stealthy status.
        """

        timestamp = time()
        status = {
            SM.VALUE: ONGOING,
            SM.TIMESTAMP: timestamp
        }
        new_status = process_status_ongoing(
            statusmanager=self.statusmanager, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[SM.VALUE], STEALTHY)

    def test_stealthy_with_pending_time(self):
        """Test stealthy status.
        """

        timestamp = time()
        status = {
            SM.VALUE: ONGOING,
            SM.TIMESTAMP: timestamp,
            SM.PENDING_TIME: timestamp
        }
        new_status = process_status_ongoing(
            statusmanager=self.statusmanager, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[SM.VALUE], STEALTHY)

    def test_flapping(self):
        """Test flapping status.
        """

        timestamp = time()
        status = {
            SM.VALUE: ONGOING,
            SM.TIMESTAMP: timestamp,
            SM.FLAPPING_FREQ: self.statusmanager.flapping_freq,
            SM.PENDING_TIME: timestamp - self.statusmanager.stealthy_time - 1
        }
        new_status = process_status_ongoing(
            statusmanager=self.statusmanager, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[SM.VALUE], FLAPPING)
        self.assertEqual(
            new_status[SM.FLAPPING_FREQ], self.statusmanager.flapping_freq + 1
        )

    def test_incflapping(self):
        """Test increment counter of flapping status.
        """

        timestamp = time()
        status = {
            SM.VALUE: ONGOING,
            SM.TIMESTAMP: timestamp,
            SM.FLAPPING_FREQ: self.statusmanager.flapping_freq - 2,
            SM.PENDING_TIME: timestamp - self.statusmanager.stealthy_time - 1
        }
        new_status = process_status_ongoing(
            statusmanager=self.statusmanager, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[SM.VALUE], OFF)
        self.assertEqual(
            new_status[SM.FLAPPING_FREQ], self.statusmanager.flapping_freq - 1
        )

    def test_noflapping_overtime(self):
        """Test to leave flapping cause expired flapping time.
        """

        timestamp = time()
        status = {
            SM.VALUE: ONGOING,
            SM.TIMESTAMP: timestamp,
            SM.FLAPPING_FREQ: self.statusmanager.flapping_freq,
            SM.PENDING_TIME: timestamp - self.statusmanager.flapping_time - 1
        }
        new_status = process_status_ongoing(
            statusmanager=self.statusmanager, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[SM.VALUE], OFF)
        self.assertEqual(
            new_status[SM.FLAPPING_FREQ], self.statusmanager.flapping_freq
        )

    def test_noflapping_ongoing(self):
        """Test to leave flapping in an ongoing status.
        """

        timestamp = time()
        status = {
            SM.VALUE: ONGOING,
            SM.TIMESTAMP: timestamp,
            SM.FLAPPING_FREQ: self.statusmanager.flapping_freq,
            SM.PENDING_TIME: timestamp - self.statusmanager.flapping_time - 1
        }
        new_status = process_status_ongoing(
            state=1,
            statusmanager=self.statusmanager, status=status,
            timestamp=timestamp
        )

        self.assertEqual(new_status[SM.VALUE], ONGOING)


class TestProcessStealthyStatus(TestProcessStatus):
    """Test the function process_status_stealthy.
    """


class TestProcessStatusFlapping(object):
    """Test the process_status_flapping function.
    """

    def setUp(self):

        super(TestProcessStatusFlapping, self).setUp()

        self.flapping_times = []
        self.status = {
            SM.STATE: 0,
            SM.VALUE: FLAPPING,
            SM.FLAPPING_TIMES: self.flapping_times
        }

    def test_flapping_to_off(self):
        """Test changing of status from flapping to off.
        """

        process_status_flapping(
            status=self.status, statusmanager=self.statusmanager, timestamp=0, state=0
        )

        self.assertEqual(self.status[SM.VALUE], 0)
        self.assertEqual(self.flapping_times, [0])

    def test_stillflapping(self):
        """Test with old flapping status.
        """

        timestamp = time()
        status = {
            SM.FLAPPING_FREQ: 1,
            SM.PENDING_TIME: timestamp + self.statusmanager.flapping_time - 1,
            SM.STATE: 0,
            SM.VALUE: FLAPPING
        }
        newstatus = process_status_flapping(
            state=1,
            timestamp=timestamp, status=status, statusmanager=self.statusmanager
        )

        self.assertEqual(newstatus[SM.VALUE], FLAPPING)

    def test_noflapping_off(self):
        """Test end of flapping with OFF status.
        """

        timestamp = time()
        status = {
            SM.FLAPPING_FREQ: 1,
            SM.PENDING_TIME: timestamp + self.statusmanager.flapping_time - 1,
            SM.STATE: 0,
            SM.VALUE: FLAPPING
        }
        newstatus = process_status_flapping(
            state=0,
            timestamp=timestamp, status=status, statusmanager=self.statusmanager
        )

        self.assertEqual(newstatus[SM.VALUE], OFF)

    def test_noflapping_ongoing(self):
        """Test end of flapping with OFF status.
        """

        timestamp = time()
        status = {
            SM.FLAPPING_FREQ: 1,
            SM.PENDING_TIME: timestamp + self.statusmanager.flapping_time - 1,
            SM.STATE: 1,
            SM.VALUE: FLAPPING
        }
        newstatus = process_status_flapping(
            state=1,
            timestamp=timestamp, status=status, statusmanager=self.statusmanager
        )

        self.assertEqual(newstatus[SM.VALUE], ONGOING)


if __name__ == '__main__':
    main()
