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
Module for exporting tracks through audioscrobbler API.

Usage in command line: lastexport.py -u USER [-o OUTFILE] [-p STARTPAGE] [-s SERVER]
"""

import urllib2, urllib, time, re, os
import xml.etree.ElementTree as ET

from logging import info, warning, error, debug

def connect_server(server, username, startpage, sleep_func=time.sleep, tracktype='recenttracks'):
    """
    Connect to server and get a XML page.
    
    :param server: Server on which the information will be extracted
    :param username: Username to use on the server
    :param startpage: Page of the server where to start the importation
    :param sleep_func: Function to be called to wait when the server is not responding
    :param tracktype: Type of information to download from the server, can be either 'recentracks' or 'lovedtracks'    
    :type server: string
    :type username: string
    :type startpage: int
    :type sleep_func: function
    :type tracktype: string
    :return: response from the request the server
    :rtype: string
    """
    if server == "libre.fm":
        baseurl = 'http://alpha.libre.fm/2.0/?'
        urlvars = dict(method='user.get%s' % tracktype,
                    api_key=('clementine_last_export').ljust(32, '-'),
                    user=username,
                    page=startpage,
                    limit=200)

    elif server == "last.fm":
        baseurl = 'http://ws.audioscrobbler.com/2.0/?'
        urlvars = dict(method='user.get%s' % tracktype,
                    api_key='e38cc7822bd7476fe4083e36ee69748e',
                    user=username,
                    page=startpage,
                    limit=50)
    else:
        if server[:7] != 'http://':
            server = 'http://%s' % server
        baseurl = server + '/2.0/?'
        urlvars = dict(method='user.get%s' % tracktype,
                    api_key=('clementine_last_export').ljust(32, '-'),
                    user=username,
                    page=startpage,
                    limit=200)

    url = baseurl + urllib.urlencode(urlvars)
    for interval in (1, 5, 10, 62):
        try:
            f = urllib2.urlopen(url)
            break
        except Exception, e:
            last_exc = e
            warning("Exception occurred, retrying in %d s: %s" % (interval, e))
            sleep_func(interval)
    else:
        error("Failed to open page %s" % urlvars['page'])
        raise last_exc

    response = f.read()
    f.close()

    #bad hack to fix bad xml
    response = re.sub('\xef\xbf\xbe', '', response)
    return response

def get_pageinfo(response, tracktype='recenttracks'):
    """
    Check how many pages of tracks the user have.
    
    :param response: ?
    :param tracktype: ?
    :type response: string
    :type tracktype: string
    :return: Number of total pages to import
    :rtype: int
    """
    xmlpage = ET.fromstring(response)
    totalpages = xmlpage.find(tracktype).attrib.get('totalPages')
    return int(totalpages)

def get_tracklist(response):
    """
    Read XML page and get a list of tracks and their info.
    
    :param response: Response from a request to the server (xml page of the server)
    :type response: string
    :return: list of tracks in the page
    :rtype: list
    """
    xmlpage = ET.fromstring(response)
    tracklist = xmlpage.getiterator('track')
    return tracklist

def parse_track(trackelement):
    """
    Extract info from every track entry and output to list.
    
    :param trackelement: xml element representing a track
    :type trackelement: xml.etree.ElementTree
    :return: List containing the date, title, artist and albumname corresponding to the track
    :rtype: list
    """
    if trackelement.find('artist').getchildren():
        #artist info is nested in loved/banned tracks xml
        artistname = trackelement.find('artist').find('name').text
    else:
        artistname = trackelement.find('artist').text

    if trackelement.find('album') is None:
        #no album info for loved/banned tracks
        albumname = ''
    else:
        albumname = trackelement.find('album').text

    trackname = trackelement.find('name').text
    date = trackelement.find('date').get('uts')

    output = [date, trackname, artistname, albumname]

    for i, v in enumerate(output):
        if v is None:
            output[i] = ''

    return output

def write_tracks(tracks, outfileobj):
    """
    Write tracks to an open file
    
    :param tracks: list of tracks, containing th fields to be written
    :param outfileobj: File object in which the tracks will be written 
    :type tracks: list
    :type outfileobj: File
    :return: None
    """
    for fields in tracks:
        outfileobj.write(("\t".join(fields) + "\n").encode('utf-8'))

def get_tracks(server, username, startpage=1, sleep_func=time.sleep, tracktype='recenttracks', firsttrack = None):
    """
    Get tracks from a server
    
    :param server: Server on which the information will be extracted
    :param username: Username to use on the server
    :param startpage: Page of the server where to start the importation
    :param sleep_func: Function to be called to wait when the server is not responding
    :param tracktype: Type of information to download from the server, can be either 'recentracks' or 'lovedtracks' 
    :param firsttrack: track information corresponding the the last track imported in the previous import
    :type server: string
    :type username: string
    :type startpage: int
    :type sleep_func: function
    :type tracktype: string
    :type firsttrack: list    
    """
    page = startpage
    response = connect_server(server, username, page, sleep_func, tracktype)
    totalpages = get_pageinfo(response, tracktype)
    import_finished = False

    if startpage > totalpages:
        raise ValueError("First page (%s) is higher than total pages (%s)." % (startpage, totalpages))

    while page <= totalpages:
        #Skip connect if on first page, already have that one stored.
        if page > startpage:
            response =  connect_server(server, username, page, sleep_func, tracktype)

        tracklist = get_tracklist(response)

        tracks = []
        for trackelement in tracklist:
            # Do not export the currently playing track.
            if not trackelement.attrib.has_key("nowplaying") or not trackelement.attrib["nowplaying"]:
                track = parse_track(trackelement)
                if track == firsttrack:
                    import_finished = True
                    break
                else:
                    tracks.append(track)
                
        yield page, totalpages, tracks

        page += 1
        sleep_func(.5)
        
        if import_finished:
            break

def parse_line(ligne):
    """
    Read an extracted line and return the artist and song part
    
    :param ligne: Line from the server to parse
    :type ligne: string
    :return: The title and the artist included in the line
    :rtype: tuple(string, string)
    """
    regexp = re.compile(""".*?\t(.*?)\t(.*?)\t.*""")
    if regexp.match(ligne):
        title, artist = regexp.findall(ligne)[0]
    else:
        title, artist = None, None
        debug("""The following line cannot be parsed: %s""" %ligne[:-1])
    return title, artist

def lastexporter(server, username, startpage, outfile, infotype='recenttracks', use_cache=False, thread_signal=None):
    """
    Main method
    """
    track_regexp = re.compile("(.*?)\t(.*?)\t(.*?)\t(.*)")
    #read the already existing file (if it exists) and use_cache option
    if os.path.exists(outfile) and use_cache:
        info("%s is already present, it will be used as reference to speed up the import" %outfile)
        old_file = open(outfile, "r")
        already_imported_lines = old_file.readlines()
        old_file.close()
        firstline = already_imported_lines[0]
        date, title, artist, album = track_regexp.findall(firstline)[0]
        firsttrack = [date , title, artist, album]
    else:
        firsttrack = None
        already_imported_lines = []
        
    trackdict = dict()
    page = startpage  # for case of exception
    totalpages = -1  # ditto
    n = 0
    try:
        for page, totalpages, tracks in get_tracks(server, username, startpage, tracktype=infotype, firsttrack=firsttrack):
            info("Got page %s of %s.." % (page, totalpages))
            if thread_signal:
                thread_signal.emit(50*page/totalpages)
            for track in tracks:
                if infotype == 'recenttracks':
                    trackdict.setdefault(track[0], track)
                else:
                    #Can not use timestamp as key for loved/banned tracks as it's not unique
                    n += 1
                    trackdict.setdefault(n, track)
    except ValueError, e:
        exit(e)
    except Exception:
        raise
    finally:
        with open(outfile, 'w') as outfileobj:
            tracks = sorted(trackdict.values(), reverse=True)
            write_tracks(tracks, outfileobj)
            info("Wrote page %s-%s of %s to file %s" % (startpage, page, totalpages, outfile))
            
            for line in already_imported_lines:
                outfileobj.write(line)
            if already_imported_lines != []:
                info("Completed with already imported informations")
            outfileobj.close()
