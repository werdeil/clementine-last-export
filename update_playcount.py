#!/usr/bin/python
# -*- coding: utf-8 -*-

#First version of the script which allows to update the playcount in the Clementine database from a last.fm extract

import sqlite3
import re
import codecs

import shutil
import os

from optparse import OptionParser
import logging
from logging import info,warning,error

from lastexport_corrected import main as lastexporter

#########################################################################
#    Functions
#########################################################################

def is_in_db(connection,artist,title):
    """
    Return False if the track is not found in the database
    """
    is_present = False
    curseur = connection.cursor()
    curseur.execute("""SELECT * FROM songs WHERE title = ? AND artist = ? """ ,(title, artist))
    if len(curseur.fetchall())>0:
        is_present = True
    else:
        curseur.execute("""SELECT * FROM songs WHERE title LIKE ? AND artist LIKE ? """ ,(title, artist))
        if len(curseur.fetchall())>0:
            is_present = True
    curseur.close()
    return is_present

def update_playcount(connection,artist,title,playcount):
    """
    Update playcount of the given title
    """
    curseur = connection.cursor()
    curseur.execute("""UPDATE songs SET playcount = ? WHERE title LIKE ? AND artist LIKE ?""" ,(int(playcount),title, artist))
    curseur.close()
    debug("""Playcount of %s from %s has been updated to %d""" %(title, artist, int(playcount)))

def parse_line(ligne):
    """
    Read a last.fm extract line and return the artist and song part
    """
    regexp = re.compile(""".*?\t(.*?)\t(.*?)\t.*""")
    titre,artiste = regexp.findall(ligne)[0]
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
        
    #Loop which will read the extract and store each play to a dictionary
    for line in extract_file.readlines():
        titre, artiste = parse_line(line)
        if biblio.has_key(artiste):
            if biblio[artiste].has_key(titre):
                biblio[artiste][titre] = biblio[artiste][titre] +1
            else:
                biblio[artiste][titre] = 1
        else:
            biblio[artiste] = {}
            biblio[artiste][titre] = 1
            
    #Loop which will try to update the database with each entry of the dictionnary           
    for artiste in biblio.keys():
        for titre in biblio[artiste].keys():
            if is_in_db(connection, artiste, titre) == True:
                update_playcount(connection, artiste, titre, biblio[artiste][titre])
                matched.append(artiste+' '+titre)
            else:
                not_matched.append(artiste+' '+titre)
    try:
        connection.commit()
    except sqlite3.Error, err:
        connection.rollback()
        error(unicode(err.args[0]))            
        
    extract_file.close()
    connection.close()
    return matched, not_matched
    
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
    parser.add_option("-i", "--input-file", dest="input_file", default=None, help="give already extracted file as input")
    parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="debug mode")
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true", help="activate verbose mode")
    
    options, args = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level="INFO")
    username= args[0]
    if options.input_file == None:
        info("No input file given, extracting directly from %s servers" %options.server)
        #Remove existing file except if the startpage is different from 1 because last_export script will no overwrite it, useful in case of a bad internet connection
        if os.path.exists(options.extract_file) and options.startpage == 1:
            os.remove(options.extract_file)
        lastexporter(username, options.startpage, options.extract_file, options.server)

    if options.backup:
        info("Backing up database into clementine_backup.db")
        shutil.copy(os.path.expanduser("~/.config/Clementine/clementine.db"), os.path.expanduser("~/.config/Clementine/clementine_backup.db"))
    
    info("Reading extract file and updating database")    
    matched, not_matched = update_db_file(os.path.expanduser("~/.config/Clementine/clementine_test.db"), options.extract_file)
    
    info("%d entries have been updated\nNo match was found for %d entries" %(len(matched), len(not_matched)))
    if options.debug == True:
        for element in sorted(not_matched):
            print element

