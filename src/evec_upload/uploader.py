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

from threading import Thread
from Queue import Queue
import evecache

from evec_upload.config import Config

def get_uploader(cfg, updcb):
    config = Config()
    upl = UploaderEC(identity=0, donecb=updcb)
    upl.start()

#ec2 = evec_upload.uploader.UploaderEC(identity=0, queue=upl.queue, donecb=updcb)
#ec2.host = "musuca.baka:8080"
#ec2.name = "EC2"
#ec2.start()

    if len(cfg.config_obj.get('em_token', "")):
        em = UploaderEM(identity=config['em_token'], donecb=updcb)
        em.start()
        mult = UploaderMulti()
        mult.add(upl)
        mult.add(em)
        upl = mult

    return upl


class UploaderPayload(object):
    def __init__(self, body="", regionid=0, typeid=0, timestamp=None,):
        self.body = body
        self.regionid = regionid
        self.typeid = typeid
	self.timestamp = timestamp


class UploaderMulti(object):
    def __init__(self):
	self.uploaders = []

    def add(self, uploader):
	self.uploaders.append(uploader)

    def do(self, orders, regionid, typeid, timestamp,):
	for upl in self.uploaders:
            upl.do(orders, regionid, typeid, timestamp)

    def trigger(self, payload):
	for upl in self.uploaders:
            upl.trigger(payload)

    def start(self):
        pass


class UploaderThread(Thread):
    def __init__(self, queue=None, donecb=None, identity=None):
        config = Config()
        Thread.__init__(self)
        self.setDaemon(True)

        self.donecb = donecb
        self.identity = identity

        self.maxthreads = int(config['upl_maxthreads'])
        self.scale = int(config['upl_scale'])
        self.helper = []

        self.queue = queue
	if not self.queue:
            self.queue = Queue()

    def done(self,payload,success):
        if self.donecb:
            self.donecb(typename = "%s: type %s, bytes %s, qsize %i" % (self.name, payload.typeid, len(payload.body), self.queue.qsize(),), success = success)
        
    def trigger(self, payload):
        if not len(payload.body):
            self.done(payload, False)
            return False

        self.queue.put(payload)

#        print "%s: %i max, %i have, %i scale" % (self.name, self.maxthreads, len(self.helper), self.scale,)
        if self.maxthreads <= len(self.helper)+1:
            return

        tf = int(self.queue.qsize() / self.scale)
        if tf <= len(self.helper):
            return

        print "%s: starting new helper thread" % (self.name,)
        ht = self.__class__(queue=self.queue, donecb=self.donecb, identity=self.identity)
        ht.name += str(len(self.helper)+2)
        if not len(self.helper):
            self.name += "1"
        self.helper.append(ht)
        ht.start()

    def run(self):
        while True:
            payload = self.queue.get()
#            try:
            self.do_upload(payload)
#            except Exception as e:
#                sys.stderr.write(e.message)

    def do_upload(self, payload):
        raise NotImplemented



class UploaderEC(UploaderThread):
    def __init__(self, queue=None, donecb=None, identity=0):
        UploaderThread.__init__(self, queue=queue, donecb=donecb, identity=identity)
        self.host = "eve-central.com"
        self.name = "EC"

    def do(self, orders, regionid, typeid, timestamp,):
        csvOutput = StringIO()
        print >>csvOutput, "CACHE GENERATED FILE HEADER"
        for order in orders:
            print >>csvOutput, order.toCsv()
	lines = csvOutput.getvalue()
        csvOutput.close()

        payload = UploaderPayload(lines, regionid, typeid, timestamp)

        if not lines:
            self.done(payload, False)
            return False

	self.trigger(payload)
	

    def do_upload(self, payload):
#        print "Upload of ",payload.typeid,payload.regionid

        submitdata = urllib.urlencode({'typename' : "", 'data' : payload.body,
                                   'userid': self.identity, 
                                   'timestamp': payload.timestamp, 'cache': True, 
                                   'region' : payload.regionid, 'typeid' : payload.typeid})

        import httplib
        conn = httplib.HTTPConnection(self.host)
        conn.request( "POST",
                      "/datainput.py/inputdata",
                      submitdata,
                      {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'eve-central.com',
            } )
        response = conn.getresponse()
        success = ( response.status == 200 )
        if not success:
            print response.status, response.reason
            print response.read()
        conn.close()

        self.done(payload, success)
        return success


class UploaderEM(UploaderThread):
    def __init__(self, queue=None, donecb=None, identity=""):
        UploaderThread.__init__(self, queue=queue, donecb=donecb, identity=identity)
        self.developer_key = "E23FA1C32D180BCE35F5C"
        self.host = "eve-metrics.com"
        self.name = "EM"

    def do(self, orders, regionid, typeid, timestamp,):
        csvOutput = StringIO()
        for order in orders:
            print >>csvOutput, order.toCsv()+",cache"
	data = csvOutput.getvalue()
	csvOutput.close()

        import re
        rex = re.compile("\.000,")
        lines = rex.sub(",", data)
        rex = re.compile("\n")
        lines = rex.sub("\r\n", lines)
#        print lines

        payload = UploaderPayload(lines, regionid, typeid, timestamp)

        if not lines:
            self.done(payload, False)
            return False

	self.trigger(payload)
 
    def do_upload(self, payload):
        import datetime
        timestamp = datetime.datetime.utcfromtimestamp(payload.timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
#        target = ('/api/upload_orders.xml' if data[0] == 'GetOrders' else '/api/upload_history.xml')
        # Compute the hash of the body
        import hashlib
        hasher = hashlib.sha1()
        hasher.update(self.developer_key)
        hasher.update(timestamp)
        body_hash = hasher.hexdigest()
    
   
        # Fire off a HTTP request
        import httplib
        conn = httplib.HTTPConnection(self.host)
        conn.request( "POST",
                      "/api/upload_orders.xml",
                      urllib.urlencode( {
              'token' : self.identity,
              'developer_key' : self.developer_key,
              'version' : '0.23',
              'hash' : body_hash,
              'generated_at' : timestamp,
              'log' : payload.body
              } ),
                      {
            'Content-Type': 'application/x-www-form-urlencoded'
            } )
        response = conn.getresponse()
        success = (response.status == 200)
        if not success:
            print response.status, response.reason
            print response.read()
        conn.close()

	self.done(payload, success)
        return success
    
