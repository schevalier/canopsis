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
from canopsis.context.manager import Context
from canopsis.task.core import register_task
from canopsis.check.manager import CheckManager
from canopsis.common.utils import singleton_per_scope
from canopsis.check.archiver import Archiver, OFF, ONGOING, STEALTHY, FLAPPING

from time import time


def criticity(state_document, state, criticity=CheckManager.HARD):
    """
    Apply criticity on input state_documents with input state.

    :param dict state_document: state document to process.
    :param int state: state to apply on input state document.
    :param int criticity: criticity of state to update.
    :return: state document.
    :rtype: dict
    """

    state_name = CheckManager.STATE
    last_name = CheckManager.LAST_STATE
    count_name = CheckManager.COUNT
    # get criticity count by criticity level
    criticity_count = CheckManager.CRITICITY_COUNT[criticity]
    # by default, result is a copy of state_document
    result = state_document.copy()
    # if state document does not contain state information
    if state_name not in state_document:
        result.update({
            state_name: state,
            last_name: state,
            count_name: 1
        })
    else:
        # get current entity state
        entity_state = state_document[state_name]
        # if state != entity_state
        if state != entity_state:
            # get count and last state
            last_state = state_document[last_name]
            count = state_document[count_name]
            if last_state != state:  # if state != last state
                count = 1  # initialize count
                last_state = state
            else:  # else increment count
                count += 1
            # if state count is equal or greater than crit count
            if count >= criticity_count:
                count = 1  # initialize count
                entity_state = state  # state entity is state
            # construct a new document with state, count and last state
            result.update({
                state_name: entity_state,
                count_name: count,
                last_name: last_state
            })
    return result


@register_task('process_supervision_status')
def process_supervision_status(event, archiver=None, context=None, **kwargs):
    """Process supervision status related to an event.
    """

    if context is None:
        context = singleton_per_scope(Context)

    if archiver is None:  # initialiaze the archiver
        archiver = singleton_per_scope(Archiver)

    # get entityid, state and status
    entity = context.get_entity(event)
    entityid = context.get_entity_id(entity)
    state = event[CheckManager.STATE]
    status = archiver.get_status(entityid=entityid)  # get status
    timestamp = event['timestamp']

    task = None  # task to run

    if status is None:  # if old event does not exist

        if state == 0:
            task = archiver.status_conf.task('off')

        else:
            task = archiver.status_conf.task('ongoing')

    else:  # process specific devent status
        task = archiver.status_conf.task(status)

    if task is None:  # raise an error if no task founded
        raise Archiver.Error(
            "No task found by {0} to process {1}.".format(archiver, event)
        )

    else:
        # process the right task
        new_status = task(
            state=state, timestamp=timestamp, status=status, archiver=archiver
        )
        # update status content
        update_status(
            state=state, status=new_status, timestamp=timestamp,
            archiver=archiver
        )
        # and save the status
        archiver.set_status(entityid=entityid, status=new_status)


def update_status(state, status, timestamp, archiver):
    """Update status content before storing it.
    """

    result = status

    # ensure status is a dictionary
    if isinstance(status, basestring):
        result = {Archiver.VALUE: archiver.status_conf.value(status)}
    elif isinstance(status, int):
        result = {Archiver.VALUE: status}

    if (not isinstance(result, dict)) or Archiver.VALUE not in result:
        raise Archiver.Error(
            'Wrong status type {0}. int, str or dict expected'.
            format(result)
        )

    # update timestamp
    result[Archiver.TIMESTAMP] = timestamp

    # update state/last_state_change
    if Archiver.STATE not in result:
        result[Archiver.STATE] = state

    elif state != result[Archiver.STATE]:
        result[Archiver.LAST_STATE_CHANGE] = timestamp

    return result


@register_task('archiver.off')
def process_status_off(
        state=0, timestamp=None, status=None, archiver=None, **kwargs
):
    """Process event where old status is off or does not exist and state is ok.
    """

    result = status

    if archiver is None:
        archiver = singleton_per_scope(Archiver)

    if state == 0:  # if state is ok twice, then final status is OFF
        result = OFF

    else:
        result[Archiver.VALUE] = ONGOING
        result[Archiver.STATE] = state

    return result


@register_task('archiver.ongoing')
def process_status_ongoing(
        state=0, timestamp=None, status=None, archiver=None, **kwargs
):
    """Process event where old status is ongoing or does not exist and state
    nok.
    """

    result = status

    if archiver is None:
        archiver = singleton_per_scope(Archiver)

    if timestamp is None:  # init timestamp
        timestamp = time()

    if state == 0:  # do something only if state is ok

        # if flapping is not setted, do it
        if Archiver.FLAPPING_FREQ not in status:
            status[Archiver.FLAPPING_FREQ] = 1

        # set pending time
        if Archiver.PENDING_TIME not in status:
            status[Archiver.PENDING_TIME] = timestamp

        # get pending duration
        pending_duration = timestamp - status[Archiver.PENDING_TIME]

        if pending_duration < archiver.stealthy_time:  # is stealthy ?
            result[Archiver.VALUE] = STEALTHY

        elif pending_duration < archiver.flapping_time:  # is flapping ?
            flapping_freq = status.get(Archiver.FLAPPING_FREQ, 1)

            if flapping_freq >= archiver.flapping_freq:
                result[Archiver.VALUE] = FLAPPING

            else:  # increment flapping frequency and change to a stable status
                status[Archiver.FLAPPING_FREQ] = flapping_freq + 1
                status[Archiver.VALUE] = OFF

        else:  # come back to a stable status
            status[Archiver.VALUE] = OFF

    return result


@register_task('archiver.stealthy')
def process_status_stealthy(
        status, state=0, timestamp=None, archiver=None, **kwargs
):
    """Process event where old status is stealthy.
    """

    result = status

    if timestamp is None:
        timestamp = time()

    if archiver is None:
        archiver = singleton_per_scope(Archiver)

    pending_time = status[Archiver.PENDING_TIME]
    pending_duration = timestamp - pending_time

    if (
            pending_duration > archiver.stealthy_time or
            state == status[Archiver.STATE]
    ):  # is not in stealthy ?
        result[Archiver.VALUE] = OFF if state == 0 else ONGOING

    elif pending_duration < archiver.flapping_time:  # is flapping ?

        flapping_freq = status.get(Archiver.FLAPPING_FREQ, 0)
        if flapping_freq > archiver.flapping_freq:
            result[Archiver.VALUE] = FLAPPING

        else:
            result[Archiver.FLAPPING_FREQ] = flapping_freq + 1

    return result


@register_task('archiver.flapping')
def process_status_flapping(state=0, status=None, archiver=None, **kwargs):
    """Process event where old status is flapping.
    """

    result = status

    if archiver is None:
        archiver = singleton_per_scope(Archiver)

    pending_time = status[Archiver.PENDING_TIME]
    old_state = status[Archiver.STATE]

    if (
            pending_time > archiver.flapping_time or
            state == old_state
    ):
        status[Archiver.VALUE] = OFF if state == 0 else ONGOING

    return result


@register_task('archiver.canceled')
def process_status_canceled(state=0, status=None, **kwargs):
    """Process event where old status is canceled.
    """

    result = OFF if state == 0 else ONGOING

    return result
