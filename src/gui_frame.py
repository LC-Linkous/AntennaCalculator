#! /usr/bin/python3

##--------------------------------------------------------------------\
#   Antenna Calculation and Autotuning Tool (with modifications)
#   Main class for design, import, or editing basic antenna/fss designs
#   + the class for the notebook with pages of design options
#   + the class for displaying detail text on notebook page 
#   + Classes for interfacing with the internal antenna calculator
#       Contains widgets for rectangular patch antenna input,
#       + the half wave dipole and quarter wave monopole page classes
#
#
#   Grouped together to keep the AntennaCalculator project small, 
#   and sample the AntennaCAT integration. 
#   This many classes together is kinda gross, but it's for demo purposes only.
#
#
#   Author(s): Lauren Linkous (LINKOUSLC@vcu.edu)
#   Last update: June 5, 2024
##--------------------------------------------------------------------\

# system level imports
import os
import time
import wx
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

# local imports
from draw_antenna import CalculateAndDraw
from calculator_interface import CalculatorInterface


# default frame/panel sizes
# constants
WIDTH = 1050
HEIGHT = 710
PANEL_WIDTH = 400
MAIN_BACKGROUND_COLOR='Light Blue'
INPUT_BOX_WIDTH = 100

# dictionary for calculator integration
ANTENNA_TYPE_DICT = {'Rectangular Patch': 'rectangular_patch',
    'Half Wave Dipole': 'half_wave_dipole',
    'Quarter Wave Monopole': 'quarter_wave_monopole'}

#######################################################################
# Classes for basic GUI frame creation
#######################################################################

class GFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent=parent, title=title, size=(WIDTH, HEIGHT))
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # add generator page
        self.panel_design = DesignPage(self)

        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.panel_design, 0, wx.EXPAND)
        self.SetSizer(self.mainSizer)

    #btn events called from children
    def onClose(self, evt=None):
        self.Destroy()


#######################################################################
# Classes for modular GUI frame elements
#######################################################################   
class DesignPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.parent = parent
        self.SetBackgroundColour(MAIN_BACKGROUND_COLOR)

        #canvas
        boxCanvasPreview = wx.StaticBox(self, label='Preview')
        self.figure = matplotlib.figure.Figure(figsize=(5,5), tight_layout=False)
        self.axes = self.figure.add_subplot(111, projection="3d")
        self.canvas = FigureCanvas(boxCanvasPreview, -1, self.figure)
        self.navToolbar = NavigationToolbar2Wx(self.canvas)

        #design options notebook creation
        boxDesignOptions = wx.StaticBox(self, label='Design Options')
        self.notebook_design = DesignNotebook(boxDesignOptions, self)

        #summary box
        boxDesignSummary = wx.StaticBox(self, label='Design Summary:')
        self.designSummaryTxt = MessageDisplay(boxDesignSummary)
        

        # btn sizer
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.AddStretchSpacer()
        
        # summary sizer
        summarySizer = wx.BoxSizer(wx.VERTICAL)
        summarySizer.AddSpacer(10)
        summarySizer.Add(self.designSummaryTxt, 1, wx.ALL|wx.EXPAND, border=5)
        boxDesignSummary.SetSizer(summarySizer)

        # 'left side sizer'
        boxDesignSizer = wx.BoxSizer(wx.VERTICAL)
        boxDesignSizer.AddSpacer(5)
        boxDesignSizer.Add(self.notebook_design, 0, wx.ALL | wx.EXPAND, border=15)
        boxDesignOptions.SetSizer(boxDesignSizer)

        #preview sizer
        # 'right side sizer'
        canvasSizer = wx.BoxSizer(wx.VERTICAL)
        canvasSizer.AddSpacer(20)
        canvasSizer.Add(self.canvas, 0, wx.CENTER|wx.EXPAND, border=15)  #the 3d graph
        canvasSizer.Add(self.navToolbar, 0,  wx.CENTER)
        boxCanvasPreview.SetSizer(canvasSizer)

        previewSizer = wx.BoxSizer(wx.VERTICAL)
        previewSizer.Add(boxCanvasPreview, 0, wx.ALL | wx.EXPAND, border=5)
        previewSizer.Add(boxDesignSummary, 1, wx.ALL|wx.EXPAND, border=5)
        previewSizer.Add(btnSizer, 0, wx.ALL | wx.EXPAND) #, border=10)      

        #main sizer
        pageSizer = wx.BoxSizer(wx.HORIZONTAL)
        pageSizer.Add(boxDesignOptions, 1, wx.ALL | wx.EXPAND, border=5)
        pageSizer.Add(previewSizer, 1, wx.ALL | wx.EXPAND, border=5)
        self.SetSizer(pageSizer)


    def draw3DDesignOnCanvas(self, aType, panelFeats, designParams):
        self.axes.clear()
        cDraw = CalculateAndDraw()

        cDraw.calculateGeneratedCoordinates(self.axes, aType, panelFeats, designParams)

        self.canvas.draw()

    def updateSummaryText(self, t):
        self.designSummaryTxt.updateText(str(t))


