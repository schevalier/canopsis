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

from canopsis.timeserie.timewindow import Period

from canopsis.configuration.configurable.decorator import (
    conf_paths, add_category
)

CONF_RESOURCE = 'storage/periodic.conf'  #: last storage resource.
CATEGORY = 'PERIODIC'  #: storage category.


@conf_paths(CONF_RESOURCE)
@add_category(CATEGORY)
class PeriodicStorage(Storage):
    """Storage dedicated to manage periodic data.

    A periodic data is ponctual but it might be helpful to indicate a period
    related to new data value storing. In such case, all methods use a local
    period. If not given, the storage period is used.
    """

    __datatype__ = 'periodic'  #: storage data type.

    TIMESTAMP = 'timestamp'  #: data timestamp.
    VALUES = 'values'  #: data values.
    PERIOD = 'period'  #: data value period.
    LAST_UPDATE = 'last_update'  #: data value last_update

    DEFAULT_PERIOD = Period(minute=5)  #: default storage period.

    def __init__(self, period=None, *args, **kwargs):

        super(PeriodicStorage, self).__init__(*args, **kwargs)

        if period is None:
            self.period = PeriodicStorage.DEFAULT_PERIOD

        else:
            self.period = period.copy()

    def count(self, data_id, period=None, timewindow=None):
        """Get number of periodic documents for input data_id.

        :param str data_id: related data_id.
        :param Period period: period to use. Default is this period.
        :param TimeWindow timewindow: timewindow which contains points.
        :rtype: int
        """

        raise NotImplementedError()

    def size(
            self, data_id=None, period=None, timewindow=None, *args, **kwargs
    ):
        """Get size occupied by research filter data_id.

        :param str data_id: related data_id.
        :param Period period: period to use. Default is this period.
        :param TimeWindow timewindow: timewindow which contains points.
        :rtype: int
        """

        raise NotImplementedError()

    def get(
            self, data_id, period=None, timewindow=None, _filter=None,
            limit=0, skip=0, sort=None
    ):
        """Get a list of data by timestamp.

        :param str data_id: related data_id.
        :param Period period: period to use. Default is this period.
        :param TimeWindow timewindow: timewindow which contains points.
        :param dict _filter: value filter.
        :param int limit: maximal number of points to retrieve.
        :param int skip: number of points to avoid in the set of iterated
            points.
        :param list sort: list of (data field name, data field value) which
            gives the order of values in the result.

        :rtype: list
        """

        raise NotImplementedError()

    def find(
            self, period=None, timewindow=None, _filter=None,
            limit=0, skip=0, sort=0
    ):

        """Get a list of data by timestamp.

        :param Period period: period to use. Default is this period.
        :param TimeWindow timewindow: timewindow which contains points.
        :param dict _filter: value filter.
        :param int limit: maximal number of points to retrieve.
        :param int skip: number of points to avoid in the set of iterated
            points.
        :param list sort: list of (data field name, data field value) which
            gives the order of values in the result.

        :rtype: list
        """

        raise NotImplementedError()

    def put(self, data_id, data, period=None, cache=False):
        """Put periodic data with related timestamps.

        :param Period period: period to use. Default is this period.
        :param Iterable data: iterable of (timestamp, value).
        :param bool cache: use query cache if True (False by default).
        """

        raise NotImplementedError()

    def remove(
            self, data_id, period=None, timewindow=None, cache=False,
            _filter=None
    ):
        """Remove periodic data related to data_id, timewindow and period.

        :param Period period: period to use. Default is this period.
        :param TimeWindow timewindow: time interval where existing points will
            be deleted. If None (default), remove all data with input period.

        :param bool cache: use query cache if True (False by default).
        """

        raise NotImplementedError()
