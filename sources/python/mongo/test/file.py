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

"""Test the MongoFileStorage."""

from unittest import TestCase, main

from canopsis.mongo.file import MongoFileStorage
from pymongo import version as pymongov
from time import sleep


class MongoFileStorageTest(TestCase):
    """Test MongoFileStream."""

    def setUp(self):

        self.testfile = 'test'
        self.mfs = MongoFileStorage(data_scope=self.testfile)

    def tearDown(self):

        self.mfs.delete()
        sleep(1)

    def test_list(self):
        """Test to list files."""

        names = set([str(i) for i in range(5)])

        for name in names:
            self.mfs.new_file(name=name).close()

        filenames = set(self.mfs.list())

        self.assertEqual(filenames, names)

    def test_notexists(self):
        """Test if a filestream does not exist."""

        exists = self.mfs.exists(name=self.testfile)

        self.assertFalse(exists)

        mfs = self.mfs.get(name=self.testfile)

        self.assertIsNone(mfs)

        fss = list(self.mfs.find(names=[self.testfile]))

        self.assertFalse(fss)

        fss = list(self.mfs.find())

        self.assertFalse(fss)

    def test_newfile(self):
        """Test if a filestream does not exist."""

        mfs = self.mfs.new_file(name=self.testfile)

        exists = self.mfs.exists(name=self.testfile)

        self.assertFalse(exists)

        mfs.close()

        exists = self.mfs.exists(name=self.testfile)

        self.assertTrue(exists)

        fs1 = self.mfs.get(name=self.testfile)

        self.assertEqual(mfs, fs1)

        self.mfs.delete(names=self.testfile)

        exists = self.mfs.exists(name=self.testfile)

        self.assertFalse(exists)

    def _create_filestream(self):
        """Create a filestream.

        :return: newly created file stream.
        :rtype: canopsis.storage.file.FileStream
        """

        result = self.mfs.new_file(name=self.testfile)

        result.close()

        return result

    def test_putr(self):
        """Test to put and read data."""

        if pymongov >= '3':
            self.mfs.put(name=self.testfile, data=self.testfile)

            mfs = self.mfs.get(name=self.testfile)

            data = mfs.read(size=2)

            self.assertEqual(self.testfile[:2], data)

            data = mfs.read(size=-1)

            self.assertEqual(self.testfile[2:], data)

    def test_writer(self):
        """Test to write and read data."""

        mfs = self.mfs.new_file(name=self.testfile)

        mfs.write(data=self.testfile)

        mfs.close()

        mfs = self.mfs.get(name=self.testfile)

        data = mfs.read(size=2)

        self.assertEqual(self.testfile[:2], data)

        data = mfs.read(size=-1)

        self.assertEqual(self.testfile[2:], data)

    def test_pos(self):
        """Test file position only with pymongo3+."""

        if pymongov >= '3':

            mfs = self._create_filestream()

            pos = mfs.pos()

            self.assertEqual(pos, 0)

            self.assertRaises(Exception, mfs.seek, 2)

if __name__ == '__main__':
    main()
