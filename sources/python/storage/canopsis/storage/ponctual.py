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


class PonctualStorage(Storage):
    """Storage dedicated to manage ponctual data."""

    __datatype__ = 'ponctual'

    TIMESTAMP = 'timestamp'
    VALUES = 'values'
    LAST_UPDATE = 'last_update'

    def count(self, data_id, timewindow=None):
        """Get number of documents for input data_id.

        :param str data_id: data identifier.
        :param TimeWindow timewindow: If timewindow is None, remove all data.
        """

        raise NotImplementedError()

    def size(self, data_id=None, timewindow=None, *args, **kwargs):
        """Get size occupied by research filter data_id.

        :param str data_id: data identifier.
        :param TimeWindow timewindow: If timewindow is None, remove all data.
        """

        raise NotImplementedError()

    def get(self, data_id, timewindow=None, limit=None, skip=None):
        """Get a list of values by timestamp.

        :param str data_id: data identifier.
        :param TimeWindow timewindow: If timewindow is None, get all data.
        :rtype: list"""

        raise NotImplementedError()

    def put(self, data_id, values, cache=False):
        """Put values in collection.

        :param str data_id: data identifier.
        :param list values: data values is an iterable of (timestamp, value).
        :param bool cache: use query cache if True (False by default).
        """

        raise NotImplementedError()

    def remove(self, data_id, timewindow=None, cache=False):
        """Remove data related to data_id and timewindow.

        :param str data_id: data identifier.
        :param TimeWindow timewindow: If timewindow is None, remove all data.

        :param bool cache: use query cache if True (False by default).
        """

        raise NotImplementedError()
