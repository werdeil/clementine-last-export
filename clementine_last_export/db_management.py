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

"""Module gathering all the functions for the management of the database"""

import sqlite3
import platform

import shutil
import os
import codecs

from logging import info, error, debug

from server_management import parse_line

#########################################################################
#    Functions
#########################################################################

def is_in_db(connection, artist, title):
    """Search the track in the connected database and return its note and playcount

    :param connection: Connection to the SQL database
    :param artist: Artist of the track
    :param title: Title of the track
    :type connection: sqlite3.Connection
    :type artist: string
    :type title: string
    :return: Note and playcount of the track in the database if it is found, (None,-1) if it is not the case
    :rtype: tuple(int, int) or tuple(None, -1)
    """
    rating = None
    playcount = -1

    curseur = connection.cursor()
    curseur.execute("""SELECT rating,playcount FROM songs WHERE title = ? AND artist = ? """,(title, artist))
    result = curseur.fetchall()
    if len(result)>0:
        rating, playcount = result[0]
    else:
        curseur.execute("""SELECT rating,playcount FROM songs WHERE title LIKE ? AND artist LIKE ? """, (title, artist))
        result = curseur.fetchall()
        if len(result)>0:
            rating, playcount = result[0]

    curseur.close()

    return rating, playcount


def update_db_rating(connection, artist, title, rating):
    """Update the rating of a given track in the connected database

    :param connection: Connection to the SQL database
    :param artist: Artist of the track
    :param title: Title of the track
    :param rating: Rating value
    :type connection: sqlite3.Connection
    :type artist: string
    :type title: string
    :type rating: int
    :return: None
    """
    curseur = connection.cursor()
    curseur.execute("""UPDATE songs SET rating = ? WHERE title LIKE ? AND artist LIKE ?""", (rating, title, artist))
    curseur.close()

def update_db_playcount(connection, artist, title, playcount):
    """Update the playcount of a given track in the connected database

    :param connection: Connection to the SQL database
    :param artist: Artist of the track
    :param title: Title of the track
    :param playcount: Playcount value
    :type connection: sqlite3.Connection
    :type artist: string
    :type title: string
    :type playcount: int
    :return: None
    """
    curseur = connection.cursor()
    curseur.execute("""UPDATE songs SET playcount = ? WHERE title LIKE ? AND artist LIKE ?""", (playcount, title, artist))
    curseur.close()

def get_dbpath():
    """Give the path to the Clementine database depending on the operating system in which the function is called

    :return: Path to the database
    :rtype: string
    :warning: This function hasn't been tested on Windows nor on OSX
    """
    operating_system = platform.system()
    if operating_system == 'Linux':
        db_path = '~/.config/Clementine/'
    if operating_system == 'Darwin':
        db_path = '~/Library/Application Support/Clementine/'
    if operating_system == 'Windows':
        db_path = '%USERPROFILE%\\.config\\Clementine\\'
    return db_path

def backup_db(db_path):
    """Create a backup of the database file by copying it into clementine_backup.db file

    :param db_path: Path to the database
    :type db_path: string
    :return: None
    """
    info("Backing up database into clementine_backup.db")
    shutil.copy(os.path.expanduser("%s/clementine.db" %db_path), os.path.expanduser("%s/clementine_backup.db" %db_path))

def update_db_file(database, extract, force_update=True, updated_part="None", thread_signal=None):
    """Update the ratings or the playcounts of a database according to an extract file

    :param database: Path to the database to update
    :param extract: Path the extract file
    :param force_update: Option to update the database fields independently to their previous values
    :param updated_part: Either "playcount" or "rating", define the field to update in the database
    :param thread_signal: Thread signal to be emitted to the GUI
    :type database: string
    :type extract: string
    :type force_update: boolean
    :type update_part: string
    :type thread_signal: Thread.signal
    :return: 3 lists: the list of updated tracks, the list of not matched tracks and the list of tracks that were already up to date
    :rtype: tuple(list, list, list)
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
        if artiste in biblio.keys():
            if biblio[artiste].has_key(titre):
                biblio[artiste][titre] = biblio[artiste][titre] +1
            else:
                biblio[artiste][titre] = 1
                nb_titles += 1
        elif artiste is None or titre is None:
            pass
        else:
            biblio[artiste] = {}
            biblio[artiste][titre] = 1

    #Loop which will try to update the database with each entry of the dictionary
    titles_updated = 0
    for artiste in biblio:
        for titre in biblio[artiste]:
            original_rating, original_playcount = is_in_db(connection, artiste, titre)
            if original_rating is None or original_playcount == -1:
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
    except sqlite3.Error as err:
        connection.rollback()
        error(err.args[0])

    extract_file.close()
    connection.close()

    return matched, not_matched, already_ok
