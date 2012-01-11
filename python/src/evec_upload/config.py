# python
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


import sys
import os
import pickle
import time
import os.path
import re
import threading


class Config(object):

    CONFIG_VERSION = '2.1.0.1'
    LOCK = threading.RLock()
    CONFIG_OBJ = {}

    def __init__(self):
        self.config_obj = Config.CONFIG_OBJ

        self.filename = ""
        try:
            import wx
            sp = wx.StandardPaths.Get()
            wx.GetApp().SetAppName("EVE-Central MarketUploader")
            path = sp.GetUserLocalDataDir()

            try:
                os.mkdir(path)
            except:
                pass

            self.filename = os.path.normpath( os.path.join( path, 'data.pickle' ) )
        except:
            pass

        if not len(self.filename):
            try:
                self.filename = os.path.normpath( os.path.join( os.environ['HOME'], '.contribtastic.pickle' ) )
            except:
                pass

        if len(self.config_obj) <= 0: # This is a blank config, reload it
            self.reinit = self.load_config()
        else:
            self.reinit = 0

    def __getitem__(self, key):
        Config.LOCK.acquire()
        i = self.config_obj[key]
        Config.LOCK.release()
        return i

    def __contains__(self, key):
        Config.LOCK.acquire()
        i = key in self.config_obj
        Config.LOCK.release()
        return i

    def __setitem__(self, key, value):
        Config.LOCK.acquire()
        ret =  self.config_obj[key] = value
        self.save_config()
        Config.LOCK.release()
        return ret

    def __len__(self):
        return len(self.config_obj)

    def __delitem__(self, key):
        del self.config_obj[key]


    def default_data(self):
        self.config_obj.update({ 'version' : Config.CONFIG_VERSION,
                                 'backup' : False,
                                 'upl_maxthreads' : 1,
                                 'upl_scale' : 100,
                                 'character_name' : 'Anonymous',
                                 'character_id' : 0,
                            })

    def save_config(self):
        file = open( self.filename, "w")
        pickle.dump(self.config_obj, file)
        file.close()

    def load_config(self):

        ret = 0
        file = None
        try:
            file = open( self.filename, "r")
            ret = 0
            self.config_obj.update(pickle.load(file))
        except Exception, e:
            print e
            if file:
                file.close()
                file = None

            self.default_data()
            self.save_config()
            return -1
        finally:
            if file:
                file.close()

        if self.config_obj['version'] != Config.CONFIG_VERSION:
            self.default_data()
            self.save_config()
            ret = -1

        return ret
