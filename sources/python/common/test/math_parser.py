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
import math
from canopsis.common.math_parser import Formulas
from random import random


class FormulasTest(TestCase):
    """docstring for FormulasTest"""

    def setUp(self):
        self.x = random()
        self.y = random()
        self.me1 = random()
        self.me2 = random()
        self.me3 = random()
        # Variables values
        _dict = {
            'x': self.x, 'y': self.y,
            'me1': self.me1,
            'me2': self.me2,
            'me3': self.me3
        }
        self.formula = Formulas(_dict)

    def test(self):
        '''abs'''

        expressions = {
            'x^2 + 9*x + 5': self.x**2 + 9*self.x + 5,
            'x^y': self.x**self.y,
            'x^y + x + 2*y': self.x**self.y + self.x + 2*self.y,
            '-9': -9,
            '-E': -math.e, '9 + 3 + 6': 9 + 3 + 6,
            '2*3.14159': 2*3.14159,
            'PI * PI / 10': math.pi * math.pi / 10,
            'PI^2': math.pi**2,
            'E^PI': math.e**math.pi,
            '2^3^2': 2**3**2,
            'sgn(-2)': -1,
            'sin(PI/2)': math.sin(math.pi / 2),
            'trunc(E)': int(math.e),
            'round(E)': round(math.e),
            '(x + y + 1)/3': (self.x + self.y + 1) / 3,
            '(me1 + me2 + me3) / 3': (self.me1 + self.me2 + self.me3) / 3,
            'MIN(2, 5, y, x)': min(2, 5, self.y, self.x),
            'MAX(2, 8, 45)': max(2, 8, 45),
            'sum(7, 13.56, 0.04)': sum([7, 13.56, 0.04])
        }

        for k, val in expressions.iteritems():
            evaluation = self.formula.evaluate(k)
            if isinstance(val, float):
                val = round(val, 5)
                evaluation = round(evaluation, 5)
            self.assertEqual(evaluation, val)

if __name__ == '__main__':
    main()
