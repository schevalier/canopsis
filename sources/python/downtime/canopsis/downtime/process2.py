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
from canopsis.pbehavior.manager import PBehaviorManager
from canopsis.event.downtime import Downtime

from datetime import datetime, timedelta
from icalendar import Event as vEvent


def event_processing(
    engine,
    event,
    logger=None,
    context=None,
    pbehavior=None,
    **kwargs
):
    if context is None:
        context = singleton_per_scope(ContextManager)

    if pbehavior is None:
        pbehavior = singleton_per_scope(PBehaviorManager)

    evtype = event[Downtime.EVENT_TYPE]
    scope, _ = context.entities_from_event(event)

    if evtype == Downtime.DEFAULT_EVENT_TYPE:
        ev = vEvent()
        ev.add(PBehaviorManager.BEHAVIOR_TYPE, '["downtime"]')
        ev.add('summary', event[Downtime.OUTPUT])
        ev.add('dtstart', datetime.fromtimestamp(event[Downtime.START]))
        ev.add('dtend', datetime.fromtimestamp(event[Downtime.END]))
        ev.add('dtstamp', datetime.fromtimestamp(event[Downtime.ENTRY]))
        ev.add('duration', timedelta(event[Downtime.DURATION]))
        ev.add('contact', event[Downtime.AUTHOR])

        pbehavior.put(source=scope.id, vevents=[ev])

    else:
        event['downtime'] = pbehavior.getend(
            source=scope.id,
            behaviors='downtime'
        ) is not None

    return event
