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

"""decorators unit tests.
"""

from unittest import main, TestCase
from canopsis.common.decorators import deprecated
from logging import Logger


class DeprecatedTest(TestCase):
    """Test the decorator deprecated.
    """

    class LoggerMock(Logger):
        """Logger Mock.
        """

        def __init__(self, *args, **kwargs):

            super(DeprecatedTest.LoggerMock, self).__init__(
                name='test', *args, **kwargs
            )

            self.msg = None

        def warning(self, msg):
            """log the warning message in setting to this the input msg.
            :param str msg: message to set to this.
            """

            self.msg = msg

    class Loggeable(object):
        """Class with logger.

        This logger is its ``logger`` attribute.
        """

        def __init__(self):

            super(DeprecatedTest.Loggeable, self).__init__()

            self.logger = DeprecatedTest.LoggerMock()

        @deprecated(start='test')
        def test(self, *args, **kwargs):
            """Empty test.
            """

    def setUp(self):

        self.start = 'test'

    def test_nologger(self):
        """Test to depreciate a function without logger.
        """

        @deprecated(start=self.start)
        def func():
            """Test function
            """

        self.assertRaises(RuntimeError, func)

    def test_loggermock(self):
        """Test to depreciate a function with a logger.
        """

        logger = DeprecatedTest.LoggerMock()

        @deprecated(start=self.start, logger=logger)
        def func():
            """Test function.
            """

        self.assertIsNone(logger.msg)

        func()

        self.assertIsNotNone(logger.msg)

    def test_classwithlogger(self):
        """Test to depreciate a method.
        """

        instance = DeprecatedTest.Loggeable()

        self.assertIsNone(instance.logger.msg)

        instance.test()

        self.assertIsNotNone(instance.logger.msg)

    def test_args(self):
        """Test to log a message from a logger in varargs.
        """

        logger = DeprecatedTest.LoggerMock()

        @deprecated(start=self.start)
        def func(*args):
            """Test function.
            """

        self.assertIsNone(logger.msg)

        func(self.start, logger, self.start)

        self.assertIsNotNone(logger.msg)

    def test_kwargs(self):
        """Test to log a message from a logger in keywords.
        """

        logger = DeprecatedTest.LoggerMock()

        @deprecated(start=self.start)
        def func(**kwargs):
            """Test function.
            """

        self.assertIsNone(logger.msg)

        func(a=self.start, b=logger, c=self.start)

        self.assertIsNotNone(logger.msg)

    def test_order(self):
        """Test to log messages related to order of appareance of a logger from
        the instance, and arguments.
        """

        baselogger = DeprecatedTest.LoggerMock()
        instance = DeprecatedTest.Loggeable()
        argslogger = DeprecatedTest.LoggerMock()
        kwargslogger = DeprecatedTest.LoggerMock()

        def initloggers():
            """Init loggers.
            """

            baselogger.msg = None
            instance.logger.msg = None
            argslogger.msg = None
            kwargslogger.msg = None

        self.assertIsNone(baselogger.msg)
        self.assertIsNone(instance.logger.msg)
        self.assertIsNone(argslogger.msg)
        self.assertIsNone(kwargslogger.msg)

        @deprecated(start=self.start, logger=baselogger)
        def func_with_logger(*args, **kwargs):
            """Test function.
            """

        func_with_logger(argslogger, a=kwargslogger)

        self.assertIsNotNone(baselogger.msg)
        self.assertIsNone(instance.logger.msg)
        self.assertIsNone(argslogger.msg)
        self.assertIsNone(kwargslogger.msg)

        @deprecated(start=self.start)
        def func(*args, **kwargs):
            """Test function.
            """

        initloggers()

        func(argslogger, a=kwargslogger)

        self.assertIsNone(baselogger.msg)
        self.assertIsNone(instance.logger.msg)
        self.assertIsNotNone(argslogger.msg)
        self.assertIsNone(kwargslogger.msg)

        initloggers()

        func(argslogger, logger=kwargslogger)

        self.assertIsNone(baselogger.msg)
        self.assertIsNone(instance.logger.msg)
        self.assertIsNone(argslogger.msg)
        self.assertIsNotNone(kwargslogger.msg)

        initloggers()

        self.assertRaises(RuntimeError, func)

        self.assertIsNone(baselogger.msg)
        self.assertIsNone(instance.logger.msg)
        self.assertIsNone(argslogger.msg)
        self.assertIsNone(kwargslogger.msg)

        initloggers()

        instance.test(argslogger, logger=kwargslogger)

        self.assertIsNone(baselogger.msg)
        self.assertIsNotNone(instance.logger.msg)
        self.assertIsNone(argslogger.msg)
        self.assertIsNone(kwargslogger.msg)


if __name__ == '__main__':
    main()
