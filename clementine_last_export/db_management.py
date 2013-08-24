#!/usr/bin/env python
#-*- coding: utf-8 -*-

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

"""
Script gathering all the methods for the management of the database
"""

import sqlite3

import shutil
import os
import codecs

from logging import info, warning, error, debug

from server_management import parse_line

#########################################################################
#    Functions
#########################################################################

def is_in_db(connection,artist,title):
    """
    Return note and playcount of the track if it is in the database, (None,-1) if it is not the case
    """
    rating = None
    playcount = -1
    curseur = connection.cursor()
    curseur.execute("""SELECT rating,playcount FROM songs WHERE title = ? AND artist = ? """ ,(title, artist))
    result = curseur.fetchall()
    if len(result)>0:
        rating, playcount = result[0]
    else:
        curseur.execute("""SELECT rating,playcount FROM songs WHERE title LIKE ? AND artist LIKE ? """ ,(title, artist))
        result = curseur.fetchall()
        if len(result)>0:
            rating, playcount = result[0]
    curseur.close()
    return rating, playcount

def update_db_rating(connection,artist,title,rating):
    """
    Update rating of the given title
    """
    curseur = connection.cursor()
    curseur.execute("""UPDATE songs SET rating = ? WHERE title LIKE ? AND artist LIKE ?""" ,(int(rating),title, artist))
    curseur.close()    

def update_db_playcount(connection,artist,title,playcount):
    """
    Update playcount of the given title
    """
    curseur = connection.cursor()
    curseur.execute("""UPDATE songs SET playcount = ? WHERE title LIKE ? AND artist LIKE ?""" ,(int(playcount), title, artist))
    curseur.close()
    
def backup_db(db_path):
    """
    Backup the database file
    """
    info("Backing up database into clementine_backup.db")
    shutil.copy(os.path.expanduser("%s/clementine.db" %db_path), os.path.expanduser("%s/clementine_backup.db" %db_path))
    
def update_db_file(database, extract, force_update=True, updated_part="None", thread_signal=None):
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
    nb_titles = 0
    for line in extract_file.readlines():
        titre, artiste = parse_line(line)
        if biblio.has_key(artiste):
            if biblio[artiste].has_key(titre):
                biblio[artiste][titre] = biblio[artiste][titre] +1
            else:
                biblio[artiste][titre] = 1
                nb_titles += 1
        elif artiste == None or titre == None:
            pass
        else:
            biblio[artiste] = {}
            biblio[artiste][titre] = 1
            
    #Loop which will try to update the database with each entry of the dictionary
    titles_updated = 0           
    for artiste in biblio.keys():
        for titre in biblio[artiste].keys():
            original_rating, original_playcount = is_in_db(connection, artiste, titre)
            if original_rating == None or original_playcount == -1:
                not_matched.append(artiste + ' ' + titre)
                debug("""Song %s from %s cannot be found in the database""" %(titre, artiste))
            #part to update the ratings
            elif updated_part == "rating":
                if original_rating == 4.5/5 and not force_update:
                    already_ok.append(artiste + ' ' + titre)
                elif original_rating < 1:
                    update_db_rating(connection, artiste, titre, 1)
                    matched.append(artiste + ' ' + titre)
                else:
                    already_ok.append(artiste + ' ' + titre)
            #part to update the playcount
            elif updated_part == "playcount":
                if original_playcount < biblio[artiste][titre] or force_update:
                    update_db_playcount(connection, artiste, titre, biblio[artiste][titre])
                    matched.append(artiste + ' ' + titre)
                else:
                    already_ok.append(artiste + ' ' + titre)
            if thread_signal:
                titles_updated += 1
                thread_signal.emit(50*titles_updated/nb_titles+50)
                
    try:
        connection.commit()
    except sqlite3.Error, err:
        connection.rollback()
        error(unicode(err.args[0]))            
        
    extract_file.close()
    connection.close()
    return matched, not_matched, already_ok 
