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

from canopsis.common.utils import isiterable
from canopsis.common.init import basestring
from canopsis.mongo.core import MongoStorage
from canopsis.storage.timed import TimedStorage
from canopsis.timeserie.timewindow import get_offset_timewindow


class MongoTimedStorage(MongoStorage, TimedStorage):

    class Key:
        """Index key names."""

        DATA_ID = 'd'  #: data id index name.
        VALUE = 'v'  #: value index name.
        TIMESTAMP = 't'  #: timestamp index name.

    TIMESTAMP_BY_ID = [  #: timestamp by data_id.
        (Key.DATA_ID, MongoStorage.ASC), (Key.TIMESTAMP, MongoStorage.DESC)
    ]
    TIMESTAMPS = [  #: timestamps index in case of data_ids is not given.
        (Key.TIMESTAMP, MongoStorage.DESC)
    ]

    def _search(
        self, data_ids=None, timewindow=None, _filter=None,
        limit=0, skip=0, sort=None,
        *args, **kwargs
    ):
        """Process internal search query in returning a cursor."""

        result = None

        # set a where clause for the search
        where = {}

        if _filter is not None:  # add value filtering
            if isinstance(_filter, dict):
                for name in _filter:
                    vname = '{0}.{1}'.format(MongoTimedStorage.Key.VALUE, name)
                    where[vname] = _filter[name]

            else:
                where[MongoTimedStorage.Key.VALUE] = _filter

        if data_ids is not None:
            if isiterable(data_ids, is_str=False):
                where[MongoTimedStorage.Key.DATA_ID] = {'$in': data_ids}

            else:
                where[MongoTimedStorage.Key.DATA_ID] = data_ids

        # if timewindow is not None, get latest timestamp before
        # timewindow.stop()
        if timewindow is not None:
            timestamp = timewindow.stop()
            where[MongoTimedStorage.Key.TIMESTAMP] = {'$lte': timestamp}

        # do the query
        result = self._find(document=where)

        # if timewindow is None or contains only one point, get only last
        # document respectively before now or before the one point
        if limit:
            result.limit(limit)

        if skip:
            result.skip(skip)

        if sort is not None:
            sort = TimedStorage._resolve_sort(sort)
            result.sort(sort)

        # apply a specific index
        if data_ids is None:
            index = MongoTimedStorage.TIMESTAMPS

        else:
            index = MongoTimedStorage.TIMESTAMP_BY_ID

        result.hint(index)

        return result

    def _cursor2periods(self, cursor, timewindow):
        """Transform a cursor to period data.

        :return: dictionary of {
            data_id: list of {
                    TimedStorage.TIMESTAMP: timestamp,
                    TimedStorage.VALUE: value
                }
            }
        :rtype: dict
        """

        result = {}

        # iterate on all documents
        for document in cursor:
            timestamp = document[MongoTimedStorage.Key.TIMESTAMP]
            value = document[MongoTimedStorage.Key.VALUE]
            data_id = document[MongoTimedStorage.Key.DATA_ID]

            # a value to get is composed of a timestamp, values and document id
            value_to_append = {
                TimedStorage.TIMESTAMP: timestamp,
                TimedStorage.VALUE: value
            }

            if data_id not in result:
                result[data_id] = [value_to_append]

            else:
                result[data_id].append(value_to_append)

            if timewindow is not None and timestamp not in timewindow:
                # stop when a document is just before the start timewindow
                break

        return result

    def get(
            self, data_ids, timewindow=None, _filter=None,
            limit=0, skip=0, sort=None,
            *args, **kwargs
    ):

        cursor = self._search(
            data_ids=data_ids, timewindow=timewindow, _filter=_filter,
            limit=limit, skip=skip, sort=sort
        )

        result = self._cursor2periods(cursor=cursor, timewindow=timewindow)

        # if one element has been requested, returns it
        if isinstance(data_ids, basestring):
            result = result[data_ids] if result else None

        return result

    def find(self, timewindow=None, _filter=None, *args, **kwargs):

        cursor = self._search(timewindow=timewindow, _filter=_filter)

        result = self._cursor2periods(cursor=cursor, timewindow=timewindow)

        return result

    def count(self, data_ids, timewindow=None, _filter=None, *args, **kwargs):

        cursor = self._search(
            data_ids=data_ids, timewindow=timewindow, _filter=_filter
        )

        result = cursor.count()

        return result

    def put(self, data_id, value, timestamp, cache=False, *args, **kwargs):

        timewindow = get_offset_timewindow(offset=timestamp)

        data = self.get(
            data_ids=data_id, timewindow=timewindow, limit=1
        )

        data_value = None

        if data:
            data = data[0]
            data_value = data[TimedStorage.VALUE]

        if value != data_value:  # new entry to insert

            document = {
                MongoTimedStorage.Key.DATA_ID: data_id,
                MongoTimedStorage.Key.TIMESTAMP: timestamp,
                MongoTimedStorage.Key.VALUE: value
            }

            if data and data[TimedStorage.TIMESTAMP] == timestamp:
                spec = {
                    MongoTimedStorage.Key.DATA_ID: data_id,
                    MongoTimedStorage.Key.TIMESTAMP: timestamp
                }

                self._update(
                    spec=spec,
                    document=document,
                    cache=cache,
                    multi=False,
                    upsert=False
                )

            else:
                self._insert(document=document, cache=cache)

    def remove(self, data_ids, timewindow=None, cache=False, *args, **kwargs):

        where = {}

        if isiterable(data_ids, is_str=False):
            where[MongoTimedStorage.Key.DATA_ID] = {'$in': data_ids}
        else:
            where[MongoTimedStorage.Key.DATA_ID] = data_ids

        if timewindow is not None:
            where[MongoTimedStorage.Key.TIMESTAMP] = {
                '$gte': timewindow.start(), '$lte': timewindow.stop()
            }

        self._remove(document=where, cache=cache)

    def all_indexes(self, *args, **kwargs):

        result = super(MongoTimedStorage, self).all_indexes(*args, **kwargs)

        result += [
            MongoTimedStorage.TIMESTAMP_BY_ID, MongoTimedStorage.TIMESTAMPS
        ]

        return result
