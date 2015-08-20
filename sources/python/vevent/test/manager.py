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


class VeventManagerTest(TestCase):
    """Test the VEventManager.
    """

    def setUp(self):

        self.manager = VEventManager(data_scope='test')

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
            document0['uid'],
            document1['uid'],
            'uid {0} and {1} are equals'.format(
                document0['uid'], document1['uid']
            )
        )

        # assert sources are None
        self.assertEqual(
            (document0['source'], document1['source']), (None, None)
        )

        # assert durations are MAXTS
        self.assertEqual(
            (document0['duration'], document1['duration']), (MAXTS, MAXTS)
        )

        # assert dtstarts are 0
        self.assertEqual((document0['dtstart'], document1['dtstart']), (0, 0))

        # assert dtends are MAXTS
        self.assertEqual(
            (document0['dtend'], document1['dtend']), (MAXTS, MAXTS)
        )

        # assert rrules are None
        self.assertEqual(
            (document0['rrule'], document1['rrule']), (None, None)
        )

    def test_uid(self):
        """Test with a given uid.
        """

        uid = 'test'

        document = VEventManager.get_document(uid=uid)

        self.assertEqual(document['uid'], uid)

    def test_dtend(self):
        """Test with a given dtend.
        """

        dtstart = 1
        dtend = 10

        document = VEventManager.get_document(dtend=dtend, dtstart=dtstart)

        self.assertEqual(document['dtend'], dtend)
        self.assertEqual(document['dtstart'], dtstart)
        self.assertEqual(document['duration'], dtend - dtstart)

    def test_duration(self):
        """Test with a given duration.
        """

        dtstart = 1
        duration = 10

        document = VEventManager.get_document(
            duration=duration, dtstart=dtstart
        )

        self.assertEqual(document['duration'], duration)
        self.assertEqual(document['dtstart'], dtstart)
        self.assertEqual(document['dtend'], dtstart + duration)

    def test_rrule(self):
        """Test with a given rrule.
        """

        rrule = ""

        document = VEventManager.get_document(rrule=rrule)

        self.assertEqual(rrule, document['rrule'])


if __name__ == '__main__':
    main()
