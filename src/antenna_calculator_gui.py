#! /usr/bin/python3


##--------------------------------------------------------------------\
#   AntennaCalculator - GUI branch  antenna_calculator_gui.py
#   
#   This is the main entry point of the calculator GUI. Refer to the 
#   README for information on format and arguments. 
##--------------------------------------------------------------------\

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