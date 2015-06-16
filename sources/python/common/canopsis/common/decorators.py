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

"""Define a set of decorators useful to enrich the canopsis runtime.
"""

__all__ = ['deprecated']

from functools import wraps

from logging import Logger


def _findlogger(func, args, kwargs):
    """Find a logger from a or func call arguments.

    :param func: function from where find a logger.
    :param tuple args: vargargs from where find a logger.
    :param dict kwargs: kwargs from where find a logger.
    :return: first logger found from (in the order):

        - func.__this__.logger
        - kwargs['logger']
        - args.
        - kwargs.
    :rtype: Logger
    """

    # initialize the result
    result = None
    # find a logger from func instance if func is a method
    func_name = func.__name__
    if args:
        instance = args[0]
        method = getattr(instance, func_name, None)
        if getattr(method, '__self__', None) is instance:
            result = getattr(instance, 'logger', None)

    if result is None:
        if 'logger' in kwargs:
            logger = kwargs['logger']
            if isinstance(logger, Logger):
                result = logger
        else:
            for arg in args:
                if isinstance(arg, Logger):
                    result = arg
                    break
            else:
                for key in kwargs:
                    value = kwargs[key]
                    if isinstance(value, Logger):
                        result = value
                        break

    return result


def deprecated(start, reason=None, logger=None):
    """Depreciate a function in enriching its docstring and in logging a
    message when the function is used.

    :param str start: date or version of function deprecation.
    :param str reason: additional message to add to the docstring if given.
    :param Logger logger: logger to use if given.
    :return: deprecated function.
    """

    def depreciate(func):
        """Depreciate input function.

        :param func: function to depreciate.
        :return: wrapper from func which log messages.
        """

        logmessage = "{0} is deprecated from {1}.".format(func, start)
        if reason is not None:
            logmessage = "{0}\nReason: {1}".format(logmessage, reason)

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Log a deprecation message before running the function ``func``.

            :param args: func call varargs.
            :param kwargs: func call keywords.
            """

            log = logger

            if log is None:
                log = _findlogger(func, args, kwargs)

            if log is None:  # raise an error if logger is None
                raise RuntimeError(logmessage)
            else:  # otherwise log a warning message
                log.warning(logmessage)

            # execute func with args and kwargs and return the result
            return func(*args, **kwargs)

        # update func docstring
        docstring = "{0}\n{1}".format(logmessage, func.__doc__)
        func.__doc__ = docstring

        return wrapper

    return depreciate
