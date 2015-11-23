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

from canopsis.mongo.core import MongoStorage
from canopsis.storage.ponctual import PonctualStorage
from canopsis.timeserie.timewindow import TimeWindow

from operator import itemgetter


DATA_ID = 'i'  #: data id field name.
TIMESTAMP = 't'  #: minimal timestamp field name.
VALUES = 'v'  #: values field name.
LAST_TIMESTAMP = 'l'  #: last update timestamp field name
COUNT = 'c'  #: number of values per document

QUERY = [(DATA_ID, 1), (TIMESTAMP, 1)]  #: mongo document index


class MongoPonctualStorage(MongoStorage, PonctualStorage):
    """MongoStorage dedicated to manage ponctual data."""

    DEFAULT_MAXCOUNT = 500  #: default max count of value per document.

    def __init__(self, maxcount=DEFAULT_MAXCOUNT, *args, **kwargs):
        """
        :param int maxcount: maximum number of values per document.
        """

        super(MongoPonctualStorage, self).__init__(*args, **kwargs)

        self.maxcount = maxcount

    def _migrate(self, document):
        """Migrate input document to the new data model format."""

        values = document[VALUES]

        if isinstance(values, dict):

            values = list([vts, values[vts]] for vts in values)
            values.sort(key=lambda item: item[0])

            # set number of items
            document[COUNT] = len(values)

            del document['p']  # remove the period

            # fill values with empty values.
            for _ in range(self.maxcount - len(values)):
                values.append([None, None])

            document[VALUES] = values

    def count(self, data_id, period, timewindow=None, *args, **kwargs):

        data = self.get(data_id=data_id, timewindow=timewindow, period=period)

        result = len(data)

        return result

    def size(self, data_id=None, timewindow=None, *args, **kwargs):

        where = {DATA_ID: data_id}

        if timewindow is not None:
            where[TIMESTAMP] = {
                '$gte': timewindow.start(),
                '$lte': timewindow.stop()
            }

        cursor = self._find(document=where)
        cursor.hint(QUERY)

        result = cursor.count()

        return result

    def get(
            self, data_id, timewindow=None, limit=None, skip=None,
            *args, **kwargs
    ):

        query = self._get_documents_query(
            data_id=data_id,
            timewindow=timewindow
        )

        projection = {
            TIMESTAMP: 1,
            VALUES: 1
        }

        cursor = self._find(document=query, projection=projection)

        cursor.hint(QUERY)

        result = []

        if limit != 0:
            cursor = cursor[:limit]

        for document in cursor:

            self._migrate(document=document)  # migrate to new date model

            values = document[VALUES]

            for vts, value in values:

                if vts is not None and (
                        timewindow is None or vts in timewindow
                ):
                    result.append((vts, value))

        result.sort(key=itemgetter(0))  # sort a last time

        # apply limit and skip
        result = result[
            0 if skip is None else skip:
            len(result) if limit is None else limit
        ]

        return result

    def _new_documents(self, data_id, values):
        """Get new documents related to input values.

        :param str data_id: data identifier.
        :param list values: values to put in documents.
        :rtype: list
        """

        result = []

        subsets = list(
            values[i: self.maxcount] for i in range(len(values) / self.maxcount)
        )

        for subset in subsets:

            if subset:
                timestamp = subset[0][0]
                last_timestamp = subset[-1][0]
                lensubset = len(subset)

                document = {
                    TIMESTAMP: timestamp,
                    LAST_TIMESTAMP: last_timestamp,
                    DATA_ID: data_id,
                    COUNT: lensubset,
                    VALUES: subset
                }

                if len(subset) < self.maxcount:  # add empty values
                    subset += list(
                        [0., 0.] for _ in range(self.maxcount - lensubset)
                    )

                result.append(document)

        return result

    def put(self, data_id, values, cache=False, *args, **kwargs):

        # sort values by timestamp
        values.sort(key=itemgetter(0))

        # get documents
        timewindow = TimeWindow(start=values[0][0], stop=values[-1][0])
        document_query = self._get_documents_query(
            data_id=data_id, timewindow=timewindow
        )
        # documents to update
        documents = list(self._find(document=document_query))

        for document in documents:

            self._migrate(document)

            dvalues = document[VALUES][0: document[COUNT]]

            dvalues += values

            dvalues.sort(key=itemgetter(0))

            values = dvalues[self.maxcount:]
            dvalues = dvalues[: self.maxcount]

            document[VALUES] = dvalues
            document[COUNT] = len(dvalues)

        else:
            if values:  # if values left
                _new_documents = self._new_documents(  # generate new doccuments
                    data_id=data_id, values=values
                )
                documents += _new_documents  # and add them to documents

        for document in documents:  # insert/update documents

            if MongoStorage.ID in document:
                self._insert(document=document, cache=cache)

            else:
                self._update(
                    spec={'_id': document[MongoStorage.ID]},
                    document={'$set': document}, cache=cache
                )

    def remove(self, data_id, timewindow=None, cache=False, *args, **kwargs):

        query = self._get_documents_query(
            data_id=data_id, timewindow=timewindow
        )

        if timewindow is not None:

            projection = {
                TIMESTAMP: 1,
                VALUES: 1
            }

            documents = self._find(document=query, projection=projection)

            for document in documents:
                timestamp = document.get(TIMESTAMP)
                values = document.get(VALUES)
                values_to_save = {
                    t: values[t] for t in values
                    if (timestamp + int(t)) not in timewindow
                }
                _id = document.get('_id')

                if len(values_to_save) > 0:
                    self._update(
                        spec={'_id': _id},
                        document={'$set': {VALUES: values_to_save}},
                        cache=cache
                    )
                else:
                    self._remove(document=_id, cache=cache)

        else:
            self._remove(document=query, cache=cache)

    def all_indexes(self, *args, **kwargs):

        result = super(MongoPonctualStorage, self).all_indexes(*args, **kwargs)

        result.append(QUERY)

        return result

    @staticmethod
    def _get_documents_query(data_id, timewindow):
        """Get mongo documents query about data_id, timewindow."""

        result = {DATA_ID: data_id}

        if timewindow is not None:  # manage specific timewindow

            result[TIMESTAMP] = {'$lte': timewindow.stop()}
            result[LAST_TIMESTAMP] = {'$gte': timewindow.start()}

        return result
