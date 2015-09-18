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

"""Status configuration module.
"""

from canopsis.common.init import basestring
from canopsis.task.core import get_task


class StatusConfiguration(dict):
    """Manage status configuration.

    A status configuration links status task and code with a name.
    """

    class Error(Exception):
        """Handle StatusConfiguration errors.
        """

    CODE = 'code'  #: status code property name.
    TASK = 'task'  #: status task property name.

    def __init__(self, status):

        super(StatusConfiguration, self).__init__(status)

        self.status_name_by_code = {}

        for name in self:
            params = self[name]
            self.status_name_by_code[params[self.CODE]] = name

    def value(self, name):
        """Get status value related to input name.

        :param str name: status name.
        :return: status code corresponding to input name.
        :rtype: int
        """

        result = None

        try:
            value = self[name]
        except KeyError:
            raise StatusConfiguration.Error(
                'Status {0} not registered in {1}'.format(name, self)
            )
        else:
            try:
                result = value[StatusConfiguration.CODE]
            except KeyError:
                raise StatusConfiguration.Error(
                    'Status {0} has no code in {1}'.format(name, value)
                )

        return result

    def name(self, code):
        """Get status name from input status code.

        :param int code: status code.
        :return: related status name.
        :rtype: str
        """

        try:
            result = self.status_name_by_code[code]

        except KeyError:
            raise StatusConfiguration.Error(
                'Code {0} does not exist in {1}'.format(code, self)
            )

        else:
            return result

    def task(self, status):
        """Get task related to input status name/code.

        :param status: status from where get the right task to process it.
        :type status: int or str or dict
        :return: task function able to process an event with input status.
        :rtype: function
        """

        value = status

        if isinstance(status, dict):
            name = self.name(status[StatusConfiguration.CODE])
            value = self[name]

        elif isinstance(status, int):
            name = self.name(status)
            value = self[name]

        elif isinstance(status, basestring):
            try:
                value = self[status]
            except KeyError:
                raise StatusConfiguration.Error(
                    'Status {0} not registered in {1}'.format(status, self)
                )

        try:
            taskpath = value[StatusConfiguration.TASK]

        except KeyError:
            raise StatusConfiguration.Error(
                'No task registered in {0} ({1})'.format(status, value)
            )

        else:
            result = get_task(taskpath)

            if result is None:
                raise StatusConfiguration.Error(
                    'No task registered to {0} in {1}'.format(status, value)
                )

            return result
