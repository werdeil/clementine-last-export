#!/usr/bin/python
# -*- coding: utf-8 -*-

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

"""Script which allows to gives 5 stars in the Clementine database for last.fm loved tracks"""

import os

from optparse import OptionParser

import logging
from logging import info

from PyQt5 import QtCore

from server_management import lastexporter
from db_management import backup_db, update_db_file, get_dbpath

class ImportLovedTracks(QtCore.QThread):

    partDone = QtCore.pyqtSignal(int)

    def __init__(self, username, input_file, server, extract_file, startpage, backup, force_update=True, use_cache=False):
        QtCore.QThread.__init__(self)
        self.username = username
        self.input_file = input_file
        self.server = server
        self.extract_file = extract_file
        self.startpage = startpage
        self.backup = backup
        self.force_update = force_update
        self.use_cache = use_cache
        self.db_path = get_dbpath()

    def run(self):
        self.partDone.emit(0)

        if not self.input_file:
            info("No input file given, extracting directly from %s servers" %self.server)
            lastexporter(self.server, self.username, self.startpage, self.extract_file, infotype='lovedtracks', use_cache=self.use_cache, thread_signal=self.partDone)
        self.partDone.emit(50)

        if self.backup:
            backup_db(self.db_path)
        self.partDone.emit(51)

        info("Reading extract file and updating database")
        matched, not_matched, already_ok = update_db_file(os.path.expanduser("%s/clementine.db" %self.db_path),
                                                                             self.extract_file,
                                                                             self.force_update,
                                                                             updated_part="rating",
                                                                             thread_signal=self.partDone)
        info("%d entries have been updated, %d entries have already the correct note, no match was found for %d entries" %(len(matched), len(already_ok), len(not_matched)))
        self.partDone.emit(100)


if __name__ == "__main__":
    parser = OptionParser()
    parser.usage = """Usage: %prog <username> [options]
    
    Script which will extract data from the server and update clementine database
    <username> .......... Username used in the server
    """

    parser.add_option("-p", "--page", dest="startpage", type="int", default="1", help="page to start fetching tracks from, default is 1")
    parser.add_option("-e", "--extract-file", dest="extract_file", default="loved_tracks.txt", help="extract file name, default is loved_tracks.txt")
    parser.add_option("-s", "--server", dest="server", default="last.fm", help="server to fetch track info from, default is last.fm")
    parser.add_option("-b", "--backup", dest="backup", default=False, action="store_true", help="backup db first")
    parser.add_option("-i", "--input-file", dest="input_file", default=False, action="store_true", help="use the already extracted file as input")
    parser.add_option("-c", "--cache", dest="use_cache", default=False, action="store_true", help="use cache for import")
    parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="debug mode")
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true", help="activate verbose mode")

    options, args = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level="INFO")
    if options.debug:
        logging.basicConfig(level="DEBUG")

    thread = ImportLovedTracks(args[0], options.input_file, options.server, options.extract_file, options.startpage, options.backup, options.use_cache)
    thread.run()
