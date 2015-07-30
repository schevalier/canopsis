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

"""Module in charge of loading a referential.
"""

from canopsis.common.utils import singleton_per_scope
from canopsis.context.manager import Context


def loadReferential(
        self, referential, connector='canopsis', connector_name='canopsis'
):
    """Load a referential.

    This version uses topology in order to load edges. The future version will
    use the Contextv2 with context edges.

    :param dict referential: referential from where get elts.
    :param str connector: default connector to use if no connector given in
        elts. canopsis by default.
    :param str connector_name: default connector name to use if no
        connector_name given in elts. canopsis by default.
    """

    # load internally topology elements which might be trashed with contextv2
    from canopsis.topology.manager import TopologyManager
    from canopsis.topology.elements import TopoNode, TopoEdge

    # load referential loaders
    contextmanager = singleton_per_scope(Context)
    topologymanager = singleton_per_scope(TopologyManager)

    def toponodeid(entity_id):
        """Get a toponodeid from an entity_id.

        :param str entity_id: entity id to transform to a toponode id.
        :return: related toponodeid.
        :rtype: str
        """

        return 'node::{0}'.format(entity_id)

    # start to load elts which might be entities with(out) entity id
    elts = referential.get('elts')
    for elt in elts:
        # set connector and connector_name if not given
        elt.setdefault('connector', connector)
        elt.setdefault('connector_name', connector_name)
        # put the elt in the context
        contextmanager.put(_type=elt['type'], entity=elt)
        # get entity id
        entity_id = elt.get('id', contextmanager.get_entity_id(elt))
        # load a toponode in the topology manager
        nodeid = toponodeid(entity_id=entity_id)
        node = TopoNode(id=nodeid, entity=entity_id)
        node.save(manager=topologymanager)

    # load edges
    edges = referential.get('elts')
    for edge in edges:
        topoedge = TopoEdge(**edge)
        sources = [toponodeid(source) for source in topoedge['sources']]
        targets = [toponodeid(target) for target in topoedge['targets']]
        topoedge = TopoEdge(
            id=edge.get('id'), sources=sources, targets=targets,
            type=edge.get('type')
        )
        topoedge.save(manager=topologymanager)
