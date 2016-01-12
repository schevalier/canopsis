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

from operator import lt, le, gt, ge, ne, eq
from deepcopy import copy
from re import I, search

from datetime import datetime
from time import time


def get_field(key, obj):
    val = obj

    for subkey in key.split('.'):
        val = val[subkey]

    return val


def set_field(key, obj, val):
    o = obj
    subkeys = key.split('.')

    for subkey in subkeys[:-1]:
        if subkey not in o:
            o[subkey] = {}

        o = o[subkey]

    o[subkeys[-1]] = val


def del_field(key, obj):
    val = obj
    subkeys = key.split('.')

    for subkey in subkeys[:-1]:
        if subkey not in val:
            return

        val = val[subkey]

    del val[subkeys[-1]]


class Filter(object):
    def __init__(self, rule, *args, **kwargs):
        super(Filter, self).__init__(*args, **kwargs)

        self.rule = rule

    def match(self, obj):
        return self._match(self.rule, obj)

    def _match(self, rule, obj):
        for key in rule:
            if key == '$and':
                if not self.handle_and(key, rule[key], obj):
                    return False

            elif key == '$or':
                if not self.handle_or(key, rule[key], obj):
                    return False

            elif key == '$nor':
                if not self.handle_nor(key, rule[key], obj):
                    return False

            elif key in obj:
                if not self.handle_field(key, rule[key], obj):
                    return False

            else:
                return False

        return True

    def handle_and(self, key, rule, obj):
        for subrule in rule:
            if not self._match(rule, obj):
                return False

        return True

    def handle_or(self, key, rule, obj):
        for subrule in rule:
            if self._match(subrule, obj):
                return True

        return False

    def handle_nor(self, key, rule, obj):
        return not self.handle_or(key, rule, obj)

    def handle_field(self, key, rule, obj):
        if isinstance(rule, dict):
            if '$in' in rule:
                return self.handle_in_field(key, rule['$in'], obj)

            elif '$nin' in rule:
                return not self.handle_in_field(key, rule['$nin'], obj)

            elif '$all' in rule:
                return self.handle_all_feld(key, rule['$all'], obj)

            else:
                return self.handle_field_rule(key, rule, obj)

        else:
            field = get_field(key, obj)
            return (field == rule)

    def handle_in_field(self, key, rule, obj):
        field = get_field(key, obj)

        if not isinstance(field, list):
            return False

        else:
            return field in rule

    def handle_all_field(self, key, rule, obj):
        field = get_field(key, obj)

        for item in rule:
            if item not in field:
                return False

        return True

    def handle_field_exists(self, key, rule, obj):
        try:
            get_field(key, obj)

        except KeyError:
            found = False

        else:
            found = True

        if rule:
            return found

        else:
            return not found

    def handle_field_regex(self, key, pattern, obj, opts=None):
        opts = I if isinstance(opts, basestring) and 'i' in opts else 0
        field = get_field(key, obj)

        if None in (field, pattern):
            return False

        return bool(search(pattern, field, opts))

    def handle_field_rule(self, key, rule, obj):
        field = get_field(key, obj)
        cond = {
            '$lt': lt,
            '$lte': le,
            '$gt': gt,
            '$gte': ge,
            '$ne': ne,
            '$eq': eq
        }

        for op in rule:
            if op == '$exists':
                if not self.handle_field_exists(key, rule[op], obj):
                    return False

            elif op in cond.keys():
                if not cond[op](field, rule[op]):
                    return False

            elif op == '$regex':
                pattern = rule[op]
                options = rule.get('$options', None)

                if not self.handle_field_regex(key, pattern, obj, options):
                    return False

            elif op == '$not':
                if isinstance(rule[op], dict):
                    if self.handle_field_rule(key, rule[op], obj):
                        return False

                else:
                    pattern = rule[op]
                    options = rule.get('$options', None)

                    if self.handle_field_regex(key, pattern, obj, options):
                        return False

        return True


