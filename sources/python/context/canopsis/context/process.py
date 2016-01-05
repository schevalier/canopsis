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

from canopsis.common.utils import singleton_per_scope
from canopsis.context.manager import ContextManager


def event_processing(engine, event, logger=None, manager=None, **kwargs):
    if manager is None:
        manager = singleton_per_scope(ContextManager)

    scope, entities = manager.entities_from_event(event)

    logger.debug('Scope: {0}'.format(scope.id))
    map(
        lambda e: logger.debug('Entity: {0}'.format(e.id)),
        entities
    )

    return event
