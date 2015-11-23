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
from canopsis.mongo.core import MongoStorage
from canopsis.storage.periodical import PeriodicalStorage
from canopsis.timeserie.timewindow import get_offset_timewindow


DATA_ID = 'd'  #: data id field name.
VALUE = 'v'  #: values field name.
TIMESTAMP = 't'  #: minimal value timestamp field name


class MongoPeriodicalStorage(MongoStorage, PeriodicalStorage):
    """Mongo implementation of the periodic storage."""

    TIMESTAMP_BY_ID = \
        [
            (DATA_ID, MongoStorage.ASC),
            (TIMESTAMP, MongoStorage.DESC)
        ]

    def get(
            self, data_ids, timewindow=None, limit=0, skip=0, sort=None,
            *args, **kwargs
    ):

        result = {}

        # set a where clause for the search
        where = {}

        one_element = False

        if isiterable(data_ids, is_str=False):
            where[DATA_ID] = {'$in': data_ids}

        else:
            where[DATA_ID] = data_ids
            one_element = True

        # if timewindow is not None, get latest timestamp before
        # timewindow.stop()
        if timewindow is not None:
            timestamp = timewindow.stop()
            where[TIMESTAMP] = {
                '$lte': timewindow.stop()
            }

        # do the query
        cursor = self._find(document=where)

        # if timewindow is None or contains only one point, get only last
        # document respectively before now or before the one point
        if limit:
            cursor.limit(limit)

        if skip:
            cursor.skip(skip)

        if sort is not None:
            sort = MongoStorage._resolve_sort(sort)
            cursor.sort(sort)

        # apply a specific index
        cursor.hint(MongoPeriodicalStorage.TIMESTAMP_BY_ID)

        # iterate on all documents
        for document in cursor:

            timestamp = document[TIMESTAMP]
            value = document[VALUE]
            data_id = document[DATA_ID]

            # a value to get is composed of a timestamp, values and document id
            value_to_append = {
                PeriodicalStorage.TIMESTAMP: timestamp,
                PeriodicalStorage.VALUE: value,
                PeriodicalStorage.DATA_ID: data_id
            }

            if data_id not in result:
                result[data_id] = [value_to_append]

            else:
                result[data_id].append(value_to_append)

            if timewindow is not None and timestamp not in timewindow:
                # stop when a document is just before the start timewindow
                break

        # if one element has been requested, returns it
        if one_element and result:
            result = result[data_ids]

        return result

    def count(self, data_id, *args, **kwargs):

        query = {
            DATA_ID: data_id
        }

        cursor = self._find(document=query)
        cursor.hint(MongoPeriodicalStorage.TIMESTAMP_BY_ID)
        result = cursor.count()

        return result

    def put(self, data_id, value, timestamp, cache=False, *args, **kwargs):

        timewindow = get_offset_timewindow(offset=timestamp)

        data = self.get(
            data_ids=[data_id], timewindow=timewindow, limit=1)

        data_value = None

        if data:
            data_value = data[data_id][0][PeriodicalStorage.VALUE]

        if value != data_value:  # new entry to insert

            values_to_insert = {
                DATA_ID: data_id,
                TIMESTAMP: timestamp,
                VALUE: value
            }
            self._insert(document=values_to_insert, cache=cache)

    def remove(self, data_ids, timewindow=None, cache=False, *args, **kwargs):

        where = {}

        if isiterable(data_ids, is_str=False):
            where[DATA_ID] = {'$in': data_ids}
        else:
            where[DATA_ID] = data_ids

        if timewindow is not None:
            where[TIMESTAMP] = {
                '$gte': timewindow.start(), '$lte': timewindow.stop()
            }

        self._remove(document=where, cache=cache)

    def all_indexes(self, *args, **kwargs):

        result = super(MongoPeriodicalStorage, self).all_indexes(*args, **kwargs)

        result.append(MongoPeriodicalStorage.TIMESTAMP_BY_ID)

        return result
