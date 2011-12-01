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

#import wx
#import wx.lib.newevent

#from evec_upload.config import Config


ProgramVersion = 2000
ProgramVersionNice = "2.1"
CheckVersion = 1031

from time import sleep
from sys import argv

#import wx
#import wx.lib.newevent

#(UpdateUploadEvent, EVT_UPDATE_UPLOAD) = wx.lib.newevent.NewEvent()
#(DoneUploadEvent, EVT_DONE_UPLOAD) = wx.lib.newevent.NewEvent()

#fail
#        evt = DoneUploadEvent(count = upcount, success = False)
#        wx.PostEvent(job.win, evt)

#+1
#                evt = UpdateUploadEvent(typename = str(typeid), success = True)
#                wx.PostEvent(job.win, evt)

# done
#    evt = DoneUploadEvent(count = upcount, success = True)
#    wx.PostEvent(job.win, evt)

def donecb(count, success):
    print "DONE: %i, %s" % (count, success,)

def updcb(typename, success):
    print "UPD: %s, %s" % (typename, success,)

from evec_upload.uploader import get_uploader
from evec_upload.config import Config
config = Config()
upl = get_uploader(config, updcb)

from evec_upload.upload import UploadPayload, upload_data
uc = 0
while True:
    for path in argv[1:]:
        print "starting ", path
	job = UploadPayload(path, upl, donecb=donecb)
        upc = upload_data(job)
	uc += upc
        print "done: %i -> %i total" % (upc, uc,)

        print "sleeping 1"
        sleep(1)

#    raise TESTING
    print "sleeping 10"
    sleep(10)

