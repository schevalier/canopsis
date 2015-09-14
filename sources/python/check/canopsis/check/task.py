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

from canopsis.context.manager import Context
from canopsis.check.manager import CheckManager
from canopsis.common.utils import singleton_per_scope
from canopsis.check.archiver import (
    Archiver, OFF, ONGOING, STEALTHY, FLAPPING, CANCELED
)

from copy import deepcopy

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

    if context is None:
        context = singleton_per_scope(Context)

    if archiver is None:  # initialiaze the archiver
        archiver = singleton_per_scope(Archiver)

    # get entityid, state and status
    entity = context.get_entity(event)
    entityid = context.get_entity_id(entity)
    state = event[CheckManager.STATE]
    status = archiver.get_status(entityid=entityid)  # get status

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
        new_status = task(state=state, status=status, archiver=archiver)
        # and save the status
        archiver.set_status(entityid=entityid, status=new_status)


@register_task('process_status_off')
def process_status_off(state=0, status=None, archiver=None, **kwargs):

    result = status

    if archiver is None:
        archiver = singleton_per_scope(Archiver)

    if state == 0:  # if state is ok twice, then final status is OFF
        result = OFF

    else:
        now = time()
        result.update(
            {
                'value': ONGOING,
                'state': state,
                'last_state_change': now,
                'timestamp': now
            }
        )

    return result


@register_task('archiver.ongoing')
def process_status_ongoing(state=0, status=None, archiver=None, **kwargs):

    result = status

    now = time()

    if archiver is None:
        archiver = singleton_per_scope(Archiver)

    if state == 0:
        ts = status['timestamp']
        if (now - ts) < archiver.stealthy_show:  # is stealthy ?
            result.update({
                'value': STEALTHY,
                'first_stealthy_time': now,
                'state': state
            })
        else:
            result = OFF

    return result


@register_task('archiver.stealthy')
def process_status_stealthy(state=0, status=None, archiver=None, **kwargs):

    result = status

    now = time()

    if archiver is None:
        archiver = singleton_per_scope(Archiver)

    ts = status['timestamp']
    if (now - ts) < archiver.stealthy_show:  # is stealthy ?
        result['state'] = state

    elif state == 0:  # OFF status
        result = OFF

    else:  # ongoing status
        result = {'value': ONGOING, 'state': state}

    return result


@register_task('archiver.flapping')
def process_status_flapping(state=0, status=None, archiver=None, **kwargs):

    result = status

    if archiver is None:
        archiver = singleton_per_scope(Archiver)

    freq = status.get('flapping_freq', 0)

    if freq > archiver.flapping_freq:
        if state == 0:
            result = OFF

        else:
            result = {'value': ONGOING, 'state': state}

    else:
        result['flapping_freq'] = freq + 1

    return result

@register_task('archiver.cancel')
def process_status_cancel(state=0, status=None, **kwargs):

    result = status

    result.update(
        {
            'state': state,
            'value': OFF if state == 0 else ONGOING
        }
    )

    return result
