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

from canopsis.task import register_task

from canopsis.perfdata.manager import PerfData
from canopsis.context.manager import Context

from copy import deepcopy


perfdatamgr = PerfData()


@register_task
def event_processing(engine, event, manager=None, logger=None, **params):
    if manager is None:
        manager = perfdatamgr

    perf_data_array = event.get('perf_data_array', [])

    for perf_data in perf_data_array:
        perf = perf_data.copy()

        # get metric id
        event_with_metric = deepcopy(event)
        event_with_metric['type'] = 'metric'
        event_with_metric[Context.NAME] = perf.pop('metric')

        metric_id = manager.context.get_entity_id(
            event_with_metric
        )

        # get metric state
        perf['state'] = 0

        warn = perf.get('warn', None)
        crit = perf.get('crit', None)

        if warn:
            c0 = crit is not None and crit >= warn and perf['value'] > warn
            c1 = crit is not None and crit < warn and perf['value'] < warn
            c2 = crit is None and perf['value'] > warn

            if any([c0, c1, c2]):
                perf['state'] = 1

        if crit:
            c0 = warn is not None and crit >= warn and perf['value'] > crit
            c1 = warn is not None and crit < warn and perf['value'] < crit
            c2 = warn is None and perf['value'] > crit

            if any([c0, c1, c2]):
                perf['state'] = 2

        perf.pop('value', None)
        manager.put_meta(metric_id, perf, event['timestamp'], cache=True)
