# MySQL Connector/Python - MySQL driver written in Python.
# Copyright (c) 2009, 2015, Oracle and/or its affiliates. All rights reserved.

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

"""Utilities
"""

from __future__ import print_function

__MYSQL_DEBUG__ = False

import struct

from .catch23 import struct_unpack


def intread(buf):
    """Unpacks the given buffer to an integer"""
    try:
        if isinstance(buf, int):
            return buf
        length = len(buf)
        if length == 1:
            return buf[0]
        elif length <= 4:
            tmp = buf + b'\x00' * (4 - length)
            return struct_unpack('<I', tmp)[0]
        else:
            tmp = buf + b'\x00' * (8 - length)
            return struct_unpack('<Q', tmp)[0]
    except BaseException:
        raise


def int1store(i):
    """
    Takes an unsigned byte (1 byte) and packs it as a bytes-object.

    Returns string.
    """
    if i < 0 or i > 255:
        raise ValueError('int1store requires 0 <= i <= 255')
    else:
        return bytearray(struct.pack('<B', i))


def int2store(i):
    """
    Takes an unsigned short (2 bytes) and packs it as a bytes-object.

    Returns string.
    """
    if i < 0 or i > 65535:
        raise ValueError('int2store requires 0 <= i <= 65535')
    else:
        return bytearray(struct.pack('<H', i))


def int3store(i):
    """
    Takes an unsigned integer (3 bytes) and packs it as a bytes-object.

    Returns string.
    """
    if i < 0 or i > 16777215:
        raise ValueError('int3store requires 0 <= i <= 16777215')
    else:
        return bytearray(struct.pack('<I', i)[0:3])


def int4store(i):
    """
    Takes an unsigned integer (4 bytes) and packs it as a bytes-object.

    Returns string.
    """
    if i < 0 or i > 4294967295:
        raise ValueError('int4store requires 0 <= i <= 4294967295')
    else:
        return bytearray(struct.pack('<I', i))


def int8store(i):
    """
    Takes an unsigned integer (8 bytes) and packs it as string.

    Returns string.
    """
    if i < 0 or i > 18446744073709551616:
        raise ValueError('int8store requires 0 <= i <= 2^64')
    else:
        return bytearray(struct.pack('<Q', i))


def intstore(i):
    """
    Takes an unsigned integers and packs it as a bytes-object.

    This function uses int1store, int2store, int3store,
    int4store or int8store depending on the integer value.

    returns string.
    """
    if i < 0 or i > 18446744073709551616:
        raise ValueError('intstore requires 0 <= i <=  2^64')

    if i <= 255:
        formed_string = int1store
    elif i <= 65535:
        formed_string = int2store
    elif i <= 16777215:
        formed_string = int3store
    elif i <= 4294967295:
        formed_string = int4store
    else:
        formed_string = int8store

    return formed_string(i)


def lc_int(i):
    """
    Takes an unsigned integer and packs it as bytes,
    with the information of how much bytes the encoded int takes.
    """
    if i < 0 or i > 18446744073709551616:
        raise ValueError('Requires 0 <= i <= 2^64')

    if i < 251:
        return bytearray(struct.pack('<B', i))
    elif i <= 65535:
        return b'\xfc' + bytearray(struct.pack('<H', i))
    elif i <= 16777215:
        return b'\xfd' + bytearray(struct.pack('<I', i)[0:3])
    else:
        return b'\xfe' + bytearray(struct.pack('<Q', i))


def read_bytes(buf, size):
    """
    Reads bytes from a buffer.

    Returns a tuple with buffer less the read bytes, and the bytes.
    """
    res = buf[0:size]
    return (buf[size:], res)


