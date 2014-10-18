#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------
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

from unittest import TestCase, main
from canopsis.context.manager import Context


class ContextTest(TestCase):

    def setUp(self):
        """
        Create a ctx with data_scope = 'test'
        """

        self.context = Context(data_scope='test')

    def tearDown(self):
        """
        Clean DB when finished
        """
        self.context[Context.CTX_STORAGE].drop()


class GetTest(ContextTest):

    def test_empty(self):
        """
        Get none entities
        """

        entities = self.context.get(ids='')

        self.assertFalse(entities)

    def test_id(self):
        """
        Get one entity from one id
        """

        entity = {
            Context.TYPE: 'connector',
            Context.NAME: 'test'
        }

        entity = self.context.put(
            _type=entity[Context.TYPE], name=entity[Context.NAME])

        _entity = self.context.get(ids=entity[Context.ID])

        self.assertIn(Context.TYPE, _entity)
        self.assertIn(Context.NAME, _entity)

    def test_ids(self):
        """
        Get entities from ids
        """

        count = 20

        for i in range(count):
            entity = {
                Context.TYPE: 'connector',
                Context.NAME: 'test{0}'.format(i)
            }

            self.context.put(
                _type=entity[Context.TYPE], name=entity[Context.NAME],
                _id=str(i))

        entities = self.context.get(ids=[str(i) for i in range(count / 2)])

        self.assertEqual(len(entities), count / 2)

    def test_parent_id(self):
        """
        Get one entity from one parent id
        """

        entity = {
            Context.TYPE: 'connector',
            Context.NAME: 'test',
            Context.PARENT_ID: 'test'
        }

        entity = self.context.put(
            _type=entity[Context.TYPE],
            name=entity[Context.NAME],
            parent_id=entity[Context.PARENT_ID]
        )

        _entity = self.context.get(ids=entity[Context.ID], parent_ids='')

        self.assertIsNone(_entity)

        _entity = self.context.get(ids=entity[Context.ID], parent_ids='test')

        self.assertIsNotNone(_entity)

    def test_parent_ids(self):
        """
        Get entities from parent ids
        """

        count = 20

        for i in range(count):
            entity = {
                Context.TYPE: 'connector',
                Context.NAME: 'test{0}'.format(i),
                Context.PARENT_ID: 'test'
            }

            self.context.put(
                _type=entity[Context.TYPE], name=entity[Context.NAME],
                _id=str(i), parent_id=entity[Context.PARENT_ID])

        entities = self.context.get(
            ids=[str(i) for i in range(count / 2)], parent_ids=[''])

        self.assertFalse(entities)

        entities = self.context.get(
            ids=[str(i) for i in range(count / 2)], parent_ids=['test'])

        self.assertEqual(len(entities), count / 2)

    def test_name(self):
        """
        Get one entity from one parent name
        """

        entity = {
            Context.TYPE: 'connector',
            Context.NAME: 'test'
        }

        entity = self.context.put(
            _type=entity[Context.TYPE],
            name=entity[Context.NAME]
        )

        _entity = self.context.get(ids=entity[Context.ID], names='')

        self.assertIsNone(_entity)

        _entity = self.context.get(
            ids=entity[Context.ID], names=entity[Context.NAME])

        self.assertIsNotNone(_entity)

    def test_names(self):
        """
        Get entities from names
        """

        count = 20

        for i in range(count):
            entity = {
                Context.TYPE: 'connector',
                Context.NAME: 'test',
            }

            self.context.put(
                _type=entity[Context.TYPE], name=entity[Context.NAME],
                _id=str(i))

        entities = self.context.get(
            ids=[str(i) for i in range(count / 2)], names=[''])

        self.assertFalse(entities)

        entities = self.context.get(
            ids=[str(i) for i in range(count / 2)], names=['test'])

        self.assertEqual(len(entities), count / 2)


