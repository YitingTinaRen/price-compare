# MySQL Connector/Python - MySQL driver written in Python.
# Copyright (c) 2009, 2014, Oracle and/or its affiliates. All rights reserved.

# MySQL Connector/Python is licensed under the terms of the GPLv2
# <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>, like most
# MySQL Connectors. There are special exceptions to the terms and
# conditions of the GPLv2 as it is applied to this software, see the
# FOSS License Exception
# <http://www.mysql.com/about/legal/licensing/foss-exception.html>.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""
This module implements some constructors and singletons as required by the
DB API v2.0 (PEP-249).
"""

# Python Db API v2
from . import constants
import datetime
import time
apilevel = '2.0'
threadsafety = 1
paramstyle = 'pyformat'


class _DBAPITypeObject(object):

    def __init__(self, *values):
        self.values = values

    def __eq__(self, other):
        if other in self.values:
            return True
        else:
            return False

    def __ne__(self, other):
        if other in self.values:
            return False
        else:
            return True


Date = datetime.date
Time = datetime.time
Timestamp = datetime.datetime


def DateFromTicks(ticks):
    return Date(*time.localtime(ticks)[:3])


def TimeFromTicks(ticks):
    return Time(*time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    return Timestamp(*time.localtime(ticks)[:6])


Binary = bytes

STRING = _DBAPITypeObject(*constants.FieldType.get_string_types())
BINARY = _DBAPITypeObject(*constants.FieldType.get_binary_types())
NUMBER = _DBAPITypeObject(*constants.FieldType.get_number_types())
DATETIME = _DBAPITypeObject(*constants.FieldType.get_timestamp_types())
ROWID = _DBAPITypeObject()
