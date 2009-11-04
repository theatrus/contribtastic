#!/usr/bin/env python
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
import images
import sys

class TaskBarIcon(wx.TaskBarIcon):
    TBMENU_RESTORE = wx.NewId()
    TBMENU_CLOSE   = wx.NewId()
    TBMENU_QUIT  = wx.NewId()
    TBMENU_REMOVE  = wx.NewId()

    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame

        # Set the image
        icon = self.MakeIcon(images.getIconImage())
        self.SetIcon(icon, "Contribtastic!")
        self.imgidx = 1

        # bind some events
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarToggle)
        self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarRemove, id=self.TBMENU_REMOVE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarQuit, id=self.TBMENU_QUIT)

    def __del__(self):
        self.RemoveIcon()

    def CreatePopupMenu(self):
        """
        This method is called by the base class when it needs to popup
        the menu for the default EVT_RIGHT_DOWN event.  Just create
        the menu how you want it and return it from this function,
        the base class takes care of the rest.
        """
        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, "Restore Contribtastic")
        menu.Append(self.TBMENU_CLOSE,   "Hide Contribtastic")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_REMOVE, "Remove from taskbar")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_QUIT, "Quit Contribtastic")
#        menu.Append(self.TBMENU_CHANGE, "Change the TB Icon")

        return menu


    def MakeIcon(self, img):
        """
        The various platforms have different requirements for the
        icon size...
        """
        if "wxMSW" in wx.PlatformInfo:
            img = img.Scale(16, 16)
        elif "wxGTK" in wx.PlatformInfo:
            img = img.Scale(22, 22)
        # wxMac can be any size upto 128x128, so leave the source img alone....
        icon = wx.IconFromBitmap(img.ConvertToBitmap() )
        return icon


    def OnTaskBarActivate(self, evt):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()


    def OnTaskBarToggle(self, evt):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
            self.frame.Raise()
        else:
            self.frame.Show(False)



    def OnTaskBarClose(self, evt):
        self.frame.Show(False)

    def OnTaskBarQuit(self, evt):
        self.RemoveIcon()
        if evt is not None:
            self.frame.Close()
        sys.exit(0)

    def OnTaskBarChange(self, evt):
        pass


    def OnTaskBarRemove(self, evt):
        self.RemoveIcon()
