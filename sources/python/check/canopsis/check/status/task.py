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

"""Tasks which process entity status.
"""

from canopsis.context.manager import Context
from canopsis.task.core import register_task
from canopsis.check.manager import CheckManager
from canopsis.common.utils import singleton_per_scope
from canopsis.check.status.manager import (
    StatusManager, OFF, ONGOING, STEALTHY, FLAPPING
)

from time import time


def applycriticity(state_document, state, criticity=CheckManager.HARD):
    """Apply criticity on input state_documents with input state.

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
def process_supervision_status(
        event, statusmanager=None, context=None, **kwargs
):
    """Process supervision status related to an event.
    """

    if context is None:
        context = singleton_per_scope(Context)

    if statusmanager is None:  # initialiaze the statusmanager
        statusmanager = singleton_per_scope(StatusManager)

    # get entityid, state and status
    entity = context.get_entity(event)
    entityid = context.get_entity_id(entity)
    state = event[CheckManager.STATE]
    status = statusmanager.get_status(entityid=entityid)  # get status
    timestamp = event['timestamp']

    if status is None:  # if old event does not exist, init status

        status = {}
        _apply_simple_status(status=status, state=state)

    # get specific status task
    task = statusmanager.status_conf.task(status)

    if task is None:  # raise an error if no task founded
        raise StatusManager.Error(
            "No task found by {0} to process {1}.".format(statusmanager, event)
        )

    else:
        # process the right task
        new_status = task(
            state=state, timestamp=timestamp, status=status,
            statusmanager=statusmanager,
            **kwargs
        )
        # update status content
        update_status(
            state=state, status=new_status, timestamp=timestamp,
            statusmanager=statusmanager, **kwargs
        )
        # and save the status
        statusmanager.put_status(entityid=entityid, status=new_status)


def update_status(state, status, timestamp, statusmanager):
    """Update status content before storing it.
    """

    result = status

    if (not isinstance(result, dict)) or StatusManager.VALUE not in result:
        raise StatusManager.Error(
            'Wrong status type {0}. int, str or dict expected'.
            format(result)
        )

    # update timestamp
    result[StatusManager.TIMESTAMP] = timestamp

    # update state/last_state_change
    if StatusManager.STATE not in result:
        result[StatusManager.STATE] = state
        result[StatusManager.LAST_STATE_CHANGE] = timestamp

    elif state != result[StatusManager.STATE]:
        result[StatusManager.LAST_STATE_CHANGE] = timestamp

    return result


def _apply_simple_status(state, status):
    """Apply off (if state == 0) or ongoing (state != 0) status.

    :param int state: entity state.
    :param dict status: status properties.
    """

    status[StatusManager.VALUE] = OFF if state == 0 else ONGOING


@register_task('statusmanager.off')
def process_status_off(state, timestamp, status, statusmanager, **kwargs):
    """Process event where old status is off or does not exist and state is ok.

    :param dict status: current status to process.
    :param StatusManager statusmanager: statusmanager to use.
    :param float timestamp: current state timestamp.
    :param int state: current state.
    :return: new status.
    :rtype: dict
    """

    result = process_status_flapping(
        state=state, status=status, timestamp=timestamp,
        statusmanager=statusmanager,
        **kwargs
    )

    return result


@register_task('statusmanager.ongoing')
def process_status_ongoing(state, timestamp, status, statusmanager, **kwargs):
    """Process event where old status is ongoing or does not exist and state
    nok.

    :param dict status: current status to process.
    :param StatusManager statusmanager: statusmanager to use.
    :param float timestamp: current state timestamp.
    :param int state: current state.
    :return: new status.
    :rtype: dict
    """

    result = process_status_flapping(
        state=state, status=status, timestamp=timestamp,
        statusmanager=statusmanager,
        **kwargs
    )

    # do something if status can be stealthy
    if state == 0 and result[StatusManager.VALUE] != FLAPPING:

        oldtimestamp = result[StatusManager.TIMESTAMP]
        if timestamp - oldtimestamp <= statusmanager.stealthy_time:
            result[StatusManager.VALUE] = STEALTHY
            result[StatusManager.STEALTHY_TIME] = oldtimestamp

    return result


@register_task('statusmanager.stealthy')
def process_status_stealthy(status, state, timestamp, statusmanager, **kwargs):
    """Process event where old status is stealthy.

    :param dict status: current status to process.
    :param StatusManager statusmanager: statusmanager to use.
    :param float timestamp: current state timestamp.
    :param int state: current state.
    :return: new status.
    :rtype: dict
    """

    result = process_status_flapping(
        status=status, state=state, timestamp=timestamp,
        statusmanager=statusmanager,
        **kwargs
    )
    # if no flapping, check stealthy
    if result[StatusManager.VALUE] != FLAPPING:

        stealthy_time = status[StatusManager.STEALTHY_TIME]

        if (timestamp - stealthy_time) > statusmanager.stealthy_time:
            del status[StatusManager.STEALTHY_TIME]
            _apply_simple_status(state=state, status=status)

        else:
            status[StatusManager.VALUE] = STEALTHY

    return result


def _update_flapping(state, status, statusmanager, timestamp, **kwargs):
    """Update status flapping properties.
    """

    isflapping = StatusManager.FLAPPING_TIMES in status

    if isflapping:

        # remove elapsed flapping occurences
        flapping_times = status[StatusManager.FLAPPING_TIMES]
        archiver_flapping_time = statusmanager.flapping_time
        # update flapping times with not elapsed times
        flapping_times[:] = [
            ts for ts in flapping_times
            if (timestamp - ts) <= archiver_flapping_time
        ]
        # check len
        isflapping = len(flapping_times) >= statusmanager.flapping_freq

        if isflapping:  # apply flapping if enough flapping times
            status[StatusManager.VALUE] = FLAPPING

        elif not flapping_times:  # clean flapping times if empty
            del status[StatusManager.FLAPPING_TIMES]

    if not isflapping:  # apply simple status if not flapping
        _apply_simple_status(status=status, state=state)


@register_task('statusmanager.flapping')
def process_status_flapping(status, statusmanager, timestamp, state, **kwargs):
    """Process event where old status is flapping.

    :param dict status: current status to process.
    :param StatusManager statusmanager: statusmanager to use.
    :param float timestamp: current state timestamp.
    :param int state: current state.
    :return: new status.
    :rtype: dict
    """

    result = status

    # still in flapping ?
    flapping_times = status.setdefault(StatusManager.FLAPPING_TIMES, [])

    oldstate = status[StatusManager.STATE]

    if oldstate != state:  # add flapping occurence if new ocilation
        flapping_times.append(timestamp)

    _update_flapping(
        state=state, status=status, statusmanager=statusmanager,
        timestamp=timestamp,
        **kwargs
    )

    return result


@register_task('statusmanager.canceled')
def process_status_canceled(state, status, **kwargs):
    """Process event where old status is canceled.

    :param int state: current state.
    :return: new status.
    :rtype: dict
    """

    _apply_simple_status(state=state, status=status)

    return status


@register_task('statusmanager.beat_processing')
def beat_processing(publisher, statusmanager=None, **kwargs):
    """Clean expired status.

    :param StatusManager statusmanager: status manager.
    """

    timestamp = time()

    if statusmanager is None:
        statusmanager = singleton_per_scope(StatusManager)

    # get expired statuses
    statuses = statusmanager.find_statuses(expired=True)

    for status in statuses:
        # in case of flapping
        if status[StatusManager.VALUE] == FLAPPING:
            # update it in a consistent state
            _update_flapping(
                status=status, state=status[StatusManager.VALUE],
                timestamp=timestamp,
                statusmanager=statusmanager
            )
            statusmanager.put_status(status=status)

        else:
            # remove stealthy
            statusmanager.remove_status(status=status)
