#!/usr/bin/env python
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

"""VEventManager UTs.
"""

from unittest import TestCase, main

from canopsis.vevent.manager import VEventManager, MAXTS
from calendar import timegm
from datetime import datetime


class VeventManagerTest(TestCase):
    """Test the VEventManager.
    """

    def setUp(self):

        self.manager = VEventManager(db='test')

    def tearDown(self):

        self.manager.remove()

    def test_manager_get_document_properties(self):
        """Test the getter on document properties.

        The method _get_document_properties has
        to return a dict.
        """

        vevent_manager = VEventManager()
        result = vevent_manager._get_document_properties(2)
        self.assertIsInstance(result, dict)

    def test_manager_get_vevent_properties(self):
        """Test the getter on document properties.

        The method _get_document_properties has
        to return a dict.
        """

        vevent_manager = VEventManager()
        result = vevent_manager._get_vevent_properties(2)
        self.assertIsInstance(result, dict)


class GetDocumentTest(TestCase):

    def test_default(self):
        """Test default document creation.
        """

        document0 = VEventManager.get_document()
        document1 = VEventManager.get_document()

        # ensures uid are different
        self.assertNotEqual(
            document0[VEventManager.UID],
            document1[VEventManager.UID],
            'uid {0} and {1} are equals'.format(
                document0[VEventManager.UID], document1[VEventManager.UID]
            )
        )

        # assert sources are None
        self.assertEqual(
            (
                document0[VEventManager.SOURCE],
                document1[VEventManager.SOURCE]
            ), (None, None)
        )

        # assert durations are MAXTS
        self.assertEqual(
            (
                document0[VEventManager.DURATION],
                document1[VEventManager.DURATION]
            ), (MAXTS, MAXTS)
        )

        # assert dtstarts are 0
        self.assertEqual(
            (
                document0[VEventManager.DTSTART],
                document1[VEventManager.DTSTART]
            ), (0, 0)
        )

        # assert dtends are MAXTS
        self.assertEqual(
            (
                document0[VEventManager.DTEND],
                document1[VEventManager.DTEND]
            ), (MAXTS, MAXTS)
        )

        # assert rrules are None
        self.assertEqual(
            (
                document0[VEventManager.RRULE],
                document1[VEventManager.RRULE]
            ), (None, None)
        )

    def test_uid(self):
        """Test with a given uid.
        """

        uid = 'test'

        document = VEventManager.get_document(uid=uid)

        self.assertEqual(document[VEventManager.UID], uid)

    def test_dtend(self):
        """Test with a given dtend.
        """

        dtstart = 1
        dtend = 10

        document = VEventManager.get_document(dtend=dtend, dtstart=dtstart)

        self.assertEqual(document[VEventManager.DTEND], dtend)
        self.assertEqual(document[VEventManager.DTSTART], dtstart)
        self.assertEqual(document[VEventManager.DURATION], dtend - dtstart)

    def test_duration(self):
        """Test with a given duration.
        """

        dtstart = 1
        duration = 10

        document = VEventManager.get_document(
            duration=duration, dtstart=dtstart
        )

        self.assertEqual(document[VEventManager.DURATION], duration)
        self.assertEqual(document[VEventManager.DTSTART], dtstart)
        self.assertEqual(document[VEventManager.DTEND], dtstart + duration)

    def test_rrule(self):
        """Test with a given rrule.
        """

        rrule = 'freq=daily'

        document = VEventManager.get_document(rrule=rrule)

        self.assertEqual(rrule, document[VEventManager.RRULE])

    def test_source(self):
        """Test with a given source.
        """

        source = 'source'

        document = VEventManager.get_document(source=source)

        self.assertEqual(source, document[VEventManager.SOURCE])


class GetVeventTest(TestCase):

    def setUp(self):

        self.manager = VEventManager(db='test')

    def test_default(self):
        """Test default document creation.
        """

        document0 = VEventManager.get_document()
        document1 = VEventManager.get_document()

        vevent0 = self.manager.get_vevent(document=document0)
        vevent1 = self.manager.get_vevent(document=document1)

        # ensures uid are different
        self.assertNotEqual(
            vevent0[VEventManager.UID],
            vevent1[VEventManager.UID],
            'uid {0} and {1} are equals'.format(
                vevent0, vevent1
            )
        )

        # assert sources are None
        self.assertNotIn(VEventManager.SOURCE, vevent0)
        self.assertNotIn(VEventManager.SOURCE, vevent1)

        # assert durations are MAXTS
        self.assertEqual(
            (
                vevent0[VEventManager.DURATION].total_seconds(),
                vevent1[VEventManager.DURATION].total_seconds()
            ),
            (MAXTS, MAXTS)
        )

        # assert dtstarts are 0
        self.assertNotIn(VEventManager.DTSTART, vevent0)
        self.assertNotIn(VEventManager.DTSTART, vevent1)

        # assert dtends are MAXTS
        self.assertEqual(
            (
                timegm(vevent0[VEventManager.DTEND].timetuple()),
                timegm(vevent1[VEventManager.DTEND].timetuple())
            ), (MAXTS, MAXTS)
        )

        # assert rrules are None
        self.assertNotIn(VEventManager.RRULE, vevent0)
        self.assertNotIn(VEventManager.RRULE, vevent1)

    def test_uid(self):
        """Test with a given uid.
        """

        uid = 'test'

        document = VEventManager.get_document(uid=uid)

        vevent = self.manager.get_vevent(document=document)

        self.assertEqual(vevent[VEventManager.UID], uid)

    def test_dtend(self):
        """Test with a given dtend.
        """

        dtstart = 1
        dtend = 10

        document = VEventManager.get_document(dtend=dtend, dtstart=dtstart)

        vevent = self.manager.get_vevent(document=document)

        self.assertEqual(
            vevent[VEventManager.DTEND],
            datetime.utcfromtimestamp(dtend)
        )
        self.assertEqual(
            vevent[VEventManager.DTSTART], datetime.utcfromtimestamp(dtstart)
        )
        self.assertEqual(
            vevent[VEventManager.DURATION].total_seconds(), dtend - dtstart
        )

    def test_duration(self):
        """Test with a given duration.
        """

        dtstart = 1
        duration = 10

        document = VEventManager.get_document(
            duration=duration, dtstart=dtstart
        )
        vevent = self.manager.get_vevent(document=document)

        self.assertEqual(
            vevent[VEventManager.DTEND],
            datetime.utcfromtimestamp(dtstart + duration)
        )
        self.assertEqual(
            vevent[VEventManager.DTSTART], datetime.utcfromtimestamp(dtstart)
        )
        self.assertEqual(
            vevent[VEventManager.DURATION].total_seconds(), duration
        )

    def test_rrule(self):
        """Test with a given rrule.
        """

        rrule = "freq=daily"

        document = VEventManager.get_document(rrule=rrule)
        vevent = self.manager.get_vevent(document=document)

        self.assertEqual(rrule, vevent[VEventManager.RRULE])

    def test_source(self):
        """Test with a given source.
        """

        source = "source"

        document = VEventManager.get_document(source=source)
        vevent = self.manager.get_vevent(document=document)

        self.assertEqual(source, vevent[VEventManager.SOURCE_TYPE])

if __name__ == '__main__':
    main()
