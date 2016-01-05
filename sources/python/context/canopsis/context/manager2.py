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

from canopsis.configuration.configurable.registry import ConfigurableRegistry
from canopsis.configuration.configurable.decorator import conf_paths
from canopsis.configuration.configurable.decorator import add_category
from canopsis.configuration.model import Parameter

from canopsis.graph.elements import Vertice, Edge, Graph
from canopsis.event.base import Event
from hashlib import sha1


CONF_PATH = 'context/manager.conf'
CATEGORY = 'context'
CONTENT = [
    Parameter('extra_event_fields', parser=Parameter.array())
]


@conf_paths(CONF_PATH)
@add_category(CATEGORY, content=CONTENT)
class ContextManager(ConfigurableRegistry):

    GRAPH_MANAGER = 'graph_manager'

    @staticmethod
    def gen_id(namespace, name):
        return sha1(namespace + name)

    @property
    def extra_event_fields(self):
        if not hasattr(self, '_extra_event_fields'):
            self.extra_event_fields = None

        return self._extra_event_fields

    @extra_event_fields.setter
    def extra_event_fields(self, value):
        if value is None:
            value = []

        self._extra_event_fields = value

    def __init__(
        self,
        graph_manager=None,
        extra_event_fields=None,
        *args, **kwargs
    ):
        super(ContextManager, self).__init__(*args, **kwargs)

        if graph_manager is not None:
            self[ContextManager.GRAPH_MANAGER] = graph_manager

        if extra_event_fields is not None:
            self.extra_event_fields = extra_event_fields

    @property
    def graph_id(self):
        return self.gen_id('context', 'graphentity')

    def get_graph_or_create(self):
        manager = self[ContextManager.GRAPH_MANAGER]

        graph = manager.get_graphs(ids=self.graph_id)

        if not graph:
            graph = Graph(id=self.graph_id)
            graph.save(manager)

        return graph

    def get_entities(self, uids=None, types=None, info=None, query=None):
        manager = self[ContextManager.GRAPH_MANAGER]

        return manager.get_elts(
            ids=uids,
            types=types,
            base_type=Vertice.BASE_TYPE,
            info=info,
            query=query,
            graph_ids=self.graph_id
        )

    def create_entity(
        self,
        uid,
        type=None,
        components=None,
        info=None,
        vertice_cls=Vertice
    ):
        manager = self[ContextManager.GRAPH_MANAGER]

        entity = self.get_entities(
            uids=[uid],
            types=[type],
            info=info
        )

        if not entity:
            graph = self.get_graph_or_create()
            entity = vertice_cls(id=uid, type=type, info=info)
            graph.add_elts(entity)

            entity.save(manager)
            graph.save(manager)

        else:
            entity = entity[0]

        if components is not None:
            self.link_entities(
                type='compositionedge',
                source=entity,
                targets=components
            )

        return entity

    def update_entity(self, entity):
        manager = self[ContextManager.GRAPH_MANAGER]
        entity.save(manager)

    def remove_entity(self, entity):
        manager = self[ContextManager.GRAPH_MANAGER]
        entity.delete(manager)

    def link_entities(self, type, source, targets, info=None, edge_cls=Edge):
        manager = self[ContextManager.GRAPH_MANAGER]
        edge_id = '/{0}/{1}'.format(type, source.id)

        targets = [
            target if isinstance(target, basestring) else target.id
            for target in targets
        ]

        edge = manager.get_elts(
            ids=edge_id,
            types=[type],
            base_type=edge_cls.BASE_TYPE,
            info=info,
            graph_ids=self.graph_id
        )

        if not edge:
            edge = edge_cls(
                id=edge_id,
                type=type,
                sources=[source.id],
                targets=targets,
                info=info
            )

        else:
            edge.targets += targets

        edge.save(manager)

        return edge

    def entites_from_event(self, event):
        event = Event(event)

        typed_connector = self.create_entity(
            uid=self.gen_id('context-typedconnector', event.connector),
            type='typedconnectorentity',
            info={
                'name': event.connector
            }
        )

        named_connector = self.create_entity(
            uid=self.gen_id('context-namedconnector', event.connector_name),
            type='namedconnectorentity',
            info={
                'name': event.connector_name,
                'connector': event.connector
            }
        )

        self.link_entities(
            type='instanceofedge',
            source=named_connector,
            targets=[typed_connector]
        )

        component = self.create_entity(
            uid=self.gen_id('context-component', event.component),
            type='componententity',
            info={
                'name': event.component
            }
        )

        entities = [
            typed_connector,
            named_connector,
            component
        ]

        if event.source_type == 'resource':
            resource = self.create_entity(
                uid=self.gen_id('context-resource', event.resource),
                type='resourceentity',
                components=[component],
                info={
                    'name': event.resource,
                    'component': event.component
                }
            )

            entities.append(resource)

            scope = resource

        else:
            scope = component

        self.link_entities(
            type='feededge',
            source=named_connector,
            targets=[scope]
        )

        metas = []

        for key in self.extra_event_fields:
            if key in event:
                info = {
                    'meta': key,
                    'value': event[key],
                    'component': event.component
                }

                if event.source_type == 'resource':
                    info['resource'] = event.resource

                meta = self.create_entity(
                    uid=self.gen_id('context-meta', event[key]),
                    type='metaentity',
                    info=info
                )

                metas.append(meta)

        self.link_entities(
            type='hasmetaedge',
            source=scope,
            targets=metas
        )

        metrics = []

        for metric in event.metrics:
            info = {
                'name': metric['metric'],
                'component': event.component
            }

            if event.source_type == 'resource':
                info['resource'] = event.resource

            metric_entity = self.create_entity(
                uid=self.gen_id('context-metric', metric['metric']),
                type='metricentity',
                info=info
            )

            metrics.append(metric_entity)

        self.link_entities(
            type='producemetricedge',
            source=scope,
            targets=metrics
        )

        entities += metas + metrics

        return scope, entities

    def get_linked_entities(self, entity, types=None, info=None, query=None):
        manager = self[ContextManager.GRAPH_MANAGER]

        edges = manager.get_edges(
            sources=entity.id,
            graph_ids=self.graph_id
        )

        linked_entities = []

        for edge in edges:
            linked_entities += edge.targets

        return self.get_entities(
            uids=linked_entities,
            types=types,
            info=info,
            query=query
        )

    def get_event(self, entity, event_type=Event, **kwargs):
        fields = entity.info.copy()
        fields.update(kwargs)

        return event_type.create(**fields)