class DesignNotebook(wx.Notebook):
    def __init__(self, parent, mainGUI):
        wx.Notebook.__init__(self, parent=parent, size=(PANEL_WIDTH, -1))
        self.parent = parent #parent used for sizer layouts in level above
        self.mainGUI = mainGUI
        self.SetBackgroundColour(MAIN_BACKGROUND_COLOR)

        self.page_generator = GeneratorNotebookPage(self)

        self.AddPage(self.page_generator, "Antenna Generator")

    def updateSummaryText(self, t):
        self.mainGUI.updateSummaryText(t)
          
    def updatePreview(self, aType, panelFeats, designParams):
        self.mainGUI.draw3DDesignOnCanvas(aType, panelFeats, designParams)


class MessageDisplay(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.parent = parent
        self.SetBackgroundColour(MAIN_BACKGROUND_COLOR)

        self.summaryTxt = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_RICH|wx.BORDER_SUNKEN)
        self.pageSizer = wx.BoxSizer(wx.VERTICAL)
        self.pageSizer.Add(self.summaryTxt, 1, wx.ALL|wx.EXPAND, border=5)
        self.SetSizer(self.pageSizer)

    def clearText(self):
        self.summaryTxt.SetValue("")
        
    def updateText(self, t):
        if t is None:
            return
        # sets the string as it gets it
        curTime = time.strftime("%H:%M:%S", time.localtime())
        msg = "[" + str(curTime) +"] " + str(t)  + "\n"
        self.summaryTxt.AppendText(msg)

class GeneratorNotebookPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.parent = parent
        self.SetBackgroundColour(MAIN_BACKGROUND_COLOR)

        #class vars
        self.antennaGen = None
        self.calcedParams = None
        self.panelFeats = None
        self.designParams = None

        #antenna selection dropdown
        boxSelect = wx.StaticBox(self, label='Select an Antenna Type')
        atnTypes = ['Rectangular Patch', 'Half Wave Dipole', 'Quarter Wave Monopole'] # getting dictionary keys throws an err - TODO: fix that to make this easier
        self.antennaDropDown = wx.ComboBox(boxSelect, choices=atnTypes, style=wx.CB_READONLY)
        self.antennaDropDown.SetValue(atnTypes[0])
        self.Bind(wx.EVT_COMBOBOX, self.antennaDesignSelectionChange) 
        #user input box (static) + calculate button
        self.boxInput = wx.StaticBox(self, label='Input Parameters')
        self.calculateRectangularPatchPanel = RectangularPatchOptionsPage(self.boxInput) #default
        self.calculateQuarterWaveMonopolePanel = QuarterWaveMonopoleOptionsPage(self.boxInput) 
        self.calculateHalfWaveDipolePanel = HalfWaveDipoleOptionsPage(self.boxInput) 


        self.calculateRectangularPatchPanel.Show()
        self.calculateQuarterWaveMonopolePanel.Hide()
        self.calculateHalfWaveDipolePanel.Hide()

        self.btnCalc = wx.Button(self, label="Calculate" )
        self.btnCalc.Bind(wx.EVT_BUTTON, self.btnCalculateClicked)

        #Summary of numbers
        self.boxDesign = wx.StaticBox(self, label='Calculated Parameter Values:')
        self.stDesign = wx.StaticText( self.boxDesign, style=wx.ALIGN_LEFT, size=(250, 120))
        self.updateDesignSummaryBox()

        #export generated options
        self.boxExport = wx.StaticBox(self, label='2D Antenna Exports:')
        self.ckbxDXF = wx.CheckBox(self.boxExport, label="Top Layer .DXF")
        self.ckbxPNG = wx.CheckBox(self.boxExport, label="Top Layer .PNG")
        self.ckbxGerber = wx.CheckBox(self.boxExport, label="Gerber Files")
        self.btnExport = wx.Button(self.boxExport, label="Export") #, size=(90, -1))
        self.btnExport.Bind(wx.EVT_BUTTON, self.btnExportClicked)            

        # sizers
        IOSizer = wx.BoxSizer(wx.VERTICAL)
        IOSizer.Add(boxSelect, 0, wx.ALL|wx.EXPAND, border=5)
        IOSizer.Add(self.boxInput, 0, wx.ALL|wx.EXPAND, border=5)

        # boxSelect sizer
        boxSelectSizer = wx.BoxSizer(wx.VERTICAL)
        boxSelectSizer.Add(self.antennaDropDown, 0, wx.ALL|wx.EXPAND, border=15)
        boxSelect.SetSizer(boxSelectSizer)

        # boxInput sizer
        boxInputSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxInputSizer.Add(self.calculateRectangularPatchPanel, 1, wx.ALL|wx.EXPAND,border=15)
        boxInputSizer.Add(self.calculateQuarterWaveMonopolePanel, 1, wx.ALL|wx.EXPAND,border=15)
        boxInputSizer.Add(self.calculateHalfWaveDipolePanel, 1, wx.ALL|wx.EXPAND,border=15)

        self.boxInput.SetSizer(boxInputSizer)

        # boxDesign sizer
        boxDesignSizer = wx.BoxSizer(wx.VERTICAL)
        self.stDesign.SetLabel("")
        boxDesignSizer.Add(self.stDesign, 0, wx.ALL|wx.EXPAND, border=15)
        self.boxDesign.SetSizer(boxDesignSizer)

        # export sizer
        boxExportSizer = wx.BoxSizer(wx.VERTICAL)
        boxExportSizer.AddSpacer(10)
        checkboxSizer = wx.BoxSizer(wx.HORIZONTAL)
        checkboxSizer.Add(self.ckbxDXF, 0, wx.ALL|wx.EXPAND, border=10)
        checkboxSizer.Add(self.ckbxPNG, 0, wx.ALL|wx.EXPAND, border=10)
        checkboxSizer.Add(self.ckbxGerber, 0, wx.ALL|wx.EXPAND, border=10)
        boxExportSizer.Add(checkboxSizer, 0, wx.ALL|wx.EXPAND, border=0)
        boxExportSizer.Add(self.btnExport, 0, wx.ALL|wx.ALIGN_RIGHT, border=8)
        self.boxExport.SetSizer(boxExportSizer)

        # main sizer
        pageSizer = wx.BoxSizer(wx.VERTICAL)
        pageSizer.Add(IOSizer, 0, wx.ALL|wx.EXPAND, border=5)
        pageSizer.Add(self.boxDesign, 0, wx.ALL|wx.EXPAND, border=5)
        pageSizer.Add(self.boxExport, 0, wx.ALL|wx.EXPAND, border=5)
        # pageSizer.AddSpacer(10)
        pageSizer.Add(self.btnCalc, 0, wx.ALL|wx.ALIGN_RIGHT, border=3)
        self.SetSizer(pageSizer)

    
    def updateSummaryText(self, t):
        if t is not None:
            self.parent.updateSummaryText(t)

    def antennaDesignSelectionChange(self, evt):
        boxText = evt.GetEventObject().GetValue()
        if boxText == 'Rectangular Patch':
            self.hideEverythingAndShowSinglePanel(self.calculateRectangularPatchPanel)
            self.boxDesign.Show()
            self.boxExport.Show()
            self.btnCalc.SetLabel("Calculate")
        elif boxText == "Half Wave Dipole":
            self.hideEverythingAndShowSinglePanel(self.calculateHalfWaveDipolePanel)
            self.boxDesign.Show()
            self.boxExport.Hide()
            self.btnCalc.SetLabel("Calculate")
        elif boxText == "Quarter Wave Monopole":
            self.hideEverythingAndShowSinglePanel(self.calculateQuarterWaveMonopolePanel)
            self.boxDesign.Show()
            self.boxExport.Hide()
            self.btnCalc.SetLabel("Calculate")
       
        self.Layout() 

    def hideEverythingAndShowSinglePanel(self, showPanel):
            # hide everything
            self.calculateRectangularPatchPanel.Hide()
            self.calculateQuarterWaveMonopolePanel.Hide()
            self.calculateHalfWaveDipolePanel.Hide()

            # show the selected panel
            showPanel.Show()


    def getGeneratorOptionsPanelFeatures(self,  aType):
        #calculated
        if aType == 'rectangular_patch':
            fts = self.calculateRectangularPatchPanel.getFeatures()

        elif aType == "half_wave_dipole":
            fts = self.calculateHalfWaveDipolePanel.getFeatures()

        elif aType == "quarter_wave_monopole":
            fts = self.calculateQuarterWaveMonopolePanel.getFeatures()

       
        return fts

      
    def btnCalculateClicked(self, evt):
        self.updateSummaryText("calculating antenna design from library")

        # calculator
        aType = str(ANTENNA_TYPE_DICT[self.antennaDropDown.GetValue()])
        panelFeats = self.getGeneratorOptionsPanelFeatures(aType)
        self.antennaGen = CalculatorInterface(aType, panelFeats)
        errMsg, paramArr = self.antennaGen.calculateAntennaParams()
        self.updateSummaryText(errMsg)
        self.updateSummaryText("calculation done")

        # set vals
        self.aType = aType
        self.panelFeats = panelFeats
        self.designParams = paramArr

        # update summary
        self.updateDesignSummaryBox()

        # update UI
        self.parent.updatePreview(self.aType, self.panelFeats, self.designParams)
        self.updateSummaryText("preview updated")

        
    def btnExportClicked(self, evt=None):
        # check if any exports are selected
        b1, b2, b3 = self.getExportSelections()
        if (b1 or b2 or b3) ==False:
            msg = "No exports selected"
            self.updateSummaryText(msg)
            return

        if (self.panelFeats == None) or (self.designParams==None):
            msg = "No topologies calculated"
            self.updateSummaryText(msg)
            return       

        self.updateSummaryText("processing exports")
        self.updateSummaryText("select save location...")

        # prompt for save loc
        pathname = os.getcwd()
        print(pathname)
        with wx.DirDialog(self, "Select save location",  "",
                    wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return     # user cancelled
            # save the current contents in the file
            pathname = dirDialog.GetPath()
            try:
                self.exportSelections(pathname) 
                msg = "designs exported to " + str(pathname)
                self.updateSummaryText(msg)
            except Exception as e:
                msg = "Cannot save current data in file " + str(pathname)
                self.updateSummaryText(msg)


    def updateDesignSummaryBox(self):
        
        if self.designParams == None:
            return

        tmp =  self.designParams
        txt = "\n"
        for t in tmp:
            tName = t[0] #name of column
            tVal = float(t[1])
             #catch the 'null' issue for rounding
            try: v = str("{:.6}".format(round(tVal, 6))) +" mm"
            except: v = "NA"
            txt = txt + str(tName) + ":\t" + str(v) + "\n"
        self.stDesign.SetLabel(txt)

  
    def getExportSelections(self):
        exportDXFBool = self.ckbxDXF.GetValue()
        exportPNGBool = self.ckbxPNG.GetValue()
        exportGerberBool = self.ckbxGerber.GetValue()
        return exportDXFBool, exportPNGBool, exportGerberBool
    
            
    def exportSelections(self, filePath):
        dxfBool, pngBool, gerberBool = self.getExportSelections()
        if (dxfBool or pngBool or gerberBool) == True:
            try:
                errMsg = self.antennaGen.exportSelections(filePath, dxfBool, pngBool, gerberBool)
                self.updateSummaryText(errMsg)
            except Exception as e:
                self.updateSummaryText("exception in panel_generator.py and calculator.py. calculator interface needs to be updated")
                self.updateSummaryText(e)
            
    

class RectangularPatchOptionsPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.parent = parent
        self.SetBackgroundColour(MAIN_BACKGROUND_COLOR)

        lblTarget = wx.StaticText(self, label="Target Frequency (Hz):")
        self.fieldFrequency = wx.TextCtrl(self, value="", size=(INPUT_BOX_WIDTH, 20))
        self.fieldFrequency.SetValue("2.4e9")
        lblDielectric = wx.StaticText(self, label="Dielectric Constant:")
        self.fieldDielectric = wx.TextCtrl(self, value="", size=(INPUT_BOX_WIDTH, 20))
        self.fieldDielectric.SetValue("4.4")
        lblSubstrateHeight = wx.StaticText(self, label="Substrate Height (mm):")
        self.fieldSubstrateHeight = wx.TextCtrl(self, value="", size=(INPUT_BOX_WIDTH, 20))
        self.fieldSubstrateHeight.SetValue("1.6")
        lblFeed = wx.StaticText(self, label="Feed Method:")
        feedTypes = ['microstrip', 'probe']
        self.feedDropDown = wx.ComboBox(self, choices=feedTypes, style=wx.CB_READONLY) #, size=(INPUT_BOX_WIDTH, 20)
        self.feedDropDown.SetValue(feedTypes[0])
        lblGap = wx.StaticText(self, label="Gap (mm):")
        self.fieldGap = wx.TextCtrl(self, value="", size=(INPUT_BOX_WIDTH, 20))
        self.fieldGap.SetValue("1")
        lblStripWidth = wx.StaticText(self, label="Strip Width (optional, mm):")
        self.fieldStripWidth = wx.TextCtrl(self, value="", size=(INPUT_BOX_WIDTH, 20))
        self.fieldStripWidth.SetValue("3.06")
        

        boxInputSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxInputLeft = wx.BoxSizer(wx.VERTICAL)
        boxInputRight = wx.BoxSizer(wx.VERTICAL)
        boxInputLeft.Add(lblTarget, 0, wx.ALL|wx.EXPAND, border=5)
        boxInputLeft.Add(lblDielectric, 0, wx.ALL|wx.EXPAND, border=5)
        boxInputLeft.Add(lblSubstrateHeight, 0, wx.ALL|wx.EXPAND, border=5)
        boxInputLeft.Add(lblFeed, 0, wx.ALL|wx.EXPAND, border=7)
        boxInputLeft.Add(lblGap, 0, wx.ALL|wx.EXPAND, border=7)
        boxInputLeft.Add(lblStripWidth, 0, wx.ALL|wx.EXPAND, border=7)

        boxInputRight.Add(self.fieldFrequency, 0, wx.ALL|wx.EXPAND, border=3)
        boxInputRight.Add(self.fieldDielectric, 0, wx.ALL|wx.EXPAND, border=3)
        boxInputRight.Add(self.fieldSubstrateHeight, 0, wx.ALL|wx.EXPAND, border=3)
        boxInputRight.Add(self.feedDropDown, 0, wx.ALL|wx.EXPAND, border=3)
        boxInputRight.Add(self.fieldGap, 0, wx.ALL|wx.EXPAND, border=3)
        boxInputRight.Add(self.fieldStripWidth, 0, wx.ALL|wx.EXPAND, border=3)

        boxInputSizer.Add(boxInputLeft, 0, wx.ALL|wx.EXPAND,border=15)
        boxInputSizer.Add(boxInputRight, 0, wx.ALL|wx.EXPAND,border=15)


        self.SetSizer(boxInputSizer)
        

    def getFeatures(self):
        features = [["feed_type", self.feedDropDown.GetValue()],
                    ["dielectric", self.fieldDielectric.GetValue()],
                    ["substrate_height", self.fieldSubstrateHeight.GetValue()],
                    ["simulation_frequency", self.fieldFrequency.GetValue()],
                    ["gap", self.fieldGap.GetValue()],
                    ["strip_width", self.fieldStripWidth.GetValue()]]

        return features


        
class QuarterWaveMonopoleOptionsPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.parent = parent
        self.SetBackgroundColour(MAIN_BACKGROUND_COLOR)

        lblTarget = wx.StaticText(self, label="Target Frequency (Hz):")
        self.fieldFrequency = wx.TextCtrl(self, value="", size=(INPUT_BOX_WIDTH, 20))
        self.fieldFrequency.SetValue("2.4e9")
        lblWireRadius = wx.StaticText(self, label="Wire Radius (mm):")
        self.fieldWireRadius = wx.TextCtrl(self, value="", size=(INPUT_BOX_WIDTH, 20))
        self.fieldWireRadius.SetValue("1")

        boxInputSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxInputLeft = wx.BoxSizer(wx.VERTICAL)
        boxInputRight = wx.BoxSizer(wx.VERTICAL)
        boxInputLeft.Add(lblTarget, 0, wx.ALL|wx.EXPAND, border=5)
        boxInputLeft.Add(lblWireRadius, 0, wx.ALL|wx.EXPAND, border=5)
        boxInputRight.Add(self.fieldFrequency, 0, wx.ALL|wx.EXPAND, border=3)
        boxInputRight.Add(self.fieldWireRadius, 0, wx.ALL|wx.EXPAND, border=3)
        boxInputSizer.Add(boxInputLeft, 0, wx.ALL|wx.EXPAND,border=15)
        boxInputSizer.Add(boxInputRight, 0, wx.ALL|wx.EXPAND,border=15)
        self.SetSizer(boxInputSizer)

    def getFeatures(self):
        features = [["conductor_radius", self.fieldWireRadius.GetValue()],
                    ["simulation_frequency", self.fieldFrequency.GetValue()]]
        return features
    


class HalfWaveDipoleOptionsPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.parent = parent
        self.SetBackgroundColour(MAIN_BACKGROUND_COLOR)

        lblTarget = wx.StaticText(self, label="Target Frequency (Hz):")
        self.fieldFrequency = wx.TextCtrl(self, value="", size=(INPUT_BOX_WIDTH, 20))
        self.fieldFrequency.SetValue("2.4e9")
        lblWireRadius = wx.StaticText(self, label="Wire Radius (mm):")
        self.fieldWireRadius = wx.TextCtrl(self, value="", size=(INPUT_BOX_WIDTH, 20))
        self.fieldWireRadius.SetValue("1")
        lblFeedGap = wx.StaticText(self, label="Feed Gap (mm):")
        self.fieldFeedGap = wx.TextCtrl(self, value="", size=(INPUT_BOX_WIDTH, 20))
        self.fieldFeedGap.SetValue("5")

        boxInputSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxInputLeft = wx.BoxSizer(wx.VERTICAL)
        boxInputRight = wx.BoxSizer(wx.VERTICAL)
        boxInputLeft.Add(lblTarget, 0, wx.ALL|wx.EXPAND, border=5)
        boxInputLeft.Add(lblWireRadius, 0, wx.ALL|wx.EXPAND, border=5)
        boxInputLeft.Add(lblFeedGap, 0, wx.ALL|wx.EXPAND, border=5)
        boxInputRight.Add(self.fieldFrequency, 0, wx.ALL|wx.EXPAND, border=3)
        boxInputRight.Add(self.fieldWireRadius, 0, wx.ALL|wx.EXPAND, border=3)
        boxInputRight.Add(self.fieldFeedGap, 0, wx.ALL|wx.EXPAND, border=3)
        boxInputSizer.Add(boxInputLeft, 0, wx.ALL|wx.EXPAND,border=15)
        boxInputSizer.Add(boxInputRight, 0, wx.ALL|wx.EXPAND,border=15)
        self.SetSizer(boxInputSizer)

    def getFeatures(self):
        features = [["conductor_radius", self.fieldWireRadius.GetValue()],
                    ["feed_gap", self.fieldFeedGap.GetValue()],
                    ["simulation_frequency", self.fieldFrequency.GetValue()]]
        return features               