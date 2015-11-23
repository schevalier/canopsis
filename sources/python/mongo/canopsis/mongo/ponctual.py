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

QUERY = [(DATA_ID, 1), (TIMESTAMP, -1)]  #: mongo document index


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
            where[TIMESTAMP] = {'$lte': timewindow.stop()}
            where[LAST_TIMESTAMP] = {'$gte': timewindow.start()}

        cursor = self._find(document=where)
        cursor.hint(QUERY)

        result = cursor.count()

        return result

    def _get_documents(self, data_id, start=None, stop=None):

        query = {DATA_ID: data_id}

        if start is not None:  # manage specific timewindow
            query[LAST_TIMESTAMP] = {'$gte': start}

        if stop is not None:
            query[TIMESTAMP] = {'$lte': stop}

        result = self._find(document=query)

        result.cursor(QUERY)

        return result

    def get(
            self, data_id, timewindow=None, limit=None, skip=None,
            *args, **kwargs
    ):

        result = []

        start = None if timewindow is None else timewindow.start()
        stop = None if timewindow is None else timewindow.stop()

        cursor = self._get_documents(data_id=data_id, start=start, stop=stop)

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
                lensubset = len(subset)

                document = {
                    TIMESTAMP: subset[0][0],
                    LAST_TIMESTAMP: subset[-1][0],
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

        # documents to update
        documents = list(self._get_documents(
            data_id=data_id, start=values[0][0], stop=values[-1][0]
        ))

        # add first document if necessary
        old_documents = self._find(
            document={
                '$query': {TIMESTAMP: {'$lte': values[0][0]}},
                '$orderby': {TIMESTAMP: -1}
            }
        )
        old_documents.limit(1)
        for old_document in old_documents:
            if (
                old_document[LAST_TIMESTAMP] <= values[0][0]
                and old_document[COUNT] < self.maxcount
            ):

                documents.insert(0, old_document)

        for document in documents:

            if not values:  # stop as soon as values is empty
                break

            self._migrate(document)

            dvalues = document[VALUES][0: document[COUNT]]

            dvalues += values

            dvalues.sort(key=itemgetter(0))

            values = dvalues[self.maxcount:]
            dvalues = dvalues[: self.maxcount]

            document[VALUES] = dvalues
            document[COUNT] = len(dvalues)
            document[TIMESTAMP] = dvalues[0][0]
            document[LAST_TIMESTAMP] = dvalues[-1][0]

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

        if timewindow is not None:

            values = self.get(data_id=data_id, timewindow=timewindow)

            # get documents to update
            documents = self._get_documents(
                data_id=data_id,
                start=timewindow.start(),
                stop=timewindow.stop()
            )

            # add first document if necessary
            old_documents = self._find(
                document={
                    '$query': {TIMESTAMP: {'$lte': values[0][0]}},
                    '$orderby': {TIMESTAMP: -1}
                }
            )
            old_documents.limit(1)
            for old_document in old_documents:
                if (
                    old_document[LAST_TIMESTAMP] <= values[0][0]
                    and old_document[COUNT] < self.maxcount
                ):

                    documents.insert(0, old_document)

            for document in documents:

                if not values:
                    document[VALUES] = []

                else:
                    dvalues = values[0: self.maxcount]
                    lendvalues = len(dvalues)
                    values = values[self.maxcount:]

                    document[VALUES] = dvalues
                    document[TIMESTAMP] = dvalues[0][0]
                    document[LAST_TIMESTAMP] = dvalues[-1][0]
                    document[COUNT] = lendvalues

                    if lendvalues < self.maxcount:
                        dvalues += list(
                            (0., 0.) for _ in range(self.maxcount - lendvalues)
                        )

            ids_to_remove = []

            for document in documents:
                _id = document[MongoStorage.ID]
                if document[VALUES]:
                    self._update(
                        spec=_id,
                        document={'$set': {VALUES: document[VALUES]}},
                        cache=cache
                    )
                else:
                    ids_to_remove.append(_id)

            if ids_to_remove:
                self._remove(
                    document={MongoStorage.ID: {'$in': ids_to_remove}},
                    cache=cache
                )

        else:
            self._remove(document={DATA_ID: data_id}, cache=cache)

    def all_indexes(self, *args, **kwargs):

        result = super(MongoPonctualStorage, self).all_indexes(*args, **kwargs)

        result.append(QUERY)

        return result
