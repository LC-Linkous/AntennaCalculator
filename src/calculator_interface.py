#! /usr/bin/python3

import sys
import os

from antenna_calculator import AntennaCalculator

CALCULATOR_EXPORT_LIST = ['rectangular_patch']

class CalculatorInterface():
    def __init__(self, aType, panelFeats):
        self.aType = aType
        self.calcPanelFeatures = panelFeats
        self.calcedParams = None
        
    def calculateAntennaParams(self):
        errMsg = None
 
        #call to func that formats the calculator project call
        inputParams = self.setCalculatorArgParams()
        # call to AntennaCalc project
        try:
            calcedParams = self.callCalculator(inputParams)
        except Exception as e:
            errMsg = "Invalid configuration detected in calculator"
            return errMsg

        #convert from meters to millimeters
        self.calcedParams = self.convertFromMetersToMillimeters(calcedParams)

        #update Antenna Config with calculated vars
        if self.aType == 'rectangular_patch': 
            fType = self.calcPanelFeatures[0][1]
            x0 = self.calcedParams[2]
            if fType == 'microstrip':
                paramArr = [["width", self.calcedParams[0]],
                            ["length", self.calcedParams[1]],
                            ["x0", x0],
                            ["y0", self.calcedParams[3]],
                            ["strip_width", self.calcedParams[4]],
                            ["gap", float(self.calcPanelFeatures[5][1])]]
            elif fType == 'probe':
                paramArr = [["width", self.calcedParams[0]],
                    ["length", self.calcedParams[1]],
                    ["x0", x0],
                    ["y0", self.calcedParams[3]]]
            else:
                errMsg = errMsg + "ERROR: unrecognized feed type. check dictionary imports"
                return errMsg
 
        
        elif self.aType == 'half_wave_dipole':
            paramArr = [["length", self.calcedParams[0]],
                        ["half_length",float(self.calcedParams[0])/2],
                        ["radius", float(self.calcPanelFeatures[0][1])],
                        ["feed_gap", float(self.calcPanelFeatures[1][1])]]

        elif self.aType == 'quarter_wave_monopole':
            paramArr = [["length", self.calcedParams[0]],
                        ["radius", float(self.calcPanelFeatures[0][1])]]

        return errMsg, paramArr
    
    
    def callCalculator(self, args):
        shell = AntennaCalculator(args)
        args = shell.getArgs()
        shell.main(args)
        calcedParams = shell.getCalcedParams()
        return calcedParams


    def convertFromMetersToMillimeters(self, params):
        convertedParams = []
        if type(params) == tuple: #rectangular patch
            for p in params:
                pmm = float(p)*1000
                convertedParams.append(pmm)
        elif type(params)== float:  #monopole, dipole
            pmm = float(params)*1000
            convertedParams.append(pmm)
        return convertedParams
    
    
    def setCalculatorArgParams(self):
        ap = []
        if self.aType == 'rectangular_patch':
            f =  self.calcPanelFeatures[3][1] #features["simulation_frequency"][0]
            er = self.calcPanelFeatures[1][1] # features["dielectric"][0]
            h =  str(float(self.calcPanelFeatures[2][1])/1000) #convert to meters for calculator
            ty =  self.calcPanelFeatures[0][1]
            ap = ['rectangular_patch',
                  '-f', str(f),
                  '-er',str(er),
                  '-h', str(h),
                  '--type', str(ty),
                  '--variable_return']
        elif self.aType == 'half_wave_dipole':
            f =  self.calcPanelFeatures[2][1]
            ap = ['half_wave_dipole',
                  '-f', str(f),
                  '--variable_return']
        elif self.aType == 'quarter_wave_monopole':
            f =  self.calcPanelFeatures[1][1]
            ap = ['quarter_wave_monopole',
                  '-f', str(f),
                  '--variable_return']
        return ap

    def exportSelections(self, filePath, dxfBool, pngBool, gerberBool):
        errMsg = None
        aType = self.aType
        if aType not in CALCULATOR_EXPORT_LIST:
            errMsg = "unable to export topology. this feature has not been added yet"
        if aType == 'rectangular_patch':
            fType =  self.calcPanelFeatures[0][1]
            if fType == 'microstrip':
                self.exportMicrostripRectangularPatch(filePath, dxfBool, pngBool, gerberBool)
            else:
                self.exportProbeRectangularPatch(filePath, dxfBool, pngBool, gerberBool)
        return errMsg

    def exportMicrostripRectangularPatch(self, filePath, dxfBool, pngBool, gerberBool):
        atype = self.aType
        fType =  self.calcPanelFeatures[0][1]
        sw = self.calcedParams[4]
        w = self.calcedParams[0]
        l = self.calcedParams[1]
        x0 = self.calcedParams[2]
        y0 = self.calcedParams[3]  

        basePath = os.path.join(filePath, str(atype))
        if dxfBool == True:
            ap = []
            pth = str(basePath + ".dxf")
            # convert to meter bc that's what the subparser expects
            ap = ['rectangular_patch_export',
                    '--type', str(fType),
                    '-W', str(w/1000),
                    '-L', str(l/1000),
                    '-x0', str(x0/1000),
                    '-y0', str(y0/1000),
                    '-ws', str(sw/1000),
                    '--dxfoutput', pth]
            self.callCalculator(ap)
        if pngBool == True:
            ap = []
            pth = str(basePath + ".png")
            # convert to meter bc that's what the subparser expects
            ap = ['rectangular_patch_export',
                '--type', str(fType),
                '-W', str(w/1000),
                '-L', str(l/1000),
                '-x0', str(x0/1000),
                '-y0', str(y0/1000),
                '-ws', str(sw/1000),
                '--pngoutput', pth]
            self.callCalculator(ap)
        if gerberBool == True:
            ap = []
            pth = str(basePath) #no extension
            # convert mm to meter bc that's what the subparser expects
            ap = ['rectangular_patch_export',
                '--type', str(fType),
                '-W', str(w/1000),
                '-L', str(l/1000),
                '-x0', str(x0/1000),
                '-y0', str(y0/1000),
                '-ws', str(sw/1000),
                '--gerberoutput', pth]
            self.callCalculator(ap)

    def exportProbeRectangularPatch(self, filePath, dxfBool, pngBool, gerberBool):
        atype = self.aType
        fType =  self.calcPanelFeatures[0][1]
        w = self.calcedParams[0]
        l = self.calcedParams[1]
        x0 = self.calcedParams[2]
        y0 = self.calcedParams[3]  

        basePath =  os.path.join(filePath, str(atype))
        if dxfBool == True:
            ap = []
            pth = str(basePath + ".dxf")
            ap = ['rectangular_patch_export',
                '--type', str(fType),
                '-W', str(w),
                '-L', str(l),
                '-x0', str(x0),
                '-y0', str(y0),
                '--dxfoutput', pth]
            self.callCalculator(ap)
        if pngBool == True:
            ap = []
            pth = str(basePath + ".png")
            ap = ['rectangular_patch_export',
                '--type', str(fType),
                '-W', str(w),
                '-L', str(l),
                '-x0', str(x0),
                '-y0', str(y0),
                '--pngoutput', pth]
            self.callCalculator(ap)
        if gerberBool == True:
            ap = []
            pth = str(basePath) #no extension
            ap = ['rectangular_patch_export',
                '--type', str(fType),
                '-W', str(w),
                '-L', str(l),
                '-x0', str(x0),
                '-y0', str(y0),
                '--gerberoutput', pth]
            self.callCalculator(ap)

    