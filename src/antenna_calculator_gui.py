#! /usr/bin/python3

import wx
import wx.lib.mixins.inspection as wit
from gui_frame import GFrame


def main():
 
        app = wit.InspectableApp()
        GUIFrame = GFrame(None, title='Antenna Calculator GUI')
        GUIFrame.Show()
        app.MainLoop()


if __name__ == '__main__':
    main()