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
import time

from threading import Thread
from Queue import Queue
import evecache
from evec_upload.config import Config, documents_path


ProgramVersion = 2000
ProgramVersionNice = "2.0"
CheckVersion = 1031


class UploadPayload(object):
    def __init__(self, path, uploader, donecb):
        self.path = path
        self.uploader = uploader
        self.donecb = donecb

class UploadThread(Thread):
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
                upload_data(payload)
            except Exception as e:
                sys.stderr.write(e)



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


def make_csv_file(orders, region, typeid, timestamp):
    config = Config()
    filename = os.path.join(documents_path, str(region) + "-" + str(typeid) + ".csv")
    with open(filename, 'w') as f:
        print >>f, orders
    return


# Local cache of currently seen files
seen = {}
def upload_data(job):

    dirl = []
    upcount = 0

    firstrun = 0
    if not seen:
	firstrun = 1

    try:
        dirl = os.listdir(job.path)
    except:
        if job.donecb:
            self.donecb(count = upcount, success = False)
        return None

    config = Config()

    highest_timestamp = config['last_upload_time']
    one_hour_ago = time.time() - 60*60
    if highest_timestamp < one_hour_ago:
        highest_timestamp = one_hour_ago

    start_ts = highest_timestamp
    print "UPLOAD START: TIMESTAMP CHECK IS > ",start_ts

    for item in dirl:
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

        print item, statinfo.st_mtime, highest_timestamp

        try:
            market_parser = evecache.MarketParser(str(item))
            if market_parser.valid() == True:
#                print "Valid"
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

    config['last_upload_time'] = highest_timestamp

    if job.donecb:
        job.donecb(count = upcount, success = True)

    return upcount
