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
from canopsis.configuration.model import Parameter

from time import time


CONF_PATH = 'storage/locker.conf'
CATEGORY = 'LOCKER'
CONTENT = [
    Parameter('interval', int)
]


@conf_paths(CONF_PATH)
@add_category(CATEGORY, content=CONTENT)
class Lock(MiddlewareRegistry):
    """Manage locks in database for load balancing."""

    LOCK_STORAGE = 'lock_storage'

    DEFAULT_INTERVAL = 300

    @property
    def interval(self):
        if not hasattr(self, '_interval'):
            self.interval = None

        return self._interval

    @interval.setter
    def interval(self, value):
        if value is None:
            value = Locker.DEFAULT_INTERVAL

        self._interval = value

    def __init__(self, interval=None, lock_storage=None, *args, **kwargs):
        super(Lock, self).__init__(*args, **kwargs)

        if interval is not None:
            self.interval = interval

        if lock_storage is not None:
            self[Locker.LOCK_STORAGE] = lock_storage

    def acquire(self, lid):
        """Try to acquire lock.

        :param str lid: Lock identifier
        :returns: True if the lock was acquired, False otherwise
        """

        l = self[Locker.LOCK_STORAGE].val_compare_and_swap(lid, False, True)

        # Check if old value was False, then the lock was acquired
        return (not l)

    def release(self, lid):
        """Release lock. Does nothing if it wasn't owned by anyone.

        :param str lid: Lock identifier
        """

        if self.own(lid):
            storage = self[Locker.LOCK_STORAGE]

            doc = {
                'value': False,
                't': time()
            }

            storage.update_elements(query=lid, setrule=doc)

    def own(self, lid):
        """Check if lock is owned by someone.

        :param str lid: Lock identifier
        :returns: True if locked, False otherwise
        """

        storage = self[Locker.LOCK_STORAGE]

        l = storage.get_elements(lid)

        now = time()
        last = l.get('t', now)

        if l.get('value', False) and (now - last) < self.interval:
            self.logger.debug(
                'Lock {0} is already owned by someone else'.format(lid)
            )

            return False

        return True


class Locker(object):
    def __init__(self, lid, *args, **kwargs):
        super(Locker, self).__init__(*args, **kwargs)

        self.lid = lid
        self.lock = Lock()

    def __enter__(self, *args, **kwargs):
        self.lock.acquire(self.lid)

        return self.lock

    def __exit__(self, *args, **kwargs):
        self.lock.release(self.lid)
