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

from unittest import TestCase, main
from canopsis.ccalendar.manager import CalendarManager
from uuid import uuid4

DEBUG = False


class CalendarManagerTest(TestCase):
    """
    Base class for all calendar manager tests.

    A event calendar is herited from a vevent,
    that is why this class is herited from
    VeventManagerTest
    """

    def setUp(self):
        """
        initialize a manager.
        """

        self.manager = CalendarManager()
        self.name = 'testcalendar'
        self.document_content = self.manager.get_document(
            category="1", output="test"
        )
        self.vevent_content = self.manager.get_vevent(
            self.document_content
        )

    def tearDown(self):
        pass

    def clean(self):
        self.manager.remove(self.ids)

    def get_calendar(self):
        return self.manager.find(ids=self.ids)


class CalendarTest(CalendarManagerTest):

    def test_get_document(self):
        print("ok for document", self.document_content)

    def test_get_document_properties(self):
        print(
            "ok for properties by doc",
            self.manager._get_document_properties(
                self.document_content
            )
        )

    def test_get_vevent(self):
        print("ok for vevent", self.vevent_content)

    def test_get_vevent_properties(self):
        print(
            "ok for properties by vevent",
            self.manager._get_vevent_properties(
                self.vevent_content
            )
        )

    def test_put(self):
        #self.clean() //TODO: test later and update code

        vevents = []
        vevents.append(self.vevent_content)

        self.manager.put(
            vevents
        )

    """def test_get(self):
        self.clean()

        self.manager.put(
            self.id,
            self.document_content
        )

        self.manager.put(
            self.id + '1',
            self.document_content
        )

        self.calendar_count_equals(1)

        result = self.manager.find()
        self.assertGreaterEqual(len(list(result)), 2)

        result = self.manager.find(limit=1)
        self.assertEqual(len(list(result)), 1)

    def test_remove(self):
        self.clean()

        self.calendar_count_equals(0)

        self.manager.put(
            self.id,
            self.document_content
        )

        self.calendar_count_equals(1)

        self.manager.remove(self.ids)

        self.calendar_count_equals(0)"""


if __name__ == '__main__':
    main()
