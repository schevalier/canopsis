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


class TimedStorage(Storage):
    """Manage timed data.

    It saves one data value at one timestamp.
    Two consecutives timestamp values can not be same values, last value is
    keeped.
    """

    __datatype__ = 'timed'

    class Index:

        TIMESTAMP = 0
        VALUE = 1
        DATA_ID = 2

    DATA_ID = 'data_id'
    VALUE = 'value'
    TIMESTAMP = 'timestamp'

    def get(
        self, data_ids, timewindow=None, limit=0, skip=0, sort=None
    ):
        """Get a dictionary document data by document id.

        :param data_ids: data id(s) to retrieve.
        :type data_ids: str or list
        :param canopsis.timeserie.timewindow.TimeWindow: request timewindow.
        :param int limit: max number of documents to get.
        :param int skip: documents to skip.
        :param sort: storage sort.
        :type sort: str, tuple, dict or list
        If timewindow is None, result is all timed document.

        :return: timed documents by id with values such as (timestamp, data,
            data_id).
        :rtype: dict of tuple(float, dict, str)
        """

        raise NotImplementedError()

    def count(self, data_id):
        """Get number of timed documents for input data_id.

        :param str data_id: related count data id.
        """

        raise NotImplementedError()

    def put(self, data_id, value, timestamp, cache=False):
        """Put a dictionary of value by name in collection.

        :param str data_id: document data id to put.
        :param value: data value to put at timestamp.
        :param float timestamp: timestamp entry to associate to value and
            data_id.
        :param bool cache: use query cache if True (False by default).
        """

        raise NotImplementedError()

    def remove(self, data_ids, timewindow=None, cache=False):
        """Remove timed_data existing on input timewindow.

        :param data_ids: document data id(s) to remove.
        :type data_ids: str or list
        :param canopsis.timeserie.timewindow.TimeWindow: request timewindow.
        :param bool cache: use query cache if True (False by default).
        """

        raise NotImplementedError()
