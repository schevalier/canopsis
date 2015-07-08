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

from canopsis.vevent.manager import VEventManager


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

    def test_values(self):
        """test the values method.
        """

if __name__ == '__main__':
    main()
