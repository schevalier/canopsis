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

from canopsis.storage.core import Storage


class StorageTest(TestCase):
    """Test Storage.
    """

    class TestStorage(Storage):
        pass

    def setUp(self):

        self.storage = StorageTest.TestStorage()


class TestGetDirected(StorageTest):
    """Test _get_directed method.
    """

    def test_empty(self):
        """Test with an empty data.
        """

        data = []
        result = Storage._get_directed(data=data)
        self.assertFalse(result, [])

    def test_str(self):
        """Test with a str data.
        """

        data = 'test'
        result = Storage._get_directed(data=data)
        self.assertEqual(result, [(data, Storage.ASC)])

    def test_dict(self):
        """Test with an empty dict.
        """

        data = {}
        self.assertRaises(KeyError, Storage._get_directed, data)

    def test_dict_property(self):
        """Test a dict with a property.
        """

        data = {Storage.PROPERTY: 'test'}
        result = Storage._get_directed(data=data)
        self.assertEqual(result, [('test', Storage.ASC)])

    def test_dict_prop_dir(self):
        """Test a dict with both property and direction.
        """

        data = {Storage.PROPERTY: 'test', Storage.DIRECTION: Storage.DESC}
        result = Storage._get_directed(data=data)
        self.assertEqual(result, [('test', Storage.DESC)])

    def test_dict_prop_strdir(self):
        """Test a dict with property and named direction.
        """

        data = {Storage.PROPERTY: 'test', Storage.DIRECTION: 'DESC'}
        result = Storage._get_directed(data=data)
        self.assertEqual(result, [('test', Storage.DESC)])

    def test_tuple(self):
        """Test a tuple.
        """

        data = 'test', Storage.DESC
        result = Storage._get_directed(data=data)
        self.assertEqual(result, [('test', Storage.DESC)])

    def test_tuple_nameddir(self):
        """Test a tuple with a named direction.
        """

        data = 'test', 'DESC'
        result = Storage._get_directed(data=data)
        self.assertEqual(result, [('test', Storage.DESC)])

    def test_tuple_namedlowerdir(self):
        """Test a tuple with a named direction.
        """

        data = 'test', 'desc'
        result = Storage._get_directed(data=data)
        self.assertEqual(result, [('test', Storage.DESC)])

    def test_list(self):
        """Test a list with all kind of data.
        """

        data = [
            'test',
            {Storage.PROPERTY: 'test1'},
            {Storage.PROPERTY: 'test2', Storage.DIRECTION: Storage.DESC},
            {Storage.PROPERTY: 'test3', Storage.DIRECTION: 'DESC'},
            ('test4', Storage.DESC),
            ('test5', 'DESC')
        ]
        result_to_compare = [
            ('test', Storage.ASC),
            ('test1', Storage.ASC),
            ('test2', Storage.DESC),
            ('test3', Storage.DESC),
            ('test4', Storage.DESC),
            ('test5', Storage.DESC)
        ]
        result = Storage._get_directed(data=data)
        self.assertEqual(result, result_to_compare)


if __name__ == '__main__':
    main()
