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

from logging import info, warning, error, debug

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

def update_rating(connection,artist,title,rating):
    """
    Update rating of the given title
    """
    curseur = connection.cursor()
    curseur.execute("""UPDATE songs SET rating = ? WHERE title LIKE ? AND artist LIKE ?""" ,(int(rating),title, artist))
    curseur.close()    

def update_playcount(connection,artist,title,playcount):
    """
    Update playcount of the given title
    """
    curseur = connection.cursor()
    curseur.execute("""UPDATE songs SET playcount = ? WHERE title LIKE ? AND artist LIKE ?""" ,(int(playcount), title, artist))
    curseur.close()
    
def backup_db(db_path):
    info("Backing up database into clementine_backup.db")
    shutil.copy(os.path.expanduser("%s/clementine.db" %db_path), os.path.expanduser("%s/clementine_backup.db" %db_path))
