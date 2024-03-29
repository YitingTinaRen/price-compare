# MySQL Connector/Python - MySQL driver written in Python.
# Copyright (c) 2016, Oracle and/or its affiliates. All rights reserved.

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

"""Implementation of the Python Database API Specification v2.0 exceptions."""

import sys
import struct

from .locales import get_client_error

PY2 = sys.version_info[0] == 2

if PY2:
    def struct_unpack(fmt, buf):
        """Wrapper around struct.unpack handling buffer as bytes and strings.
        """
        if isinstance(buf, (bytearray, bytes)):
            return struct.unpack_from(fmt, buffer(buf))
        return struct.unpack_from(fmt, buf)
else:
    from struct import unpack as struct_unpack


class Error(Exception):
    """Exception that is base class for all other error exceptions."""

    def __init__(self, msg=None, errno=None, values=None, sqlstate=None):
        super(Error, self).__init__()
        self.msg = msg
        self._full_msg = self.msg
        self.errno = errno or -1
        self.sqlstate = sqlstate

        if not self.msg and (2000 <= self.errno < 3000):
            self.msg = get_client_error(self.errno)
            if values is not None:
                try:
                    self.msg = self.msg % values
                except TypeError as err:
                    self.msg = "{0} (Warning: {1})".format(self.msg, str(err))
        elif not self.msg:
            self._full_msg = self.msg = "Unknown error"

        if self.msg and self.errno != -1:
            fields = {
                "errno": self.errno,
                "msg": self.msg.encode("utf8") if PY2 else self.msg
            }
            if self.sqlstate:
                fmt = "{errno} ({state}): {msg}"
                fields["state"] = self.sqlstate
            else:
                fmt = "{errno}: {msg}"
            self._full_msg = fmt.format(**fields)

        self.args = (self.errno, self._full_msg, self.sqlstate)

    def __str__(self):
        return self._full_msg


class Warning(Exception):  # pylint: disable=W0622
    """Exception for important warnings."""
    pass


class InterfaceError(Error):
    """Exception for errors related to the interface."""
    pass


class DatabaseError(Error):
    """Exception for errors related to the database."""
    pass


class InternalError(DatabaseError):
    """Exception for errors internal database errors."""
    pass


class OperationalError(DatabaseError):
    """Exception for errors related to the database's operation."""
    pass


class ProgrammingError(DatabaseError):
    """Exception for errors programming errors."""
    pass


class IntegrityError(DatabaseError):
    """Exception for errors regarding relational integrity."""
    pass


class DataError(DatabaseError):
    """Exception for errors reporting problems with processed data."""
    pass


class NotSupportedError(DatabaseError):
    """Exception for errors when an unsupported database feature was used."""
    pass


class PoolError(Error):
    """Exception for errors relating to connection pooling."""
    pass


def intread(buf):
    """Unpacks the given buffer to an integer."""
    try:
        if isinstance(buf, int):
            return buf
        length = len(buf)
        if length == 1:
            return buf[0]
        elif length <= 4:
            tmp = buf + b"\x00" * (4 - length)
            return struct_unpack("<I", tmp)[0]
        else:
            tmp = buf + b"\x00" * (8 - length)
            return struct_unpack("<Q", tmp)[0]
    except BaseException:
        raise


def read_int(buf, size):
    """Read an integer from buffer.

    Returns a tuple (truncated buffer, int).
    """

    try:
        res = intread(buf[0:size])
    except BaseException:
        raise

    return (buf[size:], res)


def read_bytes(buf, size):
    """Reads bytes from a buffer.

    Returns a tuple with buffer less the read bytes, and the bytes.
    """
    res = buf[0:size]
    return (buf[size:], res)


def get_mysql_exception(errno, msg=None, sqlstate=None):
    """Get the exception matching the MySQL error.

    This function will return an exception based on the SQLState. The given
    message will be passed on in the returned exception.

    Returns an Exception.
    """
    try:
        return _ERROR_EXCEPTIONS[errno](msg=msg, errno=errno,
                                        sqlstate=sqlstate)
    except KeyError:
        # Error was not mapped to particular exception
        pass

    if not sqlstate:
        return DatabaseError(msg=msg, errno=errno)

    try:
        return _SQLSTATE_CLASS_EXCEPTION[sqlstate[0:2]](msg=msg, errno=errno,
                                                        sqlstate=sqlstate)
    except KeyError:
        # Return default InterfaceError
        return DatabaseError(msg=msg, errno=errno, sqlstate=sqlstate)


def get_exception(packet):
    """Returns an exception object based on the MySQL error.

    Returns an exception object based on the MySQL error in the given
    packet.

    Returns an Error-Object.
    """
    errno = errmsg = None

    try:
        if packet[4] != 255:
            raise ValueError("Packet is not an error packet")
    except IndexError as err:
        return InterfaceError("Failed getting Error information ({0})"
                              "".format(err))

    sqlstate = None
    try:
        packet = packet[5:]
        packet, errno = read_int(packet, 2)
        if packet[0] != 35:
            # Error without SQLState
            if isinstance(packet, (bytes, bytearray)):
                errmsg = packet.decode("utf8")
            else:
                errmsg = packet
        else:
            packet, sqlstate = read_bytes(packet[1:], 5)
            sqlstate = sqlstate.decode("utf8")
            errmsg = packet.decode("utf8")
    except Exception as err:  # pylint: disable=W0703
        return InterfaceError("Failed getting Error information ({0})"
                              "".format(err))
    else:
        return get_mysql_exception(errno, errmsg, sqlstate)


_SQLSTATE_CLASS_EXCEPTION = {
    "02": DataError,  # no data
    "07": DatabaseError,  # dynamic SQL error
    "08": OperationalError,  # connection exception
    "0A": NotSupportedError,  # feature not supported
    "21": DataError,  # cardinality violation
    "22": DataError,  # data exception
    "23": IntegrityError,  # integrity constraint violation
    "24": ProgrammingError,  # invalid cursor state
    "25": ProgrammingError,  # invalid transaction state
    "26": ProgrammingError,  # invalid SQL statement name
    "27": ProgrammingError,  # triggered data change violation
    "28": ProgrammingError,  # invalid authorization specification
    "2A": ProgrammingError,  # direct SQL syntax error or access rule violation
    "2B": DatabaseError,  # dependent privilege descriptors still exist
    "2C": ProgrammingError,  # invalid character set name
    "2D": DatabaseError,  # invalid transaction termination
    "2E": DatabaseError,  # invalid connection name
    "33": DatabaseError,  # invalid SQL descriptor name
    "34": ProgrammingError,  # invalid cursor name
    "35": ProgrammingError,  # invalid condition number
    "37": ProgrammingError,  # dynamic SQL syntax error or access rule violation
    "3C": ProgrammingError,  # ambiguous cursor name
    "3D": ProgrammingError,  # invalid catalog name
    "3F": ProgrammingError,  # invalid schema name
    "40": InternalError,  # transaction rollback
    "42": ProgrammingError,  # syntax error or access rule violation
    "44": InternalError,   # with check option violation
    "HZ": OperationalError,  # remote database access
    "XA": IntegrityError,
    "0K": OperationalError,
    "HY": DatabaseError,  # default when no SQLState provided by MySQL server
}

_ERROR_EXCEPTIONS = {
    1243: ProgrammingError,
    1210: ProgrammingError,
    2002: InterfaceError,
    2013: OperationalError,
    2049: NotSupportedError,
    2055: OperationalError,
    2061: InterfaceError,
}
