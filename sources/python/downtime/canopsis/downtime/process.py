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

"""Module in charge of defining downtime processing in engines."""

from canopsis.common.utils import singleton_per_scope
from canopsis.context.manager import Context
from canopsis.pbehavior.manager import PBehaviorManager
from canopsis.task.core import register_task
from canopsis.event.manager import EventManager
from canopsis.event import Event

from datetime import datetime, timedelta
from icalendar import Event as vEvent

DOWNTIME = 'downtime'  #: downtime pbehavior value

DOWNTIME_QUERY = PBehaviorManager.get_query(behaviors=DOWNTIME)


@register_task
def event_processing(
        event, context=None, manager=None, evtm=None, logger=None, **kwargs
):
    """Process input event.

    :param dict event: event to process.
    :param Context manager: context manager to use. Default is shared a Context
        .
    :param PBehaviorManager manager: pbehavior manager to use. Default is
        a shared PBehaviorManager.
    :param EventManager evtm: event manager to use. Default is a shared
        EventManager.
    :param Logger logger: logger to use in this task.
    """

    if context is None:
        context = singleton_per_scope(Context)

    if manager is None:
        manager = singleton_per_scope(PBehaviorManager)

    if evtm is None:
        evtm = singleton_per_scope(EventManager)

    evtype = event[Event.TYPE]
    entity = context.get_entity(event)
    eid = context.get_entity_id(entity)

    if evtype == DOWNTIME:
        vev = vEvent()
        vev.add('X-Canopsis-BehaviorType', DOWNTIME)
        vev.add('summary', event['output'])
        vev.add('dtstart', datetime.fromtimestamp(event['start']))
        vev.add('dtend', datetime.fromtimestamp(event['end']))
        vev.add('dtstamp', datetime.fromtimestamp(event['entry']))
        vev.add('duration', timedelta(event['duration']))
        vev.add('contact', event['author'])

        manager.put(source=eid, vevents=[vev])

        if manager.getending(
                source=eid, behaviors=DOWNTIME, ts=event['timestamp']
        ):

            event = {
                'connector': event['connector'],
                'connector_name': event['connector_name'],
                'component': event['component'],
                'resource': event.get('resource', None)
            }
            evtm.update_event(content={DOWNTIME: True}, event=event)

    else:
        event[DOWNTIME] = manager.getending(
            source=eid, behaviors=DOWNTIME
        ) is not None

    return event


@register_task
def beat_processing(
        context=None, manager=None, evtm=None, logger=None, **kwargs
):
    """Process periodic task.

    :param Context manager: context manager to use. Default is a shared Context
        .
    :param PBehaviorManager manager: pbehavior manager to use. Default is a
        shared PBehaviorManager.
    :param EventManager evtm: event manager to use. Default is a shared
        EventManager.
    :param Logger logger: logger to use in this task.
    """

    if context is None:
        context = singleton_per_scope(Context)

    if manager is None:
        manager = singleton_per_scope(PBehaviorManager)

    if evtm is None:
        evtm = singleton_per_scope(EventManager)

    entity_ids = manager.whois(query=DOWNTIME_QUERY)
    entities = context.get_entities(list(entity_ids))

    spec = {}

    for key in ['connector', 'connector_name', 'component', 'resource']:
        spec[key] = {
            '$nin': list(e.get(key, None) for e in entities)
        }

    evtm.update_event(content={DOWNTIME: False}, event=spec)
