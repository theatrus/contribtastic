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

from upload import *
from taskbar import *

import wx
import pickle
import os
import sys
import images
import urllib

config_obj = {}

class MainFrame(wx.Frame):
    MENU_SETTINGS = wx.NewId()
    MENU_ABOUT = wx.NewId()
    MENU_SCANNOW = wx.NewId()

    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(150, 150), style = wx.CAPTION | wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CLOSE_BOX  )# size=(350, 150))
        
        try:
            check_protocol()
            r = check_client()
            if r is not True:
                dlg = wx.MessageDialog(self, 'Client outdated! New version ' + `r` + ' available! Visit EVE-Central.com to update!', 'Outdated client',
                                       wx.OK | wx.ICON_ERROR
                                       )
                dlg.ShowModal()
                dlg.Destroy()
                os.system("explorer http://eve-central.com")
                sys.exit(-1)

        except IOError:
            dlg = wx.MessageDialog(self, 'The network appears to be down. I cannot reach EVE-central.com. Check your firewall settings or internet connection',
                                   'Can\'t communicate with EVE-Central.com',
                                   wx.OK | wx.ICON_ERROR
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            sys.exit(-1)
            


        # Set icon

        self.SetIcon(images.getIconIcon())

        # Task Bar

        self.tbicon = TaskBarIcon(self)


        # Create the menubar
        menuBar = wx.MenuBar()

        # and a menu 
        menu = wx.Menu()

        # option menu
        optmenu = wx.Menu()

        # help menu
        helpmenu = wx.Menu()
        

        # add an item to the menu, using \tKeyName automatically
        # creates an accelerator, the third param is some help text
        # that will show up in the statusbar
        menu.Append(self.MENU_SCANNOW, "S&can now...")

        menu.AppendSeparator()
        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit")
        

        optmenu.Append(self.MENU_SETTINGS, "&Set/Locate EVE Directory...")

        helpmenu.Append(self.MENU_ABOUT, "&About")
        
        # bind the menu event to an event handler
        self.Bind(wx.EVT_MENU, self.OnTimer, id=self.MENU_SCANNOW)
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnLocateDir, id=self.MENU_SETTINGS)
        self.Bind(wx.EVT_MENU, self.OnAbout, id = self.MENU_ABOUT)

        self.Bind(wx.EVT_CLOSE, self.OnTimeToClose)
        
        # and put the menu on the menubar
        menuBar.Append(menu, "&File")
        menuBar.Append(optmenu, "&Options")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)

        self.CreateStatusBar()
        self.SetStatusText("Idle")

        # Now create the Panel to put the other controls on.
        panel = wx.Panel(self)

        # and a few controls
#        text = wx.StaticText(panel, -1, "EVE-Central.com MarketUploader")

        self.pathtext = wx.TextCtrl(panel, -1, "Please wait...")
        self.pathtext.Enable(False)
        self.pathtext_l = wx.StaticText(panel, -1, "Using folder:")
        self.uploadtext = wx.StaticText(panel, -1, "")

        self.uploads = 0
        self.scans = 0


        self.motd = wx.TextCtrl(panel, -1,
                                "",
                      size=(200, 100), style=wx.TE_MULTILINE|wx.TE_READONLY)

        self.update_motd()
        
        #text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        btn = wx.Button(panel, -1, "Quit")


        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnTimeToClose, btn)



        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer_path = wx.BoxSizer(wx.HORIZONTAL)
        sizer_path.Add(self.pathtext_l, 0, wx.ALL|wx.EXPAND, 1)
        sizer_path.Add(self.pathtext, 1, wx.ALL|wx.EXPAND, 1)
        sizer.Add(sizer_path, 0, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.uploadtext, 0, wx.ALL, 1)

        sizer.Add(self.motd, 4, wx.ALL|wx.EXPAND, 1)
        
        sizer.Add(btn, 0, wx.ALL|wx.EXPAND, 1)
        
        panel.SetSizer(sizer)
        panel.Layout()


        self.timer = wx.Timer(self)
        self.timer.Start(60000)

        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(EVT_UPDATE_UPLOAD, self.OnUploadUpdate)
        self.Bind(EVT_DONE_UPLOAD, self.OnUploadDone)

        self.load_infowidgets()

    def load_infowidgets(self):
        global config_obj
        path = config_obj['evepath']
        self.pathtext.SetLabel( path)
        self.uploadtext.SetLabel("Uploads so far: " + `self.uploads` + "  Scans so far: " + `self.scans`)


    def OnTimeToClose(self, evt):
        """Event handler for the button click."""
        self.tbicon.OnTaskBarQuit(None)
        self.Close()
        sys.exit(0)

    def OnUploadUpdate(self, evt):
        global config_obj
        self.uploads = self.uploads + 1
        self.SetStatusText("Uploaded " + evt.typename)
        self.load_infowidgets()

    def OnUploadDone(self, evt):
        global config_obj
        self.load_infowidgets()
        if evt.success == True:
            self.SetStatusText("Idle - Uploaded " + `evt.count` + " last run")
        else:
            self.SetStatusText("Error scanning directory! Check EVE path!")

    def OnAbout(self, evt):
        global ProgramVersionNice
        dlg = wx.MessageDialog(self, 'EVE-Central.com MarketUploader ' + ProgramVersionNice +"\n(c) 2006 Yann Ramin. All Rights Reserved.\n\nSee EVE-Central.com for the latest updates and information.", 'About',
                                       wx.OK
                               )
        dlg.ShowModal()
        dlg.Destroy()


    def OnTimer(self, evt):
        global config_obj
        self.SetStatusText("Uploading...")
        th = UploadThread(config_obj['evepath'], self)
        th.start()
        self.scans += 1

        
    def OnLocateDir(self, evt):
        global config_obj
        dlg = wx.DirDialog(self, "Please locate the root of your EVE install:",
                          style=wx.DD_DEFAULT_STYLE)

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it. 
        if dlg.ShowModal() == wx.ID_OK:
            config_obj['evepath'] = dlg.GetPath()
            config_obj['path_set'] = True
        save_config()
        self.load_infowidgets()


    def update_motd(self):


        motdf = urllib.urlopen("http://eve-central.com/motd.txt")
        motd = ""
        for line in motdf.readlines():
            motd += line
        motdf.close()

        self.motd.WriteText(motd)
            


def default_data():
    global config_obj

    config_obj = { 'version' : '1.0',
                   'path_set' : False,
                   'evepath' : 'C:\\Program Files\\CCP\\EVE\\',
                   'character_name' : 'Anonymous'
                   }

def save_config():
    global config_obj


    
    sp = wx.StandardPaths.Get()
    wx.GetApp().SetAppName("EVE-Central MarketUploader")
    path = sp.GetUserLocalDataDir()


    try:
        os.mkdir(path)
    except:
        pass
    
    file = open(path+"\\data.pickle", "w")

    pickle.dump(config_obj, file)

    file.close()


def load_config():
    global config_obj

    sp = wx.StandardPaths.Get()
    wx.GetApp().SetAppName("EVE-Central MarketUploader")
    path = sp.GetUserLocalDataDir()
    file = None
    try:
        file = open(path+"\\data.pickle", "r")
    except:
        default_data()
        save_config()
        return
    

    config_obj = pickle.load(file)
    

    file.close()

class EVEc_Upload(wx.App):
    def OnInit(self):
        global config_obj

        load_config()
        
        
        frame = MainFrame(None, "EVE-Central.com MarketUploader")
        self.SetTopWindow(frame)

        frame.Show(True)
        return True
        
app = EVEc_Upload(redirect=False)
app.MainLoop()