def read_lc_string(buf):
    """
    Takes a buffer and reads a length coded string from the start.

    This is how Length coded strings work

    If the string is 250 bytes long or smaller, then it looks like this:

      <-- 1b  -->
      +----------+-------------------------
      |  length  | a string goes here
      +----------+-------------------------

    If the string is bigger than 250, then it looks like this:

      <- 1b -><- 2/3/8 ->
      +------+-----------+-------------------------
      | type |  length   | a string goes here
      +------+-----------+-------------------------

      if type == \xfc:
          length is code in next 2 bytes
      elif type == \xfd:
          length is code in next 3 bytes
      elif type == \xfe:
          length is code in next 8 bytes

    NULL has a special value. If the buffer starts with \xfb then
    it's a NULL and we return None as value.

    Returns a tuple (trucated buffer, bytes).
    """
    if buf[0] == 251:  # \xfb
        # NULL value
        return (buf[1:], None)

    length = lsize = 0
    fst = buf[0]

    if fst <= 250:  # \xFA
        length = fst
        return (buf[1 + length:], buf[1:length + 1])
    elif fst == 252:
        lsize = 2
    elif fst == 253:
        lsize = 3
    if fst == 254:
        lsize = 8

    length = intread(buf[1:lsize + 1])
    return (buf[lsize + length + 1:], buf[lsize + 1:length + lsize + 1])


def read_lc_string_list(buf):
    """Reads all length encoded strings from the given buffer

    Returns a list of bytes
    """
    byteslst = []

    sizes = {252: 2, 253: 3, 254: 8}

    buf_len = len(buf)
    pos = 0

    while pos < buf_len:
        first = buf[pos]
        if first == 255:
            # Special case when MySQL error 1317 is returned by MySQL.
            # We simply return None.
            return None
        if first == 251:
            # NULL value
            byteslst.append(None)
            pos += 1
        else:
            if first <= 250:
                length = first
                byteslst.append(buf[(pos + 1):length + (pos + 1)])
                pos += 1 + length
            else:
                lsize = 0
                try:
                    lsize = sizes[first]
                except KeyError:
                    return None
                length = intread(buf[(pos + 1):lsize + (pos + 1)])
                byteslst.append(
                    buf[pos + 1 + lsize:length + lsize + (pos + 1)])
                pos += 1 + lsize + length

    return tuple(byteslst)


def read_string(buf, end=None, size=None):
    """
    Reads a string up until a character or for a given size.

    Returns a tuple (trucated buffer, string).
    """
    if end is None and size is None:
        raise ValueError('read_string() needs either end or size')

    if end is not None:
        try:
            idx = buf.index(end)
        except ValueError:
            raise ValueError("end byte not present in buffer")
        return (buf[idx + 1:], buf[0:idx])
    elif size is not None:
        return read_bytes(buf, size)

    raise ValueError('read_string() needs either end or size (weird)')


def read_int(buf, size):
    """Read an integer from buffer

    Returns a tuple (truncated buffer, int)
    """

    try:
        res = intread(buf[0:size])
    except BaseException:
        raise

    return (buf[size:], res)


def read_lc_int(buf):
    """
    Takes a buffer and reads an length code string from the start.

    Returns a tuple with buffer less the integer and the integer read.
    """
    if not buf:
        raise ValueError("Empty buffer.")

    lcbyte = buf[0]
    if lcbyte == 251:
        return (buf[1:], None)
    elif lcbyte < 251:
        return (buf[1:], int(lcbyte))
    elif lcbyte == 252:
        return (buf[3:], struct_unpack('<xH', buf[0:3])[0])
    elif lcbyte == 253:
        return (buf[4:], struct_unpack('<I', buf[1:4] + b'\x00')[0])
    elif lcbyte == 254:
        return (buf[9:], struct_unpack('<xQ', buf[0:9])[0])
    else:
        raise ValueError("Failed reading length encoded integer")


#
# For debugging
#
def _digest_buffer(buf):
    """Debug function for showing buffers"""
    if not isinstance(buf, str):
        return ''.join(["\\x%02x" % c for c in buf])
    return ''.join(["\\x%02x" % ord(c) for c in buf])


def print_buffer(abuffer, prefix=None, limit=30):
    """Debug function printing output of _digest_buffer()"""
    if prefix:
        if limit and limit > 0:
            digest = _digest_buffer(abuffer[0:limit])
        else:
            digest = _digest_buffer(abuffer)
        print(prefix + ': ' + digest)
    else:
        print(_digest_buffer(abuffer))
