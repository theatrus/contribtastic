#    EVE-Central.com Contribtastic
#    Copyright (C) 2005-2012 StackFoundry LLC
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License (in file COPYING) for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import os
import re
import exceptions
import sys
import urllib
import stat
from cStringIO import StringIO
import time


try:
    from win32com.shell import shell, shellcon
except:
    pass


from threading import Thread
from Queue import Queue
import evecache
from evec_upload.config import Config


def find_first_path(path, pref = None):
    dirlist = os.listdir(path)

    if pref is None:
        return dirlist[0]

    for p in pref:
        if p in dirlist or unicode(p) in dirlist:
            return p
    return dirlist[0]


def documents_path():
    # Platform specific logic for finding the cache folder
    if sys.platform == 'win32':
        document_folder = os.path.join( shell.SHGetFolderPath( 0,
                                                               shellcon.CSIDL_PERSONAL,
                                                               0, 0 ), 'EVE-Central CSV', )
    else:
        document_folder = os.path.abspath('~')

    try:
        os.makedirs(document_folder)
    except:
        pass
    return document_folder


def default_locations():
    """ This function returns all possible cache folders for Tranquility with the highest MachoNet version number """
    # Platform specific logic for finding the cache folder
    if sys.platform == 'win32':

        document_folder = "c:/"
        try:
            document_folder = os.path.join( shell.SHGetFolderPath( 0,
                                                                   shellcon.CSIDL_LOCAL_APPDATA,
                                                                   0, 0 ), 'CCP', 'EVE', )
        except Exception,e:
            print e
            pass
    elif sys.platform == 'darwin':

        from Carbon import Folder, Folders
        folderref = Folder.FSFindFolder( Folders.kUserDomain, Folders.kPreferencesFolderType, False )
        document_folder = os.path.join( folderref.as_pathname(), 'Eve Online Preferences', 'p_drive', 'My Documents', 'EVE', 'logs', 'MarketLogs' )
    else:
        document_folder = '' # don't know what the linux client has
        document_folder = os.path.normpath( document_folder )

    # Now try to find the most relevant cache folder

    print "Starting to scan from ",document_folder
    rex = re.compile('cache/MachoNet/87\.237\.38\.200/([0-9]+)/CachedMethodCalls$')
    def walker(arg, dirname, fnames):
        match = rex.search(dirname.replace('\\', '/'))
        if not match:
            return
        allpaths.append((match.group(1), dirname))

    allpaths = []

    os.path.walk(document_folder, walker, allpaths)
    print "All paths: ", allpaths
    # Max machonet version
    allversions = [x[0] for x in allpaths]
    maxversion = max(allversions)

    paths = [x[1] for x in allpaths if x[0] == maxversion]
    
    return paths


class ScannerPayload(object):
    def __init__(self, path, uploader, donecb):
        self.path = path
        self.uploader = uploader
        self.donecb = donecb

class ScannerThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(True)
        self.queue = Queue()

    def trigger(self, payload):
        self.queue.put(payload)


    def run(self):
        while True:
            payload = self.queue.get()
            try:
                scan_data(payload)
            except:
                pass # This is bad, I know.


def make_csv_file(orders, region, typeid, timestamp):
    config = Config()
    filename = os.path.join(documents_path, str(region) + "-" + str(typeid) + ".csv")
    with open(filename, 'w') as f:
        print >>f, orders
    return


# Local cache of currently seen files
seen = {}

def scan_data(job):

    dirl = []
    upcount = 0

    firstrun = 0
    if not seen:
        firstrun = 1

    try:
        dirl = os.listdir(job.path)
    except Exception,e:
        if job.donecb:
            self.donecb(count = upcount, success = False)
        print "Dir scan error at ",e
        return None

    config = Config()
    highest_timestamp = 0
    try:
        highest_timestamp = config['last_upload_time' + job.path]
    except:
        pass
    one_hour_ago = time.time() - 15*60 # 15 min ago
    if highest_timestamp < one_hour_ago:
        highest_timestamp = one_hour_ago

    start_ts = highest_timestamp
    print "UPLOAD START: TIMESTAMP CHECK IS > ",start_ts

    for item in dirl:
        print item
        if item[-6:] != ".cache":
            continue
        item = os.path.join(job.path, item)
        statinfo = os.stat(item)

        if seen.get(item,-1) == statinfo.st_mtime:
            continue

        seen[item] = statinfo.st_mtime

        if firstrun and statinfo.st_mtime <= start_ts:
            continue

        if statinfo.st_mtime > highest_timestamp:
            highest_timestamp = statinfo.st_mtime

        print "Now scanning",item, statinfo.st_mtime, highest_timestamp

        try:
            market_parser = evecache.MarketParser(str(item))
            if market_parser.valid() == True:
                entries = market_parser.getList()

                region = entries.region()
                typeid = entries.type()
                orders = []
                orders1 = entries.getSellOrders()
                orders2 = entries.getBuyOrders()
                # Fix up STL SWIG types not being list()
                for order in orders1:
                    orders.append(order)
                for order in orders2:
                    orders.append(order)

                if config['backup']:
                    make_csv_file(orders, region, typeid, statinfo.st_mtime)

                job.uploader.do(orders, region, typeid, statinfo.st_mtime)

                upcount += 1
            else:
                print "Not valid"
        except Exception,e:
            print e

    config['last_upload_time' + job.path] = highest_timestamp

    if job.donecb:
        job.donecb(count = upcount, success = True)

    return upcount
