#!/usr/bin/env python
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

"""canopsis.check.status.conf UTs.
"""

from unittest import TestCase, main

from random import randint

from canopsis.common.utils import path
from canopsis.check.status.conf import StatusConfiguration


class TestStatusConfiguration(TestCase):
    """Test the StatusConfiguration object.
    """

    def setUp(self):

        self.value = randint(-100, 100)
        self.name = '{0}'.format(self.value)
        self.status_conf = StatusConfiguration(
            {
                self.name: {
                    StatusConfiguration.CODE: self.value,
                    StatusConfiguration.TASK: path(TestStatusConfiguration)
                }
            }
        )

    def test_value(self):
        """Test the value method.
        """

        value = self.status_conf.value(self.name)

        self.assertEqual(value, self.value)

    def test_unknownvalue(self):
        """Test with an unknown name.
        """

        self.assertRaises(
            StatusConfiguration.Error,
            self.status_conf.value, TestStatusConfiguration.__name__
        )

    def test_name(self):
        """Test with a known name.
        """

        name = self.status_conf.name(self.value)

        self.assertEqual(name, self.name)

    def test_unknownname(self):
        """Test with an unknown value.
        """

        self.assertRaises(
            StatusConfiguration.Error, self.status_conf.name, self.value + 1
        )

    def test_task_by_name(self):
        """Test wit a known task by name.
        """

        task = self.status_conf.task(self.name)

        self.assertEqual(task, TestStatusConfiguration)

    def test_task_by_value(self):
        """Test wit a known task by value.
        """

        task = self.status_conf.task(self.value)

        self.assertEqual(task, TestStatusConfiguration)

    def test_task_by_dict(self):
        """Test wit a known task by dict.
        """

        status = {StatusConfiguration.CODE: self.value}

        task = self.status_conf.task(status)

        self.assertEqual(task, TestStatusConfiguration)

    def test_unknowntask_by_name(self):
        """Test wit an unknown task by name.
        """

        self.assertRaises(
            StatusConfiguration.Error,
            self.status_conf.task, TestStatusConfiguration.__name__
        )

    def test_unknowntask_by_value(self):
        """Test wit an unknown task by value.
        """

        self.assertRaises(
            StatusConfiguration.Error, self.status_conf.task, self.value + 1
        )

    def test_unknowntask_by_dict(self):
        """Test wit an unknown task by dict.
        """

        status = {StatusConfiguration.CODE: self.value + 1}

        self.assertRaises(
            StatusConfiguration.Error, self.status_conf.task, status
        )

if __name__ == "__main__":
    main()
