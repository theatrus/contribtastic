#    EVE-Central.com Contribtastic
#    Copyright (C) 2005-2010 Yann Ramin
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

import wx
import wx.lib.newevent

from threading import Thread
import evecache


ProgramVersion = 2000
ProgramVersionNice = "2.0"
CheckVersion = 1031

(UpdateUploadEvent, EVT_UPDATE_UPLOAD) = wx.lib.newevent.NewEvent()
(DoneUploadEvent, EVT_DONE_UPLOAD) = wx.lib.newevent.NewEvent()


class UploadPayload(object):
    def __init__(self, path, win, userid, backup):
        self.path = path
        self.win = win
        self.userid = userid
        self.backup = backup

class UploadThread(Thread):
    def __init__(self, payload):
        Thread.__init__(self)
        self.payload = payload
        self.setDaemon(False)
    def run(self):
        upload_data(self.payload)


class ProtocolVersionMismatch(exceptions.Exception):
    pass


def check_protocol():
    pc = urllib.urlopen("http://eve-central.com/protocol_version.txt")
    version = pc.readline().strip()
    pc.close()
    if version != "1":
        raise ProtocolVersionMismatch


def check_client():
    global ProgramVersion
    cv = urllib.urlopen("http://eve-central.com/client_version.txt")
    fversion = cv.readline().strip()
    version = cv.readline().strip()
    version = int(version)
    cv.close()
    if version > ProgramVersion:
        return fversion
    else:
        return True


def perform_upload(typename, linex, userid, times, cache = False, region = 0, typeid = 0):
    submitdata = urllib.urlencode({'typename' : typename, 'data' : lines, 
                                   'userid': userid , 'timestamp': times, 'cache': cache, 
                                   'region' : region, 'typeid' : typeid})
    
    h = urllib.urlopen("http://eve-central.com/datainput.py/inputdata", submitdata)
    h.readlines()
    h.close()

def check_csv(dirl):
    upcount = 0
    for item in dirl:
        # Old style CSV uploader
        if item[-3:] == "txt" and item != "readme.txt" and item.find("My orders")  == -1:
            # Found file
            filename = item
            upcount = upcount + 1
            typename = None
            times = 0
            try:
                # Bad check for hyphenated names
                s = item.split('-')
                if len(s) > 3:
                    typename = s[1] + "-" + s[2]
                    times = s[3]
                else:
                    typename = s[1]
                    times = s[2]
            except:
                # This isn't a valid item it seems like
                continue

            fileh = open( os.path.normpath( os.path.join( job.path, item ) ) )
            lines = ""
            linecount = 0
            for line in fileh.readlines():
                line.replace("\r", "")
                lines = lines + line
                linecount = linecount + 1

            fileh.close()
            perform_upload(typename, lines, job.userid, times, False)
            evt = UpdateUploadEvent(typename = typename, success = True)
            wx.PostEvent(job.win, evt)

            if job.backup:
                os.renames( os.path.normpath (os.path.join(job.path, filename)), os.path.normpath( os.path.join (job.path, job.backup, filename) ) )
            else:
                os.remove( os.path.normpath( os.path.join( job.path, item ) ) )
        return upcount


def upload_data(job):

    dirl = []
    upcount = 0

    try:
        dirl = os.listdir(job.path)
    except:
        evt = DoneUploadEvent(count = upcount, success = False)
        wx.PostEvent(job.win, evt)
        return None

    config = Config()
    highest_timestamp = 0
    for item in dirl:
        if item[-6:] != ".cache":
            continue
        statinfo = os.stat(item)
        if statinfo.st_mtime <= config['last_upload_time']:
            continue
        if statinfo.st_mtime > highest_timestamp:
            highest_timestamp = statinfo.st_mtime

        try:
            market_parser = evecache.MarketParser(item)
            entries = mp.getList()
            region = entries.region()
            type = entries.type()
            orders = entries.getSellOrders()
            orders.extend(entries.getBuyOrders())
            
            csvOutput = StringIO()
            print >>csvOutput, "CACHE GENERATED FILE HEADER"
            for order in orders:
                print >>csvOutput, order.toCsv()

            perform_upload("", csvOutput.getvalue(), job.userid, statinfo.st_mtime, True, region = region, typeid = typeid)
            csvOutput.close()
            evt = UpdateUploadEvent(typename = str(type), success = True)
            wx.PostEvent(job.win, evt)
        except Excetion e:
            print e

    config['last_upload_time'] = highest_timestamp


        
        
        
    upcount += check_csv(dirl)


    evt = DoneUploadEvent(count = upcount, success = True)
    wx.PostEvent(job.win, evt)


    return upcount
