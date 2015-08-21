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

"""This module provides a vevent manager.
"""

__all__ = ['VEventManager']

from canopsis.common.init import basestring
from canopsis.configuration.configurable.decorator import (
    conf_paths, add_category
)
from canopsis.middleware.registry import MiddlewareRegistry

from icalendar import Event

from calendar import timegm

from datetime import datetime, timedelta

from uuid import uuid4 as uuid

from time import time

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrulestr

from copy import deepcopy

MAXTS = 2147483647  #: maximal timestamp in 32bits
CONF_PATH = 'vevent/vevent.conf'
CATEGORY = 'VEVENT'


@add_category(CATEGORY)
@conf_paths(CONF_PATH)
class VEventManager(MiddlewareRegistry):
    """Manage virtual event data.

    Such vevent are technically an expression which respects the icalendar
    specification ftp://ftp.rfc-editor.org/in-notes/rfc2445.txt.

    A vevent document contains several values. Each value contains
    an icalendar expression (dtstart, rrule, duration) and an array of
    behavior entries:

    {
        uid: document id,
        source: source element id,
        dtstart: datetime start,
        dtend: datetime end,
        duration: vevent duration,
        freq: vevent freq,
        vevent: vevent ical format value,
        ... # specific properties
    }.
    """

    STORAGE = 'vevent_storage'  #: vevent storage name

    UID = 'uid'  #: document id
    SOURCE = 'source'  #: source field name
    DTSTART = 'dtstart'  #: dtstart field name
    DTEND = 'dtend'  #: dtend field name
    RRULE = 'rrule'  #: rrule vevent field name
    DURATION = 'duration'  #: duration field name

    SOURCE_TYPE = 'X-Canopsis-SourceType'  #: source type field name

    def __init__(self, vevent_storage=None, *args, **kwargs):
        """
        :param Storage vevent_storage: vevent storage.
        """
        super(VEventManager, self).__init__(*args, **kwargs)

        # set storage if given
        if vevent_storage is not None:
            self[VEventManager.STORAGE] = vevent_storage

    def _get_document_properties(self, document):
        """Get properties from a document.

        :param dict document: document from where get properties.
        :return: document properties in a dictionary.
        :rtype: dict
        """

        return {}

    def _get_vevent_properties(self, vevent):
        """Get information from a vevent.

        :param Event vevent: vevent from where get information.
        :return: vevent information in a dictionary.
        :rtype: dict
        """

        return {}

    @staticmethod
    def get_document(
            uid=None, source=None,
            duration=None, rrule=None, dtstart=0, dtend=None,
            **kwargs
    ):
        """Get a document related to input values.
        """

        result = kwargs

        if uid is None:
            uid = str(uuid())

        # ensure dtend and duration are consistents if rrule is None
        if rrule is None:
            if duration is None:
                if dtend is None:
                    dtend = MAXTS
                duration = dtend - dtstart

            elif dtend is None:
                datetimestart = datetime.utcfromtimestamp(dtstart)
                deltaduration = VEventManager._deserialize_duration(duration)
                datetimeend = datetimestart + deltaduration
                dtend = timegm(datetimeend.timetuple())

        result.update({
            VEventManager.UID: uid,
            VEventManager.SOURCE: source,
            VEventManager.DURATION: duration,
            VEventManager.RRULE: rrule,
            VEventManager.DTSTART: dtstart,
            VEventManager.DTEND: dtend
        })

        return result

    def get_vevent(self, document):
        """Get a vevent from a document.

        :param dict document: document to transform into an Event.
        :return: document vevent.
        :rtype: Event
        """

        # prepare vevent kwargs
        kwargs = self._get_document_properties(document=document)

        # get uid
        uid = document.get(VEventManager.UID)
        if uid:
            kwargs[VEventManager.UID] = uid

        # get source
        source = document.get(VEventManager.SOURCE)
        if source:
            kwargs[VEventManager.SOURCE_TYPE] = source

        # get dtstart
        dtstart = document[VEventManager.DTSTART]
        if dtstart:
            kwargs[VEventManager.DTSTART] = datetime.utcfromtimestamp(dtstart)

        # get dtend
        dtend = document[VEventManager.DTEND]
        if dtend:
            kwargs[VEventManager.DTEND] = datetime.utcfromtimestamp(dtend)

        # get duration
        duration = document[VEventManager.DURATION]
        if duration:
            deserialized_duration = VEventManager._deserialize_duration(
                duration
            )
            kwargs[VEventManager.DURATION] = deserialized_duration

        # get rrule
        rrule = document[VEventManager.RRULE]
        if rrule:
            kwargs[VEventManager.RRULE] = rrule

        result = Event(**kwargs)

        return result

    def get_by_uids(
            self, uids,
            limit=0, skip=0, sort=None, projection=None, with_count=False
    ):
        """Get documents by uid(s).

        :param uids: document uid(s).
        :type uids: str or list
        :param int limit: max number of elements to get.
        :param int skip: first element index among searched list.
        :param sort: contains a list of couples of field (name, ASC/DESC)
            or field name which denots an implicitelly ASC order.
        :type sort: list of {(str, {ASC, DESC}}), or str}
        :param dict projection: key names to keep from elements.
        :param bool with_count: If True (False by default), add count to the
            result.
        :return: document(s) corresponding to input uids. If uids is a string,
            result is a dict, otherwise result is a list. If with_count,
            result is the tuple (previous result, total number of documents).
        :rtype: dict or list or tuple
        """

        documents = self[VEventManager.STORAGE].get_elements(
            ids=uids,
            limit=limit, skip=skip, sort=sort, projection=projection,
            with_count=with_count
        )

        if with_count:
            result = list(documents[0]), documents[1]

        else:
            result = list(documents[0])

        return result

    def values(
            self, sources=None, dtstart=None, dtend=None, query=None,
            limit=0, skip=0, sort=None, projection=None, with_count=False
    ):
        """Get document values of source vevent(s).

        :param sources: source(s) from where get values. If None, use all
            sources.
        :type sources: str or list
        :param float dtstart: vevent dtstart (default 0).
        :param float dtend: vevent dtend (default sys.MAXTS).
        :param dict query: additional filtering query to apply in the search.
        :param int limit: max number of elements to get.
        :param int skip: first element index among searched list.
        :param sort: contains a list of couples of field (name, ASC/DESC)
            or field name which denots an implicitelly ASC order.
        :type sort: list of {(str, {ASC, DESC}}), or str}
        :param dict projection: key names to keep from elements.
        :param bool with_count: If True (False by default), add count to the
            result.
        :return: matchable documents.
        :rtype: list
        """

        result = {}  # default result is an empty dict

        # build query
        query = self._build_vevent_query(
            sources=sources,
            dtstart=dtstart,
            dtend=dtend,
            query=query
        )

        documents = self[VEventManager.STORAGE].find_elements(
            query=query,
            limit=limit, skip=skip, sort=sort, projection=projection,
            with_count=with_count
        )

        if with_count:
            result = list(documents[0]), documents[1]

        else:
            result = list(documents)

        return result

    def _build_vevent_query(
            self, sources=None, dtstart=None, dtend=None, query=None
    ):
        """Build a storage query related to input parameters.

        :param sources: query source(s).
        :type sources: str or list
        :param float dtstart: query dtstart.
        :param float dtend: query dtend.
        :param dict query: default query to use.
        """

        # initialize result
        result = deepcopy(query) if query else {}

        # put sources in query if necessary
        if sources is not None:
            if isinstance(sources, basestring):
                result[VEventManager.SOURCE] = {'$in': sources}

            else:
                result[VEventManager.SOURCE] = sources

        # put dtstart and dtend in result
        if dtstart is None:
            dtstart = 899909521

        if dtend is None:
            dtend = MAXTS

        result[VEventManager.DTSTART] = {'$lte': dtend}
        result[VEventManager.DTEND] = {'$gte': dtstart}

        return result

    def whois(self, sources=None, dtstart=None, dtend=None, query=None):
        """Get a set of sources which match with timed condition and query.

        :param list sources: sources from where get values. If None, use all
            sources.
        :param int dtstart: vevent dtstart (default 0).
        :param int dtend: vevent dtend (default sys.MAXTS).
        :param dict query: additional filtering query to apply in the search.
        :return: sources.
        :rtype: set
        """

        values = self.values(
            sources=sources, dtstart=dtstart, dtend=dtend, query=query
        )

        result = set([value[VEventManager.SOURCE] for value in values])

        return result

    @staticmethod
    def _deserialize_duration(sduration):
        """Deserialize input serialized duration.

        :param sduration: serialized duration.
        :type sduration: int or dict
        :return: duration.
        :rtype: relativedelta or timedelta
        """
        result = None

        if isinstance(sduration, dict):
            result = relativedelta(**sduration)

        else:
            result = timedelta(seconds=sduration)

        return result

    def _preparedoc(self, vevent, source=None):
        """Prepare a document related to input vevent and source.

        :param vevent: vevent to prepare before putting it in a storage.
        :type vevent: dict or Event or str
        :return: document to put.
        :rtype: dict
        """

        if isinstance(vevent, dict) and not isinstance(vevent, Event):

            result = VEventManager.get_document(**vevent)

        # if result has to be generated ...
        else:
            # ensure vevent is an ical format
            if isinstance(vevent, basestring):
                vevent = Event.from_ical(vevent)

            # prepare the result with specific properties
            result = self._get_vevent_properties(vevent=vevent)

            # get dtstart
            dtstart = vevent.get(VEventManager.DTSTART, 0)

            if isinstance(dtstart, datetime):
                dtstart = timegm(dtstart.timetuple())

            # get dtend
            dtend = vevent.get(VEventManager.DTEND, 0)
            if isinstance(dtend, datetime):
                dtend = timegm(dtend.timetuple())

            # get rrule
            rrule = vevent.get(VEventManager.RRULE)
            if rrule is not None:
                _rrule = ""
                for rrule_key in rrule:
                    rrule_value = rrule[rrule_key]
                    _rrule += "{0}={1};".format(rrule_key, rrule_value)
                rrule = _rrule

            # get duration
            duration = vevent.get(VEventManager.DURATION)
            if duration:
                if isinstance(duration, timedelta):
                    duration = duration.totalseconds()

                elif isinstance(duration, relativedelta):
                    duration = {
                        'years': duration.years,
                        'months': duration.months,
                        'days': duration.days,
                        'hours': duration.hours,
                        'minutes': duration.minutes,
                        'seconds': duration.seconds,
                        'microseconds': duration.microseconds
                    }

            # get uid
            uid = vevent.get(VEventManager.UID)
            if not uid:
                uid = str(uuid())

            # get source
            if not source:
                source = vevent.get(VEventManager.SOURCE_TYPE)

            # prepare the result
            newdoc = self.get_document(
                uid=uid, source=source, duration=duration, rrule=rrule,
                dtstart=dtstart, dtend=dtend
            )
            result.update(newdoc)

        return result

    def put(self, vevents, source=None, cache=False):
        """Add vevents (and optionally data) related to input source.

        :param str source: vevent source if not None.
        :param vevents: vevent(s) (document, str or ical vevent).
        :type vevents: dict, str, Event or list
        :param dict info: vevent info.
        :param bool cache: if True (default False), use storage cache.
        :return: new documents. Type is dict if vevents is not a list. List
            otherwise.
        :rtype: dict or list
        """

        result = []

        isunique = isinstance(vevents, (dict, str, Event))
        if isunique:
            vevents = [vevents]

        for vevent in vevents:

            document = self._preparedoc(vevent=vevent, source=source)

            uid = document[VEventManager.UID]

            self[VEventManager.STORAGE].update_elements(
                query=uid, setrule=document
            )

            # TODO: remove cause it is specific to mongo
            document['_id'] = uid

            result.append(document)

        # transform result if vevents is unique
        if isunique:
            result = result[0] if result else None

        return result

    def remove(self, uids=None, query=None, cache=False):
        """Remove elements from storage where uids are given.

        :param uids: document uid(s) to remove from storage
            (default all empty storage documents). If None, remove all
            documents.
        :type uids: str or list
        :param dict query: additional deletion query.
        :return: removed document id(s). str if uids is a string, list
            otherwise.
        :rtype: str or list
        """

        result = self[VEventManager.STORAGE].remove_elements(
            ids=uids, cache=cache, _filter=query
        )

        return result

    def remove_by_source(self, sources=None, query=None, cache=False):
        """Remove vevent documents related to input sources.

        :param sources: source(s) from where remove related vevent
            documents. Remove all documents if None.
        :type sources: str or list
        :param dict query: additional deletion query.
        :return: removed document id(s) in the same type of sources, or list
            if sources is None.
        :rtype: str or list
        """

        _filter = {} if query is None else query

        if sources is not None:
            if isinstance(sources, basestring):
                _filter[VEventManager.SOURCE] = sources
            else:
                _filter[VEventManager.SOURCE] = {'$in': sources}

        result = self[VEventManager.STORAGE].remove_elements(
            _filter=_filter, cache=cache
        )

        return result

    def get_periods(self, sources, ts=None, query=None):
        """Get couple(s) of (start, end) timestamps around an input ts
        with given source, or None if no period exists with input source and
        timestamp.

        :param sources: source id(s).
        :type sources: str or list
        :param float ts: timestamp to check. If None, use now.
        :param dict query: additional vevent document query.
        :return: depending of type of sources:
            - str: tuple of (start, end) timestamps including ts, or None if ts
            is not in a vevent document period.
            - list:
        :rtype: tuple or dict
        """

        result = {}

        if ts is None:  # initialize ts
            ts = time()

        dtts = datetime.fromtimestamp(ts)  # get the right ts datetime

        # check unicity of sources
        isunique = isinstance(sources, basestring)
        if isunique:
            sources = [sources]

        # get documents
        documents = self.values(
            sources=sources,
            dtstart=ts,
            dtend=ts,
            query=query
        )

        # iterate on documents in order to update result with end ts
        for document in documents:
            period = VEventManager.get_period(
                document=document, ts=ts, dtts=dtts
            )

            source = document[VEventManager.SOURCE]

            # put period in result
            if period is not None:
                result[source] = period

        # update result if isunique
        if isunique:
            result = result[sources[0]] if result else None

        return result

    @staticmethod
    def get_period(document, ts=None, dtts=None):
        """Get tuple of document (dtstart, dtend) related to document
        properties.

        :param dict document: document from whose get period.
        :param float ts: moment from where find the around period.
        :return: document period or None if no period in document.
        :rtype: tuple or NoneType
        """

        result = None  # default result

        if ts is None:
            ts = time()
            dtts = datetime.fromtimestamp(ts)

        elif dtts is None:
            dtts = datetime.fromtimestamp(ts)

        # prepare end ts to update in result
        duration = document.get(VEventManager.DURATION)
        rrule = document.get(VEventManager.RRULE)
        dtstart = document.get(VEventManager.DTSTART, 0)
        datetimestart = datetime.fromtimestamp(dtstart)
        dtend = document.get(VEventManager.DTEND, MAXTS)
        datetimeend = datetime.fromtimestamp(dtend)

        # get the right dtend if duration exists
        if duration:
            duration = VEventManager._deserialize_duration(sduration=duration)
            # add duration on datetimeend
            datetimeend = min(datetimestart + duration, datetimeend)
            dtend = timegm(datetimeend.timetuple())

        # in case of rrule, get the right dtstart and dtend
        rrule = document.get(VEventManager.RRULE)
        if rrule:
            rrule = rrulestr(rrule)
            before = rrule.before(dtts=ts, inc=True)

            if before:
                dtstart = timegm(before.timetuple())
                datetimeend = before

                if duration:  # add duration
                    datetimeend += duration
                    dtend = min(dtend, timegm(datetimeend.timetuple()))

                if datetimeend >= dtts:  # check if datetimeend >= than dtts
                    dtstart = timegm(datetimestart.timetuple())
                    result = dtstart, dtend

        else:  # otherwise, set result such as the couple of dtstart, dtend
            result = dtstart, dtend

        return result
