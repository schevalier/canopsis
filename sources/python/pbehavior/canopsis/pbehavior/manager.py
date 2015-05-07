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

from canopsis.common.init import basestring
from canopsis.configuration.configurable.decorator import (
    add_category, conf_paths
)
from canopsis.middleware.registry import MiddlewareRegistry
from canopsis.storage import Storage

from json import loads

from time import time

from icalendar import Event
from dateutil.rrule import rrulestr
from calendar import timegm

from datetime import datetime, time as datetime_time

from uuid import uuid4 as uuid

#: pbehavior manager configuration path
CONF_PATH = 'pbehavior/pbehavior.conf'
#: pbehavior manager configuration category name
CATEGORY = 'PBEHAVIOR'


@conf_paths(CONF_PATH)
@add_category(CATEGORY)
class PBehaviorManager(MiddlewareRegistry):
    """Dedicated to manage periodic behavior.

    Such period are technically an expression which respects the icalendar
    specification ftp://ftp.rfc-editor.org/in-notes/rfc2445.txt.

    A pbehavior document contains several values. Each value contains
    an icalendar expression (dtstart, rrule, duration) and an array of
    behavior entries:

    {
        id: document_id,
        entity_id: entity id,
        period: period,
        behaviors: behavior ids
    }.
    """

    PBEHAVIOR_STORAGE = 'pbehavior_storage'  #: pbehavior storage name

    BEHAVIOR = 'X-Canopsis-BehaviorType'  #: behavior type key in period

    ID = Storage.DATA_ID  #: document id
    ENTITY = 'entity_id'  #: entity id
    PERIOD = 'period'  #: period value field name
    BEHAVIORS = 'behaviors'  #: behaviors value field name

    def __init__(self, PBEHAVIOR_storage=None, *args, **kwargs):

        super(PBehaviorManager, self).__init__(*args, **kwargs)

        if PBEHAVIOR_storage is not None:
            self[PBehaviorManager.PBEHAVIOR_STORAGE] = PBEHAVIOR_storage

    def get(self, ids):
        """Get a document related to input id(s).

        :param ids: document id(s) to get.
        :type ids: list or str
        :return: depending on ids type:
            - str: one document.
            - list: list of documents.
        :rtype: list or dict
        """

        result = self[PBehaviorManager.PBEHAVIOR_STORAGE].get_elements(
            ids=ids
        )

        return result

    def find(self, entity_ids, behaviors=None):
        """Find documents related to input entity id(s) and behavior(s).

        :param entity_ids:
        :type entity_ids: list or str
        :param behaviors:
        :type behaviors: list or str
        :return: entity documents with input behaviors.
        :rtype: list
        """

        # prepare filter
        _filter = {
            PBehaviorManager.ENTITY: entity_ids,
            PBehaviorManager.BEHAVIORS: behaviors
        }

        result = self[PBehaviorManager.PBEHAVIOR_STORAGE].find_elements(
            _filter=_filter
        )

        return result

    def put(self, _id, document, cache=False):
        """Put a pbehavior document.

        :param str _id: document entity id.
        :param dict document: pbehavior document.
        :param bool cache: if True (False by default), use storage cache.
        :return: _id if input pbehavior document has been putted. Otherwise
            None.
        :rtype: str
        """

        result = self[PBehaviorManager.PBEHAVIOR_STORAGE].put_element(
            _id=_id, element=document, cache=cache
        )

        return result

    def add(self, entity_id, values, behaviors=None):
        """Add a pbehavior entry related to input entity_id and values.

        :param str entity_id: entity id.
        :param values: value(s) to add.
        :type values: str, Event or list of str/Event.
        :param behaviors: value(s) behavior(s) to add. If None, behaviors are
            retrieved from values with the PBehaviorManager.BEHAVIOR key.
        :type behaviors: list or str
        :return: added document ids
        :rtype: list
        """

        # initialize result
        result = []

        # ensure values is a list
        if isinstance(values, (basestring, Event)):
            values = [values]

        # ensure behaviors is a list
        if behaviors is None:
            behaviors = []
        elif isinstance(behaviors, basestring):
            behaviors = [behaviors]

        for value in values:
            event = value
            # ensure value is an event
            if isinstance(value, basestring):
                event = Event.from_ical(value)

            value_behaviors = list(behaviors)
            # update value behaviors
            if PBehaviorManager.BEHAVIOR in event:
                event_behaviors = event.get(PBehaviorManager.BEHAVIOR)
                event_behaviors = loads(event_behaviors)
                if isinstance(event_behaviors, basestring):
                    value_behaviors.append(event_behaviors)
                else:
                    value_behaviors += event_behaviors

            # prepare a document to put
            document = {
                PBehaviorManager.ENTITY: entity_id,
                PBehaviorManager.PERIOD: event.to_ical(),
                PBehaviorManager.BEHAVIORS: value_behaviors
            }

            # put a new document with a new id
            _id = str(uuid())
            self.put(_id=_id, document=document)
            # add _id to result
            result.append(_id)

        return result

    def remove(self, ids=None, cache=False):
        """Remove document(s) by id.

        :param ids: pbehavior document id(s). If None, remove all documents.
        :type ids: list or str
        :param bool cache: if True (False by default), use storage cache.
        :return: removed document id(s).
        :rtype: list
        """

        result = self[PBehaviorManager.PBEHAVIOR_STORAGE].remove_elements(
            ids=ids, cache=cache
        )

        return result

    def remove_by_entity(self, entity_ids, cache=False):
        """Remove document(s) by entity ids.

        :param entity_ids: document entity id(s) to remove.
        :type entity_ids: list or str
        :param bool cache: if True (False by default), use storage cache.
        :return: removed document id(s).
        :rtype: list

        """

        result = self[PBehaviorManager.PBEHAVIOR_STORAGE].remove_elements(
            _filter={PBehaviorManager.ENTITY: entity_ids}
        )

        return result

    def getending(self, entity_ids, behaviors, ts=None):
        """Get end date of corresponding behaviors if a timestamp is in a
        behavior period.

        :param entity_ids: entity id(s).
        :type entity_ids: list or str
        :param behaviors: behavior(s) to check at timestamp.
        :type behaviors: list or str
        :param long ts: timestamp to check. If None, use now.
        :return: depending on entity_ids and behaviors types:
            - behaviors:
                + str: behavior end timestamp.
                + array: dict of end timestamp by behavior.
            - entity_ids:
                + str: one end dates of behaviors if related entity is in
                    behavior at ts. None if entity ids is not in Storage.
                + list: set of (entity id: behaviors). If entity is not
                    registered in behavior state, no entry is added in the
                    result.
        :rtype: dict or long or NoneType
        """

        # initialize result
        result = {}

        # initialize ts
        if ts is None:
            ts = time()
        # calculate ts datetime
        dtts = datetime.fromtimestamp(ts)

        # get entity documents(s)
        documents = self.get(entity_ids=entity_ids)
        # check if one entity document is asked
        isunique = isinstance(entity_ids, basestring)

        if isunique:  # ensure documents is a list
            documents = [] if documents is None else [documents]

        # are many behaviors asked ?
        isbunique = isinstance(behaviors, basestring)

        # get sbehaviors such as a behaviors set
        if isbunique:
            sbehaviors = {behaviors}

        else:
            sbehaviors = set(behaviors)

        # check all pbehavior related to input ts
        for document in documents:
            values = document.get(PBehaviorManager.VALUES)
            behavior_result = self._get_ending(
                behaviors=sbehaviors, values=values, dtts=dtts
            )

            # update result only if behavior result
            if behavior_result:
                document_id = document[PBehaviorManager.ID]

                if isbunique:
                    result[document_id] = behavior_result[behaviors]

                else:
                    result[document_id] = behavior_result

        # update result is isunique
        if isunique:
            # convert result to a bool or None if entity_ids is str
            result = result[entity_ids] if entity_ids in result else None

        return result

    def whois(self, behaviors, ts=None):
        """Get entities which currently have specific behaviors.

        :param behaviors: behavior(s) to look for.
        :type behaviors: list or str

        :return: list of entities ids with the specified behaviors
        :rtype: list
        """

        result = []

        if ts is None:
            ts = time()

        # calculate ts datetime
        dtts = datetime.fromtimestamp(ts)

        documents = self[PBehaviorManager.PBEHAVIOR_STORAGE].find_elements({})

        if isinstance(behaviors, basestring):
            behaviors = [behaviors]

        len_behaviors = len(behaviors)

        for document in documents:
            values = document.get(PBehaviorManager.VALUES)
            ending = self._get_ending(
                behaviors=behaviors, values=values, dtts=dtts
            )
            if len(ending) != len_behaviors:
                document_id = document[PBehaviorManager.ID]
                result.append(document_id)

        return result

    def _get_ending(self, behaviors, values, dtts):
        """Get ending date of occured behavior(s) at a timestamp among value
        periods.

        :param set behaviors: behavior(s) to check.
        :param value: (list of) period(s) and behaviors.
        :type value: dict or list
        :param datetime dtts: date time moment.
        """

        result = {}

        if isinstance(values, dict):
            values = [values]

        for value in values:
            # get period
            period = value[PBehaviorManager.PERIOD]
            period = Event.from_ical(period)
            # get behaviors intersection
            dbehaviors = set(value[PBehaviorManager.BEHAVIORS])
            behaviors_to_check = behaviors & dbehaviors
            # if intersection contains elements
            for behavior in behaviors_to_check:
                # get duration, dtstart and rrule
                duration = period.get('duration')
                duration = duration.dt
                dtstart = period.get('dtstart')
                dtstart = dtstart.dt
                if isinstance(dtstart, datetime_time):
                    dtstart = datetime.now().replace(
                        hour=dtstart.hour, minute=dtstart.minute,
                        second=dtstart.second, tzinfo=dtstart.tzinfo
                    )
                rrule = period.get('rrule')
                rrule = rrulestr(rrule.to_ical(), cache=True, dtstart=dtstart)
                # calculate first date after dtts including dtts
                before = rrule.before(dt=dtts, inc=True)
                # if before datetime exist
                if before is not None:
                    # add duration
                    end = before + duration
                    # and check if dtstart is in [first; end]
                    if before <= dtts <= end:
                        # update end in the result
                        endts = timegm(end.timetuple())
                        result[behavior] = endts

        return result
