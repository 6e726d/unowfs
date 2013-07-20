#!/usr/bin/env python3

# unowfs.py - Port of the utility to extract files from OWFS file system images
#             wrote by Craig Heffner (http://www.devttys0.com).
#             Original tool can be found on the following URL:
#               - http://www.devttys0.com/wp-content/uploads/2011/06/unowfs.c
#
# Copyright (C) 2013 - Andres Blanco
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Andres Blanco (6e726d)
#

import os
import sys
import struct

version_error_msg = "Python 3.3 or later is required."

try:
    import lzma
except ImportError:
    print(versio_error_msg)
    sys.exit(-1)

MAGIC = b"owowowowowowowowowowowowowowowow"
MAGIC_SIZE = 32
FILE_NAME_MAX_SIZE = 40
DEFAULT_DEST_DIR = "owfs-root"
DIRECTORY_TRAVERSAL = "../"
FILE_PREFIX = "./"
FILE_PREFIX_SIZE = 2
FILE_PATH_SIZE = 43


def file_write(file, data):
    try:
        fd = open(file, "wb")
        aux_data = lzma.decompress(data)
        fd.write(aux_data)
        fd.close()
        return True
    except Exception:
        return False
    return True


def unowfs(data):
    offset = 0
    header = {}
    file_count = 0

    offset = data.find(MAGIC)

    if offset == -1:
        print("\nNo signature on file\n")
        return -1

    if len(data) - offset < MAGIC_SIZE + 4 + 4 + 4:
        print("Invalid image: size too small\n")
        return -1

    header['magic'] = data[offset:offset+MAGIC_SIZE]

    if header['magic'] != MAGIC:
        print("Invalid image: bad magic signature\n")
        return -1

    fs_hdr_offset = offset

    offset += MAGIC_SIZE

    version = data[offset:offset + 4]
    header['version'] = struct.unpack(">I", version)[0]
    offset += 4
    number_of_entries = data[offset:offset+4]
    header['number of entries'] = struct.unpack(">I", number_of_entries)[0]
    offset += 4
    # Unknown integer value
    offset += 4

    msg = "Extracting %d files from OWFS version %d image...\n"
    print(msg % (header['number of entries'], header['version']))

    for index in range(header['number of entries']):
        filename = data[offset:offset + FILE_NAME_MAX_SIZE].replace(b'\x00', b'').decode("UTF-8")
        offset += FILE_NAME_MAX_SIZE
        size = struct.unpack(">I", data[offset:offset + 4])[0]
        offset += 4
        file_offset = fs_hdr_offset + struct.unpack(">I", data[offset:offset + 4])[0]
        offset += 4
        if file_write(filename, data[file_offset:file_offset+size]):
            print("Extracted file \"%s\"" % filename)
        else:
            print("Error extracting file \"%s\"" % filename)

    return header['number of entries']

if __name__ == "__main__":

    if not (sys.version_info.major >= 3 and sys.version_info.minor >= 3):
        print(version_error_msg)
        sys.exit(-1)

    if len(sys.argv) < 2 or sys.argv[1][0] == "-":
        print("\nUsage: unowfs <owfs image> [destination directory]\n")
        sys.exit(-1)

    file = sys.argv[1]

    if len(sys.argv) == 3:
        directory = sys.argv[2]
    else:
        directory = DEFAULT_DEST_DIR

    fd = open(file, "rb")
    owbuf = fd.read()
    fd.close()

    if(len(owbuf) == 0):
        sys.exit(-1)

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as e:
        print("Error: %s" % str(e))
        sys.exit(-1)

    os.chdir(directory)

    file_count = unowfs(owbuf)
    if(file_count > 0):
        print("\nExtracted %d files to ./%s/\n" % (file_count, directory))
        sys.exit(0)

