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

import sqlite3
import re
import codecs

import shutil
import os, platform

from optparse import OptionParser
import logging
from logging import info,warning,error,debug

from lastexport import main as lastexporter

#########################################################################
#    Functions
#########################################################################

def is_in_db(connection,artist,title):
    """
    Return playcount if the track is in the database, -1 if it is not the case
    """
    playcount = -1
    curseur = connection.cursor()
    curseur.execute("""SELECT playcount FROM songs WHERE title = ? AND artist = ? """ ,(title, artist))
    result = curseur.fetchall()
    if len(result)>0:
        playcount = result[0][0]
    else:
        curseur.execute("""SELECT playcount FROM songs WHERE title LIKE ? AND artist LIKE ? """ ,(title, artist))
        result = curseur.fetchall()
        if len(result)>0:
            playcount = result[0][0]
    curseur.close()
    return playcount

def update_playcount(connection,artist,title,playcount):
    """
    Update playcount of the given title
    """
    curseur = connection.cursor()
    curseur.execute("""UPDATE songs SET playcount = ? WHERE title LIKE ? AND artist LIKE ?""" ,(int(playcount), title, artist))
    curseur.close()

def parse_line(ligne):
    """
    Read a last.fm extract line and return the artist and song part
    """
    regexp = re.compile(""".*?\t(.*?)\t(.*?)\t.*""")
    if regexp.match(ligne):
        titre,artiste = regexp.findall(ligne)[0]
    else:
        titre, artiste = None,None
        debug("""The following line cannot be parsed: %s""" %ligne[:-1])
    return titre, artiste

def update_db_file(database, extract):
    """
    Update a database according to an extract file
    """
    connection = sqlite3.connect(database)
    extract_file = codecs.open(extract, encoding='utf-8')
    biblio = {}    
    matched = []
    not_matched = []
    already_ok = []
        
    #Loop which will read the extract and store each play to a dictionary
    for line in extract_file.readlines():
        titre, artiste = parse_line(line)
        if biblio.has_key(artiste):
            if biblio[artiste].has_key(titre):
                biblio[artiste][titre] = biblio[artiste][titre] +1
            else:
                biblio[artiste][titre] = 1
        elif artiste == None or titre == None:
            pass
        else:
            biblio[artiste] = {}
            biblio[artiste][titre] = 1
            
    #Loop which will try to update the database with each entry of the dictionnary           
    for artiste in biblio.keys():
        for titre in biblio[artiste].keys():
            original_playcount = is_in_db(connection, artiste, titre)
            if original_playcount == -1:
                not_matched.append(artiste+' '+titre)
                debug("""Song %s from %s cannot be found in the database""" %(titre,artiste))
            elif original_playcount < biblio[artiste][titre]:
                update_playcount(connection, artiste, titre, biblio[artiste][titre])
                matched.append(artiste+' '+titre)
            else:
                already_ok.append(artiste+' '+titre)
    try:
        connection.commit()
    except sqlite3.Error, err:
        connection.rollback()
        error(unicode(err.args[0]))            
        
    extract_file.close()
    connection.close()
    return matched, not_matched, already_ok
    
#######################################################################
#    Main
#######################################################################

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
        
    username= args[0]
    operating_system = platform.system()
    if operating_system == 'Linux':
        db_path = '~/.config/Clementine/'
    if operating_system == 'Darwin':
        db_path = '~/Library/Application Support/Clementine/'
    if operating_system == 'Windows':
        db_path = '%USERPROFILE%\\.config\\Clementine\\'''
    
    if not options.input_file:
        info("No input file given, extracting directly from %s servers" %options.server)
        #Remove existing file except if the startpage is different from 1 because last_export script will no overwrite it, useful in case of a bad internet connection
        if os.path.exists(options.extract_file) and options.startpage == 1:
            os.remove(options.extract_file)
        lastexporter(options.server, username, options.startpage, options.extract_file, infotype='recenttracks')

    if options.backup:
        info("Backing up database into clementine_backup.db")
        shutil.copy(os.path.expanduser("%s/clementine.db" %db_path), os.path.expanduser("%s/clementine_backup.db" %db_path))

    info("Reading extract file and updating database")    
    matched, not_matched, already_ok = update_db_file(os.path.expanduser("%s/clementine.db" %db_path), options.extract_file)
    
    info("%d entries have been updated, %d entries have already the correct playcount, no match was found for %d entries" %(len(matched), len(already_ok), len(not_matched)))

