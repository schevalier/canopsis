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
from canopsis.event.base import Event
from canopsis.task import get_task

from canopsis.router.filter import Filter
from copy import deepcopy
import json


CONF_PATH = 'router/manager.conf'
CATEGORY = 'ROUTER'
CONTENT = []


@conf_paths(CONF_PATH)
@add_category(CATEGORY, content=CONTENT)
class RouterManager(MiddlewareRegistry):

    FILTER_STORAGE = 'filter_storage'
    JOB_MANAGER = 'job_manager'

    def __init__(self, filter_storage=None, job_manager=None, *args, **kwargs):
        super(RouterManager, self).__init__(*args, **kwargs)

        if filter_storage is not None:
            self[RouterManager.FILTER_STORAGE] = filter_storage

        if job_manager is not None:
            self[RouterManager.JOB_MANAGER] = job_manager

        self.configuration = {
            'rules': [],
            'default_action': 'pass'
        }

        self.passed = 0
        self.dropped = 0

    def reload_configuration(self):
        storage = self[RouterManager.FILTER_STORAGE]

        configuration = {
            'rules': [],
            'default_action': 'pass'
        }

        daction = storage.get_elements(
            query={
                'crecord_type': 'defaultrule'
            }
        )

        if len(daction) > 0:
            configuration['default_action'] = daction[0]['action']

        rules = storage.find_elements(
            query={
                'crecord_type': 'filter',
                'enable': True
            },
            sort='priority'
        )

        for rule in rules:
            try:
                _filter = json.loads(rule['filter'])

            except ValueError as err:
                self.logger.error('Invalid filter "{0}": {1}'.format(
                    rule['name'],
                    err
                ))

            else:
                rule['loaded'] = True
                storage.put_element(element=rule)

                rule['filter'] = Filter(_filter)
                configuration['rules'].append(rule)

        self.configuration = configuration

    def get_stats_event(self):
        event = Event.create(
            event_type='perf',
            source_type='resource',
            resource='router-stats',
            output='{0} passed / {1} dropped'.format(
                self.passed, self.dropped
            ),
            metrics=[
                {
                    'metric': 'passed',
                    'value': self.passed,
                    'unit': 'evt',
                    'type': 'GAUGE'
                },
                {
                    'metric': 'dropped',
                    'value': self.dropped,
                    'unit': 'evt',
                    'type': 'GAUGE'
                }
            ]
        )

        self.passed = 0
        self.dropped = 0

        return event

    def apply_rules(self, event):
        rules = self.configuration.get('rules', [])
        old_event = deepcopy(event)
        matched = False

        for rule in rules:
            if rule['filter'].match(event):
                matched = True

                self.logger.debug('Matching event on "{0}": {1}'.format(
                    rule['name'],
                    old_event['rk']
                ))

                for action in rule['actions']:
                    event = self.apply_action(event, action)

                    if event is None:
                        break

                if rule['break']:
                    self.logger.debug('Breaking rule: {0}'.format(
                        rule['name']
                    ))

                    break

        if not matched:
            event = self.apply_action(
                event,
                self.configuration['default_action']
            )

        if event is None:
            self.logger.debug('Event dropped: {0}'.format(old_event['rk']))
            self.dropped += 1
            return None

        else:
            self.passed += 1
            return event

    def apply_action(self, event, action):
        aname = action.pop('name')
        task = get_task('router.{0}'.format(aname))

        return task(
            manager=self,
            event=event,
            **action
        )