class EntitiesFromCTX(ContextTest):

    def test_empty(self):
        """
        Test with an empty ctx
        """

        ctx = {}

        entities = self.context.get_entities_from_ctx(ctx=ctx)

        self.assertFalse(entities)

    def test_connector(self):
        """
        Test to add connector
        """

        ctx = {'connector': 'test'}

        entities = self.context.get_entities_from_ctx(ctx=ctx)

        self.assertEqual(len(entities), 1)

        self.assertEqual(entities[0][Context.TYPE], 'connector')
        self.assertEqual(entities[0][Context.NAME], ctx['connector'])

    def test_resource(self):
        """
        Test to add resource
        """

        ctx = {}

        entity_types = self.context.ENTITY_TYPES_LIST[0]

        for entity_type in entity_types:
            ctx[entity_type] = entity_type

        entities = self.context.get_entities_from_ctx(ctx=ctx)

        self.assertEqual(len(entities), len(entity_types))

        for i in range(len(entity_types)):
            entity = entities[i]
            self.assertEqual(entity[Context.TYPE], entity_types[i])
            self.assertEqual(entity[Context.NAME], entity_types[i])
            if i > 0:
                self.assertEqual(
                    entity[Context.PARENT_ID], entities[i - 1][Context.ID])

    def test_over(self):
        """
        Test to add sub element of resource
        """

        ctx = {}

        entity_types = self.context.ENTITY_TYPES_LIST[0]

        for entity_type in entity_types:
            ctx[entity_type] = entity_type

        ctx['test'] = 'test'

        entities = self.context.get_entities_from_ctx(ctx=ctx)

        self.assertEqual(len(entities), len(entity_types))

        for i in range(len(entity_types)):
            entity = entities[i]
            self.assertEqual(entity[Context.TYPE], entity_types[i])
            self.assertEqual(entity[Context.NAME], entity_types[i])
            if i > 0:
                self.assertEqual(
                    entity[Context.PARENT_ID], entities[i - 1][Context.ID])


class CRUDTest(ContextTest):

    def test_ctx_storage(self):

        entity_types = self.context.ENTITY_TYPES_LIST[0]

        count_per_entity_type = 5

        # let's iterate on ctx items in order to create entities
        for entity_type in entity_types:
            ids = [None] * count_per_entity_type
            for i in range(count_per_entity_type):
                name = '{0}{1}'.format(entity_type, i)
                parent_id = ids[i]
                entity = self.context.put(
                    _type=entity_type, name=name, parent_id=parent_id)
                ids[i] = entity[Context.ID]

        entities = self.context.find()

        self.assertEqual(
            len(entities), count_per_entity_type * len(entity_types))

    def test_name(self):
        """
        Test to change of name
        """

        entity = self.context.put(_type='test', name='test')

        putted_entity = self.context.get(ids=entity[Context.ID])

        self.assertEqual(putted_entity[Context.NAME], 'test')

        entity = {
            Context.NAME: 'tset'
        }

        new_name_entity = self.context.put(_type='test',
            _id=putted_entity[Context.ID], name='test', entity=entity)

        self.assertEqual(new_name_entity[Context.NAME], 'tset')

        entities = self.context.find()

        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0][Context.NAME], 'tset')


class RemoveTest(ContextTest):

    pass


class ContextFromRKTest(TestCase):

    def test_connector(self):
        """
        Test with empty rk
        """

        rk = '/a'

        ctx = Context.get_ctx_from_rk(rk)

        self.assertEqual(ctx, {'connector': 'a'})

    def test_resource(self):
        """
        Test with resource
        """
        rk = '/a/b/c/d'

        ctx = Context.get_ctx_from_rk(rk=rk)

        self.assertEqual(
            ctx,
            {
                'connector': 'a',
                'connector_name': 'b',
                'component': 'c',
                'resource': 'd'
            }
        )

    def test_over(self):
        """
        Test with an rk which has more names than entity types
        """

        rk = '/a/b/c/d/e'

        ctx = Context.get_ctx_from_rk(rk=rk)

        self.assertEqual(
            ctx,
            {
                'connector': 'a',
                'connector_name': 'b',
                'component': 'c',
                'resource': 'd'
            }
        )


class GetCTXFromEvent(TestCase):

    def test_empty(self):
        """
        Test empty event
        """

        ctx = Context.get_ctx_from_event(event={})

        self.assertEqual(ctx, {})

    def test_connector(self):
        """
        Test connector event
        """

        event = {
            'connector': 'a',
            'test': 'b'
        }

        ctx = Context.get_ctx_from_event(event=event)

        self.assertEqual(ctx, {'connector': 'a'})

    def test_resource(self):
        """
        Test resource event
        """

        event = {
            'connector': 'a',
            'connector_name': 'b',
            'component': 'c',
            'resource': 'd',
            'test': 'e'
        }

        ctx = Context.get_ctx_from_event(event=event)

        self.assertEqual(
            ctx,
            {
                'connector': 'a',
                'connector_name': 'b',
                'component': 'c',
                'resource': 'd'
            }
        )

if __name__ == '__main__':
    main()
