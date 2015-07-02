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

from canopsis.event.manager import Event
from canopsis.organisation.rights import Rights
from canopsis.engines.core import Engine, publish
from canopsis.session.manager import Session
from canopsis.event import forger

import pprint
pp = pprint.PrettyPrinter(indent=4)


class engine(Engine):

    etype = 'stats'

    event_manager = Event()
    right_manager = Rights()
    session_manager = Session()

    """
    This engine's goal is to compute canopsis internal statistics.
    Statistics are computed on each passing event and are updated
    in async way in order to manage performances issues.
    """

    def __init__(self, *args, **kargs):

        super(engine, self).__init__(*args, **kargs)

        self.states_str = {
            0: 'info',
            1: 'minor',
            2: 'major',
            3: 'critical'
        }

    def pre_run(self):

        self.beat()
        #TODO remove consume dispatcher call
        self.consume_dispatcher({})

    def consume_dispatcher(self, event, *args, **kargs):

        """
        Entry point for stats computation. Triggered by the dispatcher
        engine for distributed processing puroses.
        Following methods will generate metrics that are finally embeded
        in a metric event.
        """

        self.logger.debug('Entered in stats consume dispatcher')

        self.perf_data_array = []

        # Some queries may be used twice, so cache them for performance
        self.prepare_queries()

        self.compute_states()

        self.publish_states()

    def prepare_queries(self):

        """
        Stats are computed from database information. This methods
        let perform cached results queries that are available in
        all stats methods. Cached result should not be altered while 
        processing stats computation
        """

        users = self.right_manager.get_users()
        self.userlist = [user['_id'] for user in list(users)]

        # Query for current ack events
        cursor = self.event_manager.find(
            query={
                'ack.isAck': True
            },
            projection={
                'ack.author': 1,
                'ack.timestamp': 1,
                'last_state_change': 1,
                'domain': 1,
                'perimeter': 1
            }
        )
        self.ack_events = list(cursor)

        cursor = self.event_manager.find(
            query={
                'ack.wasAck': {'$exists': True}
            },
            projection={
                'ack.wasAck': 1,
            }
        )
        self.solved_alerts_events = list(cursor)
        self.logger.debug(self.solved_alerts_events)

    def compute_states(self):

        """
        Entry point for dynamic stats method triggering
        Dynamic triggering allow greated control on which
        stats are computed and can be activated/deactivated
        from frontend.
        """

        # Allow individual stat computation management from ui.
        stats_to_compute = [
            'event_count_by_source',
            'event_count_by_source_and_state',
            'event_count_by_state',
            'users_session_duration',
            'ack_count',
            'solved_alerts',
        ]

        for stat in stats_to_compute:
            method = getattr(self, stat)
            method()

    def add_metric(self, mname, mvalue, mtype='COUNTER'):
        self.perf_data_array.append({
            'metric': mname,
            'value': mvalue,
            'type': mtype
        })

    def solved_alerts(self):

        was_ack = 0
        was_not_ack = 0

        for event in self.solved_alerts_events:
            if event['ack']['wasAck']:
                was_ack += 1
            else:
                was_not_ack += 1

        self.add_metric('cps_solved_alert_ack', was_ack)
        self.add_metric('cps_solved_alert_not_ack', was_not_ack)

    def ack_count(self):
        ack_count = len(self.ack_events)
        self.add_metric('cps_ack_count', ack_events)

    def users_session_duration(self):
        sessions = self.session_manager.get_new_inactive_sessions()
        metrics = self.session_manager.get_delta_session_time_metrics(sessions)
        self.perf_data_array += metrics
        self.logger.debug(self.perf_data_array)

    def event_count_by_source(self):

        """
        Counts and produces metrics for events depending on source type
        """

        for source_type in ('resource', 'component'):
            # Event count source type
            cursor, count = self.event_manager.find(
                query={'source_type': source_type},
                with_count=True
            )

            self.add_metric(
                'cps_count_{}'.format(
                    source_type
                ),
                count
            )

    def event_count_by_source_and_state(self):

        """
        Counts and produces metrics for events depending on source type,
        by state
        """

        for source_type in ('resource', 'component'):

            # Event count by source type and state
            for state in (0, 1, 2, 3):

                # There is an index on state and source_type field in
                # events collection, that would keep the query efficient
                cursor, count = self.event_manager.find(
                    query={
                        'source_type': source_type,
                        'state': state
                    },
                    with_count=True
                )

                state_str = self.states_str[state]

                self.add_metric(
                    'cps_states_{}_{}'.format(
                        source_type,
                        state_str
                    ),
                    count
                )

    def event_count_by_state(self):

        """
        Counts and produces metrics for events depending on state
        """

        # Event count computation by state
        for state in (0, 1, 2, 3):
            # There is an index on state field in events collection,
            # that would keep the query efficient
            cursor, count = self.event_manager.find(
                query={'state': state},
                with_count=True
            )

            state_str = self.states_str[state]

            self.add_metric(
                'cps_states_{}'.format(state_str),
                count
            )

    def publish_states(self):

        stats_event = forger(
            connector='engine',
            connector_name='engine',
            event_type='perf',
            source_type='resource',
            resource='Engine_stats',
            state=0,
            perf_data_array=self.perf_data_array
        )

        metrics = []
        for m in self.perf_data_array:
            metrics.append('{}\t{}\t{}'.format(
                m['value'],
                m['type'],
                m['metric']
            ))

        self.logger.debug('-- Generated perfdata --\n{}'.format(
            '\n'.join(metrics)
        ))

        publish(publisher=self.amqp, event=stats_event)
