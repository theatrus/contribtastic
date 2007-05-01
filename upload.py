#    EVE-Central.com MarketUploader
#    Copyright (C) 2005-2006 Yann Ramin
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

import wx
import wx.lib.newevent

from threading import Thread


ProgramVersion = 1020
ProgramVersionNice = "1.2"
CheckVersion = 1000

(UpdateUploadEvent, EVT_UPDATE_UPLOAD) = wx.lib.newevent.NewEvent()
(DoneUploadEvent, EVT_DONE_UPLOAD) = wx.lib.newevent.NewEvent()


class UploadThread(Thread):
    def __init__(self, path, win, userid):
        Thread.__init__(self)
        self.path = path
        self.win = win
        self.userid = userid
        self.setDaemon(False)
    def run(self):
        upload_data(self.path, self.win,self.userid)


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

    
def upload_data(path, win, userid):

    dirl = []
    upcount = 0
    
    try:
        dirl = os.listdir(path)
    except:
        evt = DoneUploadEvent(count = upcount, success = False)
        wx.PostEvent(win, evt)

        return None



    
    for item in dirl:

        if item[-3:] == "txt" and item != "readme.txt":
            # Found file
            upcount = upcount + 1
            typename = None
            try:
                s = item.split(' - ')
                typename = s[1]
            except:
                # This isn't a valid item it seems like
                continue
            
            fileh = open(path+'\\'+item)
            lines = ""
            linecount = 0
            for line in fileh.readlines():
                line.replace("\r", "")
                lines = lines + line
                linecount = linecount + 1

            fileh.close()
            
            submitdata = urllib.urlencode({'typename' : typename, 'data' : lines, 'userid': userid})
            
            h = urllib.urlopen("http://eve-central.com/datainput.py/inputdata", submitdata)
            kk = h.readlines()
            for llk in kk:
                print llk
                
                
                
            h.close()
            evt = UpdateUploadEvent(typename = typename, success = True)
            wx.PostEvent(win, evt)
            os.remove(path+'\\'+item)


            
    evt = DoneUploadEvent(count = upcount, success = True)
    wx.PostEvent(win, evt)


    return upcount





if __name__ == "main":
    upload_data()
