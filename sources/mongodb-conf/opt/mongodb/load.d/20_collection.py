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

from canopsis.mongo.core import MongoStorage


ms = MongoStorage()


collection_prefix_to_rename = {
    'periodic_': 'ponctual',
    'timed_': 'periodical_'
}

logger = None


def init():
    names = ms._database.collection_names()

    for name in names:
        for cptr in collection_prefix_to_rename:
            if name.startswith(cptr):
                newprefix = collection_prefix_to_rename[cptr]
                newname = '{0}{1}'.format(newprefix, name[len(cptr):])
                ms._database[name].rename(newname)
                logger.info('rename {0} to {1}'.format(name, newname))
                break


def update():
    pass