class Mangle(object):
    def __init__(self, rule, *args, **kwargs):
        super(Mangle, self).__init__(*args, **kwargs)

        self.rule = rule

    def __call__(self, obj):
        obj = copy(obj)

        for op in self.rule:
            if not op.startswith('$'):
                continue

            method = getattr(self, op[1:])
            method(self.rule[op], obj)

        return obj

    def inc(self, rule, obj):
        for key, amount in rule.iteritems():
            try:
                val = get_field(key, obj)

            except KeyError:
                val = 0

            set_field(key, obj, val + amount)

    def mul(self, rule, obj):
        for key, amount in rule.iteritems():
            try:
                val = get_field(key, obj)

            except KeyError:
                val = 0

            set_field(key, obj, val * amount)

    def rename(self, rule, obj):
        for key, newkey in rule.iteritems():
            try:
                val = get_field(key, obj)

            except KeyError:
                pass

            else:
                del_field(key, obj)
                set_field(key, obj, val)

    def set(self, rule, obj):
        for key, val in rule.iteritems():
            set_field(key, obj, val)

    def unset(self, rule, obj):
        for key in rule:
            try:
                get_field(key, obj)

            except KeyError:
                pass

            else:
                del_field(key, obj)

    def min(self, rule, obj):
        for key, newval in rule.iteritems():
            try:
                val = get_field(key, obj)

            except KeyError:
                set_field(key, obj, newval)

            else:
                if newval < val:
                    set_field(key, obj, newval)

    def max(self, rule, obj):
        for key, newval in rule.iteritems():
            try:
                val = get_field(key, obj)

            except KeyError:
                set_field(key, obj, newval)

            else:
                if newval > val:
                    set_field(key, obj, newval)

    def currentDate(self, rule, obj):
        for key, typespec in rule.iteritems():
            if isinstance(typespec, bool):
                val = datetime.now() if typespec else time()

            elif typespec['$type'] == 'date':
                val = datetime.now()

            elif typespec['$type'] == 'timestamp':
                val = time()

            else:
                continue

            set_field(key, obj, val)

    def addToSet(self, rule, obj):
        for key, value in rule.iteritems():
            try:
                array = get_field(key, obj)

            except KeyError:
                array = []

            if isinstance(value, dict) and '$each' in value:
                value = value['$each']

            if not isinstance(value, list):
                value = [value]

            for val in value:
                if val not in array:
                    array.append(val)

            set_field(key, obj, array)

    def pop(self, rule, obj):
        for key, spec in rule.iteritems():
            array = get_field(key, obj)

            if spec == -1:
                array.pop()

            elif spec == 1:
                array.pop(0)

            set_field(key, obj, array)

    def pull(self, rule, obj):
        for key, spec in rule.iteritems():
            array = get_field(key, obj)

            if isinstance(spec, dict):
                _filter = Filter(spec)

                array = [
                    val
                    for val in array
                    if not _filter.match(val)
                ]

            else:
                array = [val for val in array if val != spec]

            set_field(key, obj, array)

    def pullAll(self, rule, obj):
        for key, vals in rule.iteritems():
            array = get_field(key, obj)

            array = [
                val
                for val in array
                if val not in vals
            ]

            set_field(key, obj, array)

    def push(self, rule, obj):
        for key, spec in rule.iteritems():
            try:
                array = get_field(key, obj)

            except KeyError:
                array = []

            p, sort, s = -1, None, None

            if isinstance(spec, dict):
                if '$each' in spec:
                    val = spec['$each']
                    p = spec.get('$position', -1)
                    sort = spec.get('$sort', None)
                    s = spec.get('$slice', None)

            else:
                val = spec

            if not isinstance(val, list):
                val = [val]

            array = array[:p] + val + array[p:]

            if sort is not None:
                if isinstance(sort, dict):
                    for sortkey in sort:
                        array.sort(key=sortkey, reverse=(sort[sortkey] < 0))

                else:
                    array.sort(reverse=(sort < 0))

            if s is not None:
                if s < 0:
                    array = array[s:]

                else:
                    array = array[:s]

            set_field(key, obj, array)

    def bit(self, rule, obj):
        for key, spec in rule.iteritems():
            val = get_field(key, obj)

            if 'and' in spec:
                val &= spec['and']

            elif 'or' in spec:
                val |= spec['or']

            elif 'xor' in spec:
                val ^= spec['xor']

            set_field(key, obj, val)
