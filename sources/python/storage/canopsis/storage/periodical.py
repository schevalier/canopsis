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

from canopsis.storage.core import Storage


class PeriodicalStorage(Storage):
    """Store dedicated to manage periodical data.

    It saves one value at one timestamp.
    Two consecutives timestamp values can not be same values.
    """

    __datatype__ = 'periodic'  #: default protocol name.

    class Index:
        """periodical result index name."""

        TIMESTAMP = 0  #: timestamp index value.
        VALUE = 1  #: value index value.
        DATA_ID = 2  #: data_id index value.

    DATA_ID = 'data_id'  #: data_id field name.
    VALUE = 'value'  #: value field name.
    TIMESTAMP = 'timestamp'  #: timestamp field name.

    def get(
        self, data_ids, timewindow=None, limit=0, skip=0, sort=None
    ):
        """Get a dictionary of sorted list of triplet of dictionaries such as :

        dict(
            tuple(
                timestamp,
                dict(data_type, data_value), data id))

        If timewindow is None, result is all timed document.

        :return:
        :rtype: dict of tuple(float, dict, str)
        """

        raise NotImplementedError()

    def count(self, data_id):
        """Get number of periodical documents for input data_id."""

        raise NotImplementedError()

    def put(self, data_id, value, timestamp, cache=False):
        """Put a dictionary of value by name in collection.

        :param bool cache: use query cache if True (False by default).
        """

        raise NotImplementedError()

    def remove(self, data_ids, timewindow=None, cache=False):
        """Remove periodical data existing on input timewindow.

        :param bool cache: use query cache if True (False by default).
        """

        raise NotImplementedError()