# -*- coding: utf-8 -*-
# --------------------------------
# Copyright (c) 2014 "Capensis" [http://www.capensis.com]
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

from canopsis.configuration.configurable.decorator import (
    conf_paths, add_category)
from canopsis.middleware.registry import MiddlewareRegistry
from canopsis.storage import Storage
from canopsis.common.utils import isiterable
from uuid import uuid4 as uuid

CONF_RESOURCE = 'context/context.conf'  #: last context conf resource
CATEGORY = 'CONTEXT'  #: Context category


@add_category(CATEGORY)
@conf_paths(CONF_RESOURCE)
class Context(MiddlewareRegistry):
    """
    Manage access to a ctx (connector, component, resource) elements
    and ctx data (metric, downtime, etc.)

    It uses a composite storage in order to modelise composite data.

    For example, let a resource ``R`` in the component ``C`` and connector
    ``K`` is identified through the ctx [``K``, ``C``], the name ``R`` and
    the type ``resource``.

    In addition to those composable data, it is possible to extend two entities
    which have the same name and type but different ctx.

    For example, in following entities:
        - component: name is component_id and type is component
        - connector: name is connector and type is connector
    """

    DATA_SCOPE = 'ctx'  #: default data scope

    CTX_STORAGE = 'ctx_storage'  #: ctx storage name
    CONTEXT = 'ctx'

    TYPE = 'type'  #: entity type field name
    PARENT_ID = 'pid'  #: entity parent id
    ID = Storage.DATA_ID  #: entity id field name
    NAME = 'name'  #: entity name field name
    EXTENDED = 'extended'  #: extended field name

    # an entity is unique by a type, a parent id and a name
    DEFAULT_CONTEXT = [TYPE, NAME, PARENT_ID]

    ENTITY_TYPES_LIST = [
        ('connector', 'connector_name', 'component', 'resource'),
        ('topology', 'topology_node')]

    def __init__(
        self, ctx=DEFAULT_CONTEXT, ctx_storage=None, *args, **kwargs
    ):

        super(Context, self).__init__(self, *args, **kwargs)

        self._context = ctx
        if ctx_storage is not None:
            self[Context.CTX_STORAGE] = ctx_storage

    @property
    def ctx(self):
        """
        List of ctx element name.
        """
        return self._context

    @ctx.setter
    def ctx(self, value):
        self._context = value

    def get_entities(self, ids):
        """
        Get entities by id

        :param ids: one id or a set of ids
        """

        return self[Context.CTX_STORAGE].get_elements(ids=ids)

    def get_entity_from_evt(self, event, from_db=False, create=True):
        """
        Get event entity.

        :param bool from_base: If True (False by default), check return entity
            from base, otherwise, return entity information from the event.
        :param bool create: Create the event entity if it does not exists
            (True by default).
        :return: event entity or None if not entity exists
        :rtype: dict
        """

        result = None

        ctx = self.get_ctx_from_event(event)

        entities = self.get_entities_from_ctx(ctx=ctx, create=create)

        if entities:
            result = entities[-1]

        return result

    def get_entities_from_ctx(self, ctx=None, create=True):
        """
        Get a chain of entities related to a ctx.

        :param str _type: entity type
        :param str name: entity name
        :param dict ctx: set of (entity type, entity name) such as result
            parents
        :param bool create: create entities if they do not exist
        :return: list of found entities
        :rtype: list
        """

        result = []

        # initialize entity and parent_id
        parent_id = None

        # among entity types list
        for entity_types in Context.ENTITY_TYPES_LIST:

            # iterate on entity type from entity types list
            for entity_type in entity_types:

                # if entity_type is in ctx
                if entity_type in ctx:

                    # get name
                    name = ctx[entity_type]

                    # get the right entity
                    entities = self.find(
                        types=entity_type,
                        names=name,
                        parent_ids=parent_id
                    )

                    entity = entities[0] if entities else None

                    # if an entity has not been found
                    if entity is None:
                        if create:  # create it if necessary
                            entity = self.put(
                                _type=entity_type,
                                parent_id=parent_id,
                                name=name
                            )

                        else:  # or break the loop
                            break

                    # append entity to the result
                    result.append(entity)
                    # parent_id equals entity id
                    parent_id = entity[Context.ID]

                else:
                    break

            # if an entity has been found
            if result:
                # exit the loop
                break

        return result

    def get(
        self, ids, types=None, names=None, parent_ids=None, extended=False
    ):
        """
        Get entities by type, parent id and names

        :param str _type: entity type (connector, component, etc.)

        :param str names: entity names

        :param str parent_id: parent entit id

        :param dict ctx: entity ctx such as couples of name, value.

        :param bool extended: get extended entities if entity is shared.

        :return: one element, list of elements if entity is shared or None
        :rtype: dict, list or None
        """

        _filter = Context._prepare_filter(
            ids=ids, types=types, names=names, parent_ids=parent_ids)

        result = self[Context.CTX_STORAGE].get(
            path=_filter, data_ids=ids, shared=extended)

        return result

    def find(
        self,
        ids=None, types=None, parent_ids=None, names=None, ctx=None,
        _filter=None, extended=False,
        limit=0, skip=0, sort=None, with_count=False
    ):
        """
        Find all entities which of input _type and ctx with an additional
        filter.

        :param extended: get extended entities if they are shared
        """

        result = None

        path = {}

        if ctx is not None:
            entities = self.get_entities_from_ctx(ctx=ctx)
            if entities:
                path = entities[-1]

        query = Context._prepare_filter(
            ids=ids, types=types, parent_ids=parent_ids, names=names)

        if _filter is not None:
            query.update(_filter)

        result = self[Context.CTX_STORAGE].get(
            path=path, _filter=query, shared=extended,
            limit=limit, skip=skip, sort=sort)

        return result

    def put(
        self,
        _type, name, entity=None, parent_id=None, _id=None, extended_id=None
    ):
        """
        Put an element designated by the element_id, element_type and element.

        :return: entity
        """

        _id = str(uuid()) if _id is None else _id

        # fill path
        path = {
            Context.NAME: name,
            Context.TYPE: _type
        }
        if parent_id is not None:
            path[Context.PARENT_ID] = parent_id

        # fill data
        data = {
            Context.NAME: name
        }
        if entity is not None:
            data.update(entity)

        self[Context.CTX_STORAGE].put(
            path=path, data_id=_id, data=data, shared_id=extended_id)

        result = {
            Context.ID: _id
        }
        result.update(path)
        result.update(data)

        return result

    def remove(
        self,
        ids=None, types=None, parent_ids=None, names=None, ctx=None,
        extended=False
    ):
        """
        Remove a set of elements identified by element_ids, an element type or
        a timewindow
        """

        # start to remove entities from the ctx if necessary
        if ctx is not None:
            # get all entities
            entities = self.get_entities_from_ctx(
                ctx=ctx, create=False)
            # remove entities
            for entity in entities:
                self.remove(
                    ids=entity[Context.ID],
                    types=entity[Context.TYPE],
                    parent_ids=entity[Context.PARENT_ID],
                    names=entity[Context.NAMES]
                )

        # create a filter
        path = Context._prepare_filter(
            ids=ids, types=types, parent_ids=parent_ids, names=names)

        if path:
            self[Context.CTX_STORAGE].remove(path=path, shared=extended)

    def get_entity_context_and_name(self, entity):
        """
        Get the right ctx related to input entity
        """

        result = self[Context.CTX_STORAGE].get_path_with_id(entity)

        return result

    def get_entity_id(self, entity):
        """
        Get unique entity id related to its ctx and name.
        """

        path, data_id = self.get_entity_context_and_name(entity=entity)

        result = self[Context.CTX_STORAGE].get_absolute_path(
            path=path, data_id=data_id)

        return result

    def unify_entities(self, entities, extended=False):
        """
        Unify input entities as the same entity
        """

        self[Context.CTX_STORAGE].share_data(data=entities, shared=extended)

    def _configure(self, unified_conf, *args, **kwargs):

        super(Context, self)._configure(
            unified_conf=unified_conf, *args, **kwargs)

        if Context.CTX_STORAGE in self:
            self[Context.CTX_STORAGE].path = self.ctx

    @staticmethod
    def get_ctx_from_event(event):
        """
        Get a ctx object from an event.

        :param dict event: contains pairs of entity (type, name)
        """

        result = {}

        entity_types = Context.ENTITY_TYPES_LIST[0]

        # iterate on entity types
        for entity_type in entity_types:
            # and push event value
            if entity_type in event:
                result[entity_type] = event[entity_type]
            else:  # or break the loop
                break

        return result

    @staticmethod
    def get_ctx_from_rk(rk):
        """
        Get a ctx object from an rk.

        :param str rk: may respect the form '/key0/key1/.../keyn' where
            key0, key1, ..., keyn are entity names which have to respect
            Context.ENTITY_TYPES_LIST values.
        :return: set of pairs (entity type, entity name) related to rk and
            first type tree.
        :rtype: dict
        """

        # result is an empty dict
        result = {}

        # split entity_names
        entity_names = rk.split('/')[1:]

        entity_types = Context.ENTITY_TYPES_LIST[0]

        # calculate the minimal length
        min_length = min(len(entity_names), len(entity_types))

        # result contains all pairs of entity types and names
        result = {
            entity_types[index]: entity_names[index]
            for index in range(min_length)
        }

        return result

    @staticmethod
    def _prepare_filter(ids=None, types=None, parent_ids=None, names=None):
        """
        Prepare a filter related to ids, types, parent_ids and a ctx.
        """

        result = {}

        if ids is not None:
            if isiterable(ids, is_str=False):
                result[Context.ID] = {'$in': ids}
            else:
                result[Context.ID] = ids

        if types is not None:
            if isiterable(types, is_str=False):
                result[Context.TYPE] = {'$in': types}
            else:
                result[Context.TYPE] = types

        if parent_ids is not None:
            if isiterable(parent_ids, is_str=False):
                result[Context.PARENT_ID] = {'$in': parent_ids}
            else:
                result[Context.PARENT_ID] = parent_ids

        if names is not None:
            if isiterable(names, is_str=False):
                result[Context.NAME] = {'$in': names}
            else:
                result[Context.NAME] = names

        return result
