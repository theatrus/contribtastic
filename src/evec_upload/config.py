import sys
import wx
import os
import pickle


def default_location():
    if sys.platform == 'win32':
        from win32com.shell import shell, shellcon
        document_folder = os.path.join( shell.SHGetFolderPath( 0, shellcon.CSIDL_PERSONAL, 0, 0 ), 'Eve', 'logs', 'Marketlogs' )
    elif sys.platform == 'darwin':
        from Carbon import Folder, Folders
        folderref = Folder.FSFindFolder( Folders.kUserDomain, Folders.kPreferencesFolderType, False )
        document_folder = os.path.join( folderref.as_pathname(), 'Eve Online Preferences', 'p_drive', 'My Documents', 'EVE', 'logs', 'MarketLogs' )
    else:
        document_folder = '' # don't know what the linux client has

        document_folder = os.path.normpath( document_folder )
        return document_folder


class Config(object):




    def __init__(self):
        self.config_obj = {}
        self.reinit = self.load_config()


    def __getitem__(self, key):
        return self.config_obj[key]

    def __setitem__(self, key, value):
        ret =  self.config_obj[key] = value
        self.save_config()
        return ret

    def __len__(self):
        return len(self.config_obj)

    def __delitem__(self, key):
        del self.config_obj[key]


    def default_data(self):

        loc = default_location()
        loc = [loc]

        self.config_obj = { 'version' : '2.0',
                       'path_set' : False,
                       'backup' : 'backup',
                       'evepath' : loc,
                       'character_name' : 'Anonymous',
                       'character_id' : 0
                       }

    def save_config(self):

        sp = wx.StandardPaths.Get()
        wx.GetApp().SetAppName("EVE-Central MarketUploader")
        path = sp.GetUserLocalDataDir()


        try:
            os.mkdir(path)
        except:
            pass

        file = open( os.path.normpath( os.path.join( path, 'data.pickle' ) ), "w")

        pickle.dump(self.config_obj, file)

        file.close()



    def load_config(self):


        sp = wx.StandardPaths.Get()
        wx.GetApp().SetAppName("EVE-Central MarketUploader")
        path = sp.GetUserLocalDataDir()
        file = None
        try:
            file = open( os.path.normpath( os.path.join( path, 'data.pickle' ) ), "r")
        except:
            self.default_data()
            self.save_config()
            return

        ret = 0
        self.config_obj = pickle.load(file)
        if self.config_obj['version'] != '2.0':
            self.default_data()
            self.save_config()
            ret = -1

        file.close()

        return ret
