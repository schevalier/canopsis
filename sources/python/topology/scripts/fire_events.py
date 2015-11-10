#!/usr/bin/env python
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

from canopsis.topology.manager import TopologyManager
from canopsis.old.rabbitmq import Amqp
from canopsis.engines.core import publish


def fire_events():

    manager = TopologyManager()
    publisher = Amqp()

    graphs = manager.get_graphs()

    for graph in graphs:
        graph.state = 0
        event = graph.get_event(state=0)
        publish(publisher=publisher, event=event)

if __name__ == '__main__':
    fire_events()
