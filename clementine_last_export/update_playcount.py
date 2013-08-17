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

"""
Script which allows to update the playcount in the Clementine database from a last.fm extract
"""

import os, platform

from optparse import OptionParser
import logging
from logging import info, warning, error, debug

from server_management import lastexporter
from db_management import backup_db, update_db_file
   
#######################################################################
#    Main
#######################################################################

def update_playcount(username, input_file, server, extract_file, startpage, backup, force_update = False, use_cache = False):
    """
    Main method
    """
    operating_system = platform.system()
    if operating_system == 'Linux':
        db_path = '~/.config/Clementine/'
    if operating_system == 'Darwin':
        db_path = '~/Library/Application Support/Clementine/'
    if operating_system == 'Windows':
        db_path = '%USERPROFILE%\\.config\\Clementine\\'''
    
    if not input_file:
        info("No input file given, extracting directly from %s servers" %server)
        lastexporter(server, username, startpage, extract_file, infotype='recenttracks', use_cache=use_cache)

    if backup:
        backup_db(db_path)

    info("Reading extract file and updating database")    
    matched, not_matched, already_ok = update_db_file(os.path.expanduser("%s/clementine.db" %db_path), extract_file, force_update, updated_part="playcount")
    
    info("%d entries have been updated, %d entries have already the correct playcount, no match was found for %d entries" %(len(matched), len(already_ok), len(not_matched)))


if __name__ == "__main__":
    parser = OptionParser()
    parser.usage = """Usage: %prog <username> [options]
    
    Script which will extract data from the server and update clementine database
    <username> .......... Username used in the server
    """

    parser.add_option("-p", "--page", dest="startpage", type="int", default="1", help="page to start fetching tracks from, default is 1")
    parser.add_option("-e", "--extract-file", dest="extract_file", default="extract_last_fm.txt", help="extract file name, default is extract_last_fm.txt")
    parser.add_option("-s", "--server", dest="server", default="last.fm", help="server to fetch track info from, default is last.fm")
    parser.add_option("-b", "--backup", dest="backup", default=False, action="store_true", help="backup db first")
    parser.add_option("-i", "--input-file", dest="input_file", default=False, action="store_true", help="use the already extracted file as input")
    parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="debug mode")
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true", help="activate verbose mode")
    
    options, args = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level="INFO")
    if options.debug:
        logging.basicConfig(level="DEBUG")
        
    update_playcount(args[0], options.input_file, options.server, options.extract_file, options.startpage, options.backup, options.use_cache)
    
