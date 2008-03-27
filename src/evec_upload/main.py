# python
#    EVE-Central.com MarketUploader
#    Copyright (C) 2005-2008 Yann Ramin
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

from evec_upload.upload import *
from evec_upload.taskbar import *
import evec_upload.login
import evec_upload.options

from evec_upload.config import Config

import wx
import pickle
import os
import sys
import images
import urllib




class MainFrame(wx.Frame):
    MENU_SETTINGS = wx.NewId()
    MENU_ABOUT = wx.NewId()
    MENU_SCANNOW = wx.NewId()
    MENU_LOGIN = wx.NewId()

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


        # Load config
        c = Config()
        r = c.reinit
        if r == -1:
            dlg = wx.MessageDialog(self, """The uploader client configuration has been reset since an old configuration file was found.
            Please check your configuration (such as user login and EVE path).""", 'Client Upgrade', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()







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


        optmenu.Append(self.MENU_SETTINGS, "L&ocate EVE Market Export directory...")
        optmenu.Append(self.MENU_LOGIN, "&Login to your EVE-central.com account...")
        helpmenu.Append(self.MENU_ABOUT, "&About")

        # bind the menu event to an event handler
        self.Bind(wx.EVT_MENU, self.OnTimer, id=self.MENU_SCANNOW)
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnLocateDir, id=self.MENU_SETTINGS)
        self.Bind(wx.EVT_MENU, self.OnAbout, id = self.MENU_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnLogin, id = self.MENU_LOGIN)

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

        self.pathtext = wx.StaticText(panel, -1, "Please wait...")
#        self.pathtext.Enable(False)
        self.pathtext_l = wx.StaticText(panel, -1, "Using folder:  ")

        self.usertext_l = wx.StaticText(panel, -1, "Character name:  ")
        self.usertext = wx.StaticText(panel, -1, "...")

        self.uploadtext = wx.StaticText(panel, -1, "")

        config_obj = Config()

        if config_obj['character_id'] == 0:
            self.uploads = long(0)
        else:
            self.uploads = get_charuploads(config_obj['character_id'])
        self.scans = 0


        self.motd = wx.TextCtrl(panel, -1,
                                "",
                                size=(200, 100), style=wx.TE_MULTILINE|wx.TE_READONLY)

        self.update_motd()

        #text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))



        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer_path = wx.FlexGridSizer(2,2)
        #--
        sizer_path.Add(self.pathtext_l, 2, wx.EXPAND|wx.ALL, 1)
        sizer_path.Add(self.pathtext, 0, wx.ALL|wx.EXPAND, 1)

        sizer_path.Add(self.usertext_l, 2, wx.EXPAND|wx.ALL, 1)
        sizer_path.Add(self.usertext, 0, wx.ALL|wx.EXPAND, 1)

        #--
        sizer.Add(sizer_path, 0, wx.EXPAND | wx.ALL, 1)
        line = wx.StaticLine(panel, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        sizer.Add(self.uploadtext, 0, wx.ALL, 1)

        sizer.Add(self.motd, 4, wx.ALL|wx.EXPAND, 1)



        panel.SetSizer(sizer)
        panel.Layout()


        self.timer = wx.Timer(self)
        self.timer.Start(60000)

        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(EVT_UPDATE_UPLOAD, self.OnUploadUpdate)
        self.Bind(EVT_DONE_UPLOAD, self.OnUploadDone)

        self.load_infowidgets()

    def load_infowidgets(self):
        config_obj = Config()

        path = config_obj['evepath'][0]
        self.pathtext.SetLabel( path)
        self.usertext.SetLabel(config_obj['character_name'])
        self.uploadtext.SetLabel("Uploads so far: " + `self.uploads`[:-1] + "  Scans so far: " + `self.scans`)


    def OnLogin(self,evt):

        config_obj = Config()

        dlg = evec_upload.login.LoginDialog(self, config_obj['character_name'])
        r = dlg.ShowModal()
        if r == wx.ID_OK:
            if dlg.anon_cb.IsChecked():
                config_obj['character_name'] = "Anonymous"
                config_obj['character_id'] = 0

                self.load_infowidgets()
            else:
                v = get_charid(dlg.uname.GetValue(), dlg.passwd.GetValue())
                if v == -1:
                    dlge = wx.MessageDialog(self, 'User login information incorrect. Using old value', 'Bad login',
                                            wx.OK | wx.ICON_ERROR
                                            )
                    dlge.ShowModal()
                    dlge.Destroy()
                else:
                    config_obj['character_id'] = v
                    config_obj['character_name'] = dlg.uname.GetValue()
                    self.load_infowidgets()


        else:
            pass
        dlg.Destroy()

    def OnTimeToClose(self, evt):
        """Event handler for the button click."""
        self.tbicon.OnTaskBarQuit(None)
        self.Close()
        sys.exit(0)

    def OnUploadUpdate(self, evt):

        self.uploads = self.uploads + 1
        self.SetStatusText("Uploaded " + evt.typename)
        self.load_infowidgets()

    def OnUploadDone(self, evt):

        self.load_infowidgets()
        if evt.success == True:
            self.SetStatusText("Idle - Uploaded " + `evt.count` + " last run")
        else:
            self.SetStatusText("Error scanning directory! Check EVE path!")

    def OnAbout(self, evt):
        global ProgramVersionNice
        dlg = wx.MessageDialog(self, 'EVE-Central.com MarketUploader ' + ProgramVersionNice +"\n(c) 2006-2007 Yann Ramin. All Rights Reserved.\n\nSee EVE-Central.com for the latest updates and information.", 'About',
                               wx.OK
                               )
        dlg.ShowModal()
        dlg.Destroy()


    def OnTimer(self, evt):
        config_obj = Config()
        self.SetStatusText("Uploading...")
        job = UploadPayload(config_obj['evepath'][0], self, config_obj['character_id'], config_obj['backup'])

        th = UploadThread(job)
        th.start()

        self.scans += 1

    def OnLocateDir(self, evt):

        config_obj = Config()

        dlg = wx.DirDialog(self, "Please locate the market export directory (Documents and Settings\[user]\My Documents\EVE\logs\Marketlogs)..:",
                           style=wx.DD_DEFAULT_STYLE,
                           defaultPath=default_location() )

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it.
        if dlg.ShowModal() == wx.ID_OK:
            config_obj['evepath'] = dlg.GetPath()
            config_obj['path_set'] = True

        self.load_infowidgets()


    def update_motd(self):


        motdf = urllib.urlopen("http://eve-central.com/motd.txt")
        motd = ""
        for line in motdf.readlines():
            motd += line
        motdf.close()

        self.motd.WriteText(motd)


def get_charid(user, passwd):
    data = urllib.urlencode({'username':user,'password':passwd})
    cv = urllib.urlopen("http://eve-central.com/datainput.py/userlogin", data)
    num = cv.readline().strip()
    cv.close()
    return long(num)


def get_charuploads(userid):
    data = urllib.urlencode({'userid':userid})
    cv = urllib.urlopen("http://eve-central.com/datainput.py/usercount", data)
    num = cv.readline().strip()
    cv.close()
    return long(num)


class EVEc_Upload(wx.App):
    def OnInit(self):

        frame = MainFrame(None, "EVE-Central.com MarketUploader")
        self.SetTopWindow(frame)


        try:
            if sys.argv[1] == "-hide":
                frame.Show(False)
            else:
                frame.Show(True)
        except:
            frame.Show(True)


        return True

if __name__ == "__main__":
    app = EVEc_Upload(redirect=False)
    app.MainLoop()