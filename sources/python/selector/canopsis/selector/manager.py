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

from canopsis.middleware.registry import MiddlewareRegistry
from canopsis.configuration.configurable.decorator import conf_paths
from canopsis.configuration.configurable.decorator import add_category

from canopsis.common.template import Template
from canopsis.selector.event import Selector
from canopsis.event.check import Check
from canopsis.task import get_task


CONF_PATH = 'selector/manager.conf'
CATEGORY = 'SELECTOR'
CONTENT = []


@conf_paths(CONF_PATH)
@add_category(CATEGORY, content=CONTENT)
class SelectorManager(MiddlewareRegistry):

    CONFIG_STORAGE = 'config_storage'
    ALERTS_MANAGER = 'alerts_manager'
    CONTEXT_MANAGER = 'context_manager'

    def __init__(
        self,
        config_storage=None,
        alerts_manager=None,
        context_manager=None,
        *args, **kwargs
    ):
        super(SelectorManager, self).__init__(*args, **kwargs)

        if config_storage is not None:
            self[SelectorManager.CONFIG_STORAGE] = config_storage

        if alerts_manager is not None:
            self[SelectorManager.ALERTS_MANAGER] = alerts_manager

        if context_manager is not None:
            self[SelectorManager.CONTEXT_MANAGER1] = context_manager

    def get_selectors(self):
        return self[SelectorManager.CONFIG_STORAGE].find_elements()

    def get_entities_by_selector(self, selector):
        context = self[SelectorManager.CONTEXT_MANAGER]

        context_filter = selector.get('context_filter', {})
        include_ids = selector.get('include_ids', None)
        exclude_ids = selector.get('exclude_ids', None)

        entities = context.find(_filter=context_filter)

        if include_ids:
            entities += context.get_entities(include_ids)

        if exclude_ids:
            entities = filter(
                lambda e: context.get_entity_id(e) not in exclude_ids,
                entities
            )

        return entities

    def get_alarms_by_entities(self, entities):
        context = self[SelectorManager.CONTEXT_MANAGER]
        entities_ids = map(context.get_entity_id, entities)

        result = self[SelectorManager.ALERTS_MANAGER].get_alarms(
            resolve=False
        )

        for data_id in result.keys():
            if data_id not in entities_ids:
                del result[data_id]

        return result

    def get_states_from_alarms(self, entities, alarms):
        context = self[SelectorManager.CONTEXT_MANAGER]
        entities_ids = map(context.get_entity_id, entities)

        result = []

        for entity_id in entities_ids:
            if entity_id not in alarms:
                result.append((entity_id, Check.OK, False))

            else:
                for alarm in alarms[entity_id]:
                    result.append((
                        entity_id,
                        alarm['state']['val'],
                        alarm['ack'] is not None
                    ))

        return result

    def is_selector_ack(self, selector, states):
        n_ack = len(filter(
            lambda s: s[2],
            states
        ))

        return n_ack == len(states)

    def get_selector_state(self, selector, states):
        if self.is_selector_ack(selector, states):
            task = get_task('selector.states.{0}'.format(
                selector['state_when_all_ack']
            ))

        else:
            task = get_task('selectorManager.states.{0}'.format(
                selector['state_algorithm']
            ))

        return task(selector, states)

    def get_event_from_selector(self, selector):
        entities = self.get_entities_by_selector(selector)
        alarms = self.get_alarms_by_entities(entities)
        states = self.get_states_from_alarms(entities, alarms)
        state = self.get_selector_state(selector, states)

        n_items = {
            'state_{0}'.format(state): len(filter(
                lambda s: s[1] == state
            ))
            for state in [Check.OK, Check.MINOR, Check.MAJOR, Check.CRITICAL]
        }
        n_items['ack'] = len(filter(
            lambda s: s[2],
            states
        ))
        n_items['total'] = len(states)

        template = Template(selector['output_tpl'])
        output = template(n_items)

        metrics = [
            {
                'metric': 'cps_sel_{0}'.format(n_item),
                'value': n_items[n_item]
            }
            for n_item in n_items
        ]

        event = Selector.create(
            source_type='component',
            component=selector['display_name'],
            state=state,
            output=output,
            metrics=metrics
        )

        return event
