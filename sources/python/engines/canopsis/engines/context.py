# -*- coding: UTF-8 -*-
#--------------------------------
# Copyright (c) 2011 "Capensis" [http://www.capensis.com]
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

from canopsis.engines import Engine

from canopsis.context.manager import Context
"""
TODO: sla
from canopsis.middleware import Middleware
"""

HOSTGROUPS = 'hostgroups'
SERVICEGROUPS = 'servicegroups'

HOSTGROUP_TYPE = 'hostgroup'
SERVICEGROUP_TYPE = 'servicegroup'


class engine(Engine):
    etype = 'context'

    def __init__(self, *args, **kwargs):
        super(engine, self).__init__(*args, **kwargs)

        # get a context
        self.context = Context()
        """
        TODO: sla
        # get a storage for sla macro
        #self.storage = Middleware.get_middleware(
        #    protocol='storage', data_scope='global')

        #self.sla = None
        """
        self.beat()

    def beat(self):
        """
        TODO: sla
        sla = self.storage.find_elements(request={
            'crecord_type': 'sla',
            'objclass': 'macro'
        })

        if sla:
            self.sla = sla[0]
        """

    def work(self, event, *args, **kwargs):
        mCrit = 'PROC_CRITICAL'
        mWarn = 'PROC_WARNING'

        """
        TODO: sla
        if self.sla:
            mCrit = self.sla.data['mCrit']
            mWarn = self.sla.data['mWarn']
        """

        # find the right ctx related to (connector, connector_name, ...)
        ctx = self.context.get_entity_from_evt(event)
        # add event entities to DB
        entities = self.get_entities_from_ctx(ctx=ctx)

        if entities:  # if entity of types (connector, ...) exists
            # get last found entity
            entity = entities[-1]

            connector_name = event['connector_name']
            component = event['component']

            # dict which contains data to update
            data_to_update = {}

            connector = event['connector']
            if 'connector' not in entity or connector != entity['connector']:
                data_to_update['connector'] = connector
            connector_name = event['connector_name']
            if 'connector_name' not in entity or connector_name != entity['connector_name']:
                data_to_update['connector_name'] = connector_name
            component = event['component']
            if 'component' not in entity or component != entity['component']:
                data_to_update['component'] = component

            # get status data
            mCrit = event.get('mCrit')
            mWarn = event.get('mWarn')
            state = event['state']
            state_type = event['state_type']

            # add status to data_to_update if necessary
            if entity.get('mCrit', None) != mCrit:
                data_to_update['mCrit'] = mCrit
            if entity.get('mWarn', None) != mWarn:
                data_to_update['mWarn'] = mWarn
            if entity.get('state', None) != state:
                data_to_update['state'] = state
            if entity.get('state_type', None) != state_type:
                data_to_update['state_type'] = state_type

            # if entity type is a component or a resource
            if entity[Context.TYPE] in ('component', 'resource'):

                # Get hostgroups informations
                hostgroups = event.get(HOSTGROUPS, [])

                # add hostgroups
                hostgroup_entities = self.context.find(
                    types=HOSTGROUP_TYPE, names=hostgroups)
                if len(hostgroups) != hostgroup_entities:
                    for hostgroup in hostgroups:
                        self.context.put(_type=HOSTGROUP_TYPE, name=hostgroup)

                # add hostgroups to data_to_update if necessary
                if entity.get(HOSTGROUPS, []) != hostgroups:
                    data_to_update[HOSTGROUPS] = hostgroups

                # if status data_to_update is a resource
                if entity[Context.TYPE] == 'resource':

                    # Get servicegroups informations
                    servicegroups = event.get(SERVICEGROUPS, [])

                    # add servicegroups
                    servicegoup_entities = self.context.find(
                        types=SERVICEGROUP_TYPE, names=servicegroups)
                    if len(servicegroups) != servicegoup_entities:
                        for servicegoup in servicegroups:
                            self.context.put(
                                _type=SERVICEGROUP_TYPE, name=servicegoup)

                    # add servicegroups to data_to_update if necessary
                    if entity.get(SERVICEGROUPS, []) != servicegroups:
                        data_to_update[SERVICEGROUPS] = servicegroups

                # update the data_to_update if necessary
                if data_to_update:
                    put_args = {
                        '_type': entity[Context.TYPE],
                        'name': entity[Context.NAME],
                        '_id': entity[Context.ID],
                        'entity': data_to_update
                    }
                    if Context.PARENT_ID in entity:
                        put_args['parent_id'] = entity[Context.PARENT_ID]
                    self.context.put(**put_args)

            # add authored data_to_update data (downtime, ack, metric, etc.)
            authored_entity = {}
            event_type = event['event_type']

            if 'author' in event:
                authored_entity['author'] = event['author']
                if 'output' in event:
                    authored_entity['comment'] = event['output']

            # only ack and downtime event type are managed
            if event_type in ('ack', 'downtime'):

                if event_type == 'ack':
                    authored_entity['timestamp'] = event['timestamp']
                    _id = str(event['timestamp'])

                elif event_type == 'downtime':
                    authored_entity['downtime_id'] = event['downtime_id']
                    authored_entity['start'] = event['start']
                    authored_entity['end'] = event['end']
                    authored_entity['duration'] = event['duration']
                    authored_entity['fixed'] = event['fixed']
                    authored_entity['entry'] = event['entry']
                    _id = event['id']

                # this time, parent id is entity[Context.ID]
                parent_id = entity[Context.ID]

                # push authored data in DB
                self.context.put(
                    _type=event_type,
                    name=_id,
                    _id=_id,
                    entity=authored_entity,
                    parent_id=parent_id
                )

            else:
                self.logger.error(
                    'Event type {0} if not managed such as an authored data'.
                    format(event))

            # add perf data
            for perfdata in event.get('perf_data_array', []):
                name = perfdata['metric']
                _type = 'metric'
                perfdata_entity = {
                    'internal': perfdata['metric'].startswith('cps')
                }
                perfdatum = self.find(
                    types=_type, names=name, parent_ids=parent_id)
                if not perfdatum:  # only if it didn't exist
                    self.context.put(
                        _type=_type,
                        entity=perfdata_entity,
                        name=name,
                        parent_id=parent_id
                    )

        else:
            self.logger.error(
                'Event {0} is not associated to any data_to_update'.format(
                    event))

        return event
