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


import wx
import pickle
import os
import sys
import images
import urllib

from evec_upload.config import Config

class OptionDialog(wx.Dialog):
    def __init__(self, parent):
        config = Config()

        wx.Dialog.__init__(self, parent, -1, "Options", style = wx.DEFAULT_DIALOG_STYLE)

        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, -1, "Configure how the Uploader operates")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)



        self.backup = wx.CheckBox(self, -1, "Create CSV dumps the uploaded data")
        self.backup.SetValue(config['backup'])
        sizer.Add(self.backup, 0, wx.ALL, 5)

        self.suggest = wx.CheckBox(self, -1, "Offer suggestions of what can be uploaded")
        sizer.Add(self.suggest, 0, wx.ALL, 5)

        self.anon_cb = wx.CheckBox(self, -1, "Anonymous login - no username")
        self.Bind(wx.EVT_CHECKBOX, self.OnAnonCb, self.anon_cb)
        sizer.Add(self.anon_cb, 0, wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)


        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Username:")

        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.uname = wx.TextCtrl(self, -1, "", size=(80,-1))

        box.Add(self.uname, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Password: ")

        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.passwd = wx.TextCtrl(self, -1, "", size=(80,-1), style=wx.TE_PASSWORD)

        box.Add(self.passwd, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)


        btnsizer = wx.StdDialogButtonSizer()


        btn = wx.Button(self, wx.ID_OK)

        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)

        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

        char_name = config['character_name']

        if char_name == "Anonymous":
            self.anon_cb.SetValue(True)
            self.uname.Enable(False)
            self.passwd.Enable(False)
        else:
            self.uname.SetValue(char_name)


    def OnAnonCb(self, evt):
        if self.uname.IsEnabled():
            self.uname.Enable(False)
        else:
            self.uname.Enable(True)
        if self.passwd.IsEnabled():
            self.passwd.Enable(False)
        else:
            self.passwd.Enable(True)
