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

"""This module is dedicated to CTXInfoFunder interface.

It aims to execute ctxinfo manager read and delete methods related to its own
information managers such as the perfdata manager for example.
"""

from canopsis.common.init import basestring
from canopsis.ctxinfo.funder import CTXInfoFunder
from canopsis.middleware.core import Middleware


class Funder(Middleware):
    """Funder dedicated to entity events.
    """

    ENTITY_ID = 'entity_id'  #: default entity id field name

    __register__ = True  #: register this class such as a middleware
    __protocol__ = 'funder'  #: protocol registration name if __register__

    def _entity_id_field(self):
        """Get entity id document field name.

        :return: entity id document field name. CTXInfoFunder.ENTITY_ID by
            default.
        :rtype: str
        """

        return CTXInfoFunder.ENTITY_ID

    @staticmethod
    def _entity_ids_unique(entity_ids):
        """Return a couple of (list of entity ids, entity_ids is unique).

        :param entity_ids: entity id(s).
        :type entity_ids: str or list
        :return: a couple of (list of entity ids, entity_ids is unique) where
            unique is True iif entity_ids is a string and, the list of entity
            ids depending on entity_ids type:

        - None: empty list.
        - str: [entity_ids].
        - iterable: entity_ids.
        :rtype: tuple
        """

        unique = isinstance(entity_ids, basestring)

        if unique:
            entity_ids = [entity_ids]

        result = entity_ids, unique

        return result

    def _final_result(self, queryresult, unique):
        """Transform a query result to a final result which is a dictionary of
        document by entity id.

        :param queryresult: query result to transform into a dict of documents
            by entity id.
        :type queryresult: list or dict
        :param bool unique: True if related entity_ids where a string.
        :return: dict of documents by entity id or documents if unique.
        :rtype: dict or list
        """

        # get default entity id field name
        entity_id_field = self._entity_id_field()

        # initialiaze the result with an empty dict
        result = {}

        # ensure queryresult such as a list of documents
        if isinstance(queryresult, dict):
            queryresult = [queryresult]
        elif queryresult is None:
            queryresult = []

        # iterate on query result
        for r in queryresult:
            # get document entity id
            entity_id = r[entity_id_field]
            # get result documents
            documents = result.setdefault(entity_id, [])
            # append a document in result documents
            documents.append(r)

        if unique:  # apply unique rule
            result = iter(result).next() if result else None

        return result

    def get(self, entity_ids=None, query=None, *args, **kwargs):
        """Get entity information related to input ``entity id(s)`` and
        additional specific filter ``query`` per entity id.

        :param entity_ids: entity id(s) from where find information. If None
            (default), get all information of all entities.
        :type entity_ids: str or list
        :param dict query: specific query to apply on the method execution.
        :return: couples of (entity id, [information]).
        :rtype: dict
        """

        entity_ids, unique = self._entity_ids_unique(entity_ids)

        result = self._get(entity_ids=entity_ids, query=query, *args, **kwargs)

        result = self._final_result(result, unique)

        return result

    def _get(self, *args, **kwargs):
        """Protected get method implementation.
        """

        raise NotImplementedError()

    def count(self, entity_ids=None, query=None, *args, **kwargs):
        """Get entity information count related to input ``entity id(s)`` and
        additional specific filter ``query`` per entity id.

        :param entity_ids: entity id(s) from where find information. If None
            (default), get all information of all entities.
        :type entity_ids: str or list
        :param dict query: specific query to apply on the method execution.
        :return: couples of (entity id, count).
        :rtype: dict
        """

        entity_ids, unique = self._entity_ids_unique(entity_ids)

        result = self._count(
            entity_ids=entity_ids, query=query, *args, **kwargs
        )

        result = self._final_result(result, unique)

        return result

    def _count(self, *args, **kwargs):
        """Protected count method implementation.
        """

        raise NotImplementedError()

    def delete(
        self, entity_ids=None, query=None, cache=False, *args, **kwargs
    ):
        """Get entity information count related to input ``entity id(s)`` and
        additional specific filter ``query`` per entity id.

        :param entity_ids: entity id(s) from where find information. If None
            (default), get all information of all entities.
        :type entity_ids: str or list
        :param dict query: specific query to apply on the method execution.
        :param bool cache: storage cache property.
        :return: couples of (entity id, count).
        :rtype: dict
        """

        entity_ids, unique = self._entity_ids_unique(entity_ids)

        result = self._get(
            entity_ids=entity_ids, query=query, cache=cache, *args, **kwargs
        )

        result = self._final_result(result, unique)

        return result

    def _delete(self, *args, **kwargs):
        """Protected delete method implementation.
        """

        raise NotImplementedError()

    def get_entity_ids(self, query=None):
        """Get funder entity id(s) related to input query.

        :param dict query: query to apply on funder documents in order to
            retrieve related entity id. If None, get all funder entity ids.
        :return: list of entity ids.
        :rtype: list
        """

        raise NotImplementedError()
