#! /usr/bin/python3

##--------------------------------------------------------------------\
#   Antenna Calculation Autotuning Tool (with modificatios)
#   Most of the functions for the class for calculating coordinate points 
#   used in the GUI drawing, and some of the simulation polyshape creation
#   Not all points used for drawing are saved for CAD creation
#
#   Author(s): Lauren Linkous (LINKOUSLC@vcu.edu)
#   Last update: June 5, 2024 
##--------------------------------------------------------------------\

import numpy as np

ZEROS_ARR = [0, -0, 0.0, -0.0] #cover the different ways zeros can be represented (also deals w weird user input)

class CalculateAndDraw():
    def __init__(self):
        
        # main coord arrays
        # format is [[shape1], [shape2]]. i.e: [[[x,y,z], [x,y,z], [x,y,z]], [[x,y,z],[x,y,z]]]
        self.conductorCoords = []
        self.substrateCoords = []
        self.superstrateCoords = []
        #user set vals
        self.bendAngle = None #angle of deflection for antenna-substrate contact
        self.substrateParams = [] #width,length for rectangles. radx,radx for circles/ovals
        self.substrateLayers = []
        self.conductorType = None
        self.conductorFeed = None
        self.conductorLayers = []
        self.conductorParams = None 
        self.superstrateLayers = []
        self.superstrateParams = None

        #calculated vals for CAD drawing
        self.substrateSheetEqs = [] #format [[A, min_ang, max_ang, offset]]
        self.conductorSheetEqs = []


        # flat coord array backups
        self.flatConductorCoords = []
        self.flatSubstrateCoords = []
        self.flatSuperstrateCoords = []

        #arc drawing params
        self.d = None  #deflection angle provided by user
        self.mainArcRadius = None #radius of top layer substrate arc (used as the reference radius for substrate and conductor layers)
        self.substrateArcLength = None # this applies only to curved materials
        self.N = 45  # num pts to graph in arc
        self.k = 0  # (k,h,f). offset
        self.h = 0
        self.f = 0
        self.offset = 0 #(x,y,z) for future feature options
        self.arcCenter = 0
        self.mainArc_x = []
        self.mainArc_y = []
        self.x_lim = 1
        self.y_lim = 1

    #######################################################################
    # canvas basics
    #######################################################################  
    def setupCanvas(self, ax, units="mm"):
        #takes in the axes for plotting in matplotlib chart
        ax.clear()
        self.updateCanvas(ax, units=units)

    def matplotlibColorConversion(self, color):
        #convert from 0-255 scale to 0-1 scale
        #also deals with RGBA to RGB
        col = []
        if (color[0] >= 1) or (color[1] >=1) or (color[1] >=1):
            col = tuple([color[0]/255, color[1]/255, color[2]/255])
        else:
            col = tuple([color[0], color[1], color[2]])

        return col

    def updateCanvas(self, ax, view=[-75, 90, 0], units="mm", equal=True):
        ax.set_xlabel('x_size ('+ str(units) + ')')
        ax.set_ylabel('y_size ('+ str(units) + ')')
        ax.set_zlabel('z_size ('+ str(units) + ')')
        ax.view_init(elev=view[0], azim=view[1], roll=view[2])    #set to look at XY plane (-90,90, 0), with a bit of an angle
        if equal == True:
           ax.axis('equal') #for equal scale so no distortion
        
    def setEnviornmentParams(self, bendAngle=0, offset=[0,0,0], *args):
        self.bendAngle = float(bendAngle)        
        self.k = offset[0]
        self.h = offset[1]
        self.f = offset[2]
        self.offset = offset #(x,y,z) for future feature options
        self.arcCenter = 0


    #######################################################################
    # setters and getters for class vars
    #######################################################################   

    def setConductorCords(self, c):
        # used for imported DXF designs.
        # format is [[shape1], [shape2]]. i.e: [[[x,y,z], [x,y,z], [x,y,z]], [[x,y,z],[x,y,z]]]
        self.conductorCoords = c

    def getConductorCoords(self):
        return self.conductorCoords

    def setSubstrateCords(self, c):
        self.substrateCoords = c

    def getSubstrateCoords(self):
        return self.substrateCoords    
    
    def setSuperstrateCords(self, c):
        self.superstrateCoords = c

    def getSuperstrateCoords(self):
        return self.superstrateCoords    
    

    def setSuperstrateParams(self, superstrateLayers=[], *args):
        self.superstrateLayers = superstrateLayers
        self.superstrateParams = args[0]

    def setConductorParams(self, conductorType=None, conductorFeed=None, conductorLayers=[], *args):
        self.conductorType = conductorType
        self.conductorFeed = conductorFeed
        self.conductorLayers = conductorLayers
        self.conductorParams = args[0]

    def setSubstrateParams(self, substrateLayers=[], *args):
        self.substrateLayers = substrateLayers
        self.substrateParams = args[0]
    
    def setSuperstrateParams(self, superstrateLayers=[], *args):
        return self.superstrateParams

    def getConductorParams(self, conductorType=None, conductorFeed=None, conductorLayers=[], *args):
        return self.conductorParams

    def getSubstrateParams(self, substrateLayers=[], *args):
        return self.substrateParams

    
    #######################################################################
    # main function for generating cordinates
    #
    #   calculateGeneratedDesignCoordinates()
    #       called by the design_page when the calculator/replicator options are used
    #   parseImportedConductorDesignCoordinates()
    #       used when importing the dxf design. parses conductor/substrate/values out
    #   calculateLayerDesignCoordinates()
    #       called when the layers are set. might include generated/imported 
    #   calculateBendCoordinates()
    #       takes existing coordinates and bends them to fit a 2D line
    #   
    #       ... advanced features such as substrate shape to be added
    #######################################################################

    def calculateGeneratedCoordinates(self, ax, aType, features, params):
        # Called by the calculate/replicate button in 'page_design'

        xlims = [0, 10]
        ylims = [0, 10]
        zlims = [-10, 10]

        if (aType == "rectangular_patch"):
            l,w = self.generatePatch(ax, features, params)
            # adjust limits for 3D canvas
            xlims = [0, 2.5*l]
            ylims = [0, 2.5*l]
            zlims = [-1.25*l, 1.25*l]          

        elif (aType =="half_wave_dipole"):
            l,a  = self.generateDipole(ax, features, params)
            # adjust limits for 3D canvas
            xlims = [-l/2, l/2]
            ylims = [-l/2, l/2]
            zlims = [-0.75*l, 0.75*l]         

        elif aType =="quarter_wave_monopole":
            l  = self.generateMonopole(ax, features, params)
            # adjust limits for 3D canvas
            xlims = [-l/2, l/2]
            ylims = [-l/2, l/2]
            zlims = [0, 1.25*l]     
       
        else:
            print("unrecognized antenna type in graphics helper funcs: " + str(aType))


        #adjust limits for 3D canvas
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
        ax.set_zlim(zlims)
        
        ax.set_xlabel('x_size (mm)')
        ax.set_ylabel('y_size (mm)')
        ax.set_zlabel('z_size (mm)')


    #######################################################################
    # primary functions for drawing generated designs
    #   these generate the coordinates for the FLAT version of the generated
    #   designs from the design page
    #######################################################################

    def generatePatch(self, ax, features, params):
        feed = features[0][1]
        h = float(features[2][1]) 
        w = float(params[0][1])
        l = float(params[1][1])    
        x0 = float(params[2][1])
        y0 = float(params[3][1])

        #draw ground plane rectangle
        pts = self.drawRectangularPlane(ax, 2*l, 2*w, z=0, color="goldenrod") # groundplane
        self.substrateCoords.append(pts)

        #draw top of patch
        if feed == "microstrip":
            sw = float(params[4][1])
            g = float(params[5][1])
            self.draw2DMicrostripConductor(ax, l, w, h, x0, sw, g, color="orange")
        elif feed =="probe":
            pts = self.drawRectangularPlane(ax, 2*l, 2*w, z=h, corner=[0,0], color="orange")
            self.substrateCoords.append(pts)
            pts = self.drawRectangularPlane(ax, l, w, z=h, corner=[w/2,l/2], color="orange")
            self.conductorCoords.append(pts)
            pts = self.drawCircularPoint(ax, w/2+y0, 1.5*l-x0, h, color="orange")
            self.conductorCoords.append(pts)
        else:
            print("unrecognized feed type for rectangular_patch")
        return l, w


    def generateMonopole(self, ax, features, params, color = "b"):
        l = float(params[0][1])    
        rad = float(params[1][1])    

        self.drawCylinder(ax, rad, start=0, stop=l, center=[0,0], color=color)

        return l #return val to size the canvas

    def generateDipole(self, ax, features, params, color = "m"):
        l = float(params[0][1]) 
        hl = float(params[1][1])    
        rad = float(params[2][1])    
        fg = float(params[3][1])    

        #draw cylinder x2
        self.drawCylinder(ax, rad, start=(fg/2), stop=(hl+fg/2), center=[0,0], color=color)
        self.drawCylinder(ax, rad, start=(-hl-fg/2), stop=-fg/2, center=[0,0], color=color)

        return l, rad #return val to size the canvas


    #######################################################################
    # Functions for drawing rectangular patch antenna conductors
    #######################################################################

    def draw2DMicrostripConductor(self, ax,  l, w, h, x0, ws, g, corner=[0,0], color="g"):
        #substrate edges
        substratePts = self.rectangle(corner, 2*w, 2*l, h)
        x,y,z = self.XYZptsSplit(substratePts)
        ax.plot(x,y,z, color=color)
        #conductor
        conductorPts = self.rectangularPatchConductor(l, w, h, x0, ws, g)
        x,y,z = self.XYZptsSplit(conductorPts)
        ax.plot(x, y, z, color=color)

        #append points to memory
        self.substrateCoords.append(substratePts)
        self.conductorCoords.append(conductorPts)


   
    def rectangularPatchConductor(self, L, W, h, x0, Ws, g):
        #2D coordinates for drawing the patch antenna conductor
        #modified from antenna calculator
        substrate_origin = 0.0
        originW = -(substrate_origin - W*0.5)
        originL = -(substrate_origin - L*0.5) #keep
        W_cut = (W - Ws - g * 2) / 2
        points = [[originW, originL, h], [originW + W, originL, h], [originW + W, originL + L, h],
                [(originW + W_cut + Ws + g * 2), originL + L, h],
                [originW + W_cut + Ws + g * 2, originL + L - x0, h],
                [originW + W_cut + Ws + g, originL + L - x0, h],
                [originW + W_cut + Ws + g, originL + L * 1.5, h],
                [originW + W_cut + g, originL + L * 1.5, h],
                [originW + W_cut + g, originL + L - x0, h],
                [originW + W_cut, originL + L - x0, h],
                [originW + W_cut, originL + L, h],
                [originW, originL + L, h],
                [originW, originL, h]]
        return points

    
    #######################################################################
    # Functions for drawing planes
    #######################################################################
    def drawRectangularPlane(self, ax, length, width, z, corner=[0,0], color ="b"):
        pts = self.rectangle(corner, width, length, z)
        x,y,z = self.XYZptsSplit(pts)
        ax.plot(x,y,z, color=color)
        return pts


    #######################################################################
    # Functions for drawing 3D shapes
    #######################################################################

    def drawCylinder(self, ax, a, start, stop, center=[0,0], color="b"):
        x = center[0]
        y = center[1]
        z = np.linspace(start, stop, 50)
        theta = np.linspace(0, 2*np.pi, 50)
        thetaMat, zMat=np.meshgrid(theta, z)
        xMat = x + a*np.cos(thetaMat)
        yMat = y + a*np.sin(thetaMat)
        ax.plot_surface(xMat, yMat, zMat, alpha=0.75, color=color)

        # zip cords
        pts = zip(xMat, yMat, zMat)
        return pts

    def drawFlatRectangle3DLayer(self, ax, width, length, depth, centerFrontPt, color="b"):        
        w = width
        l = length
        c_x = centerFrontPt[0]
        c_y = centerFrontPt[1] #depth_ctr
        c_z = centerFrontPt[2]
                
        #corner points, clockwise from front left + one to close shape
        #top
        u1 = [c_x-w/2, c_y, c_z+0] #front left
        u2 = [c_x-w/2, c_y, c_z+l]
        u3 = [c_x+w/2, c_y, c_z+l]
        u4 = [c_x+w/2, c_y, c_z+0] #front right
        upper_face_pts = np.array([u1, u2, u3, u4, u1])
        ax.plot(upper_face_pts[:,0], upper_face_pts[:,1] ,upper_face_pts[:,2], color=color)
        #bottom
        l1 = [c_x-w/2, c_y+depth, c_z+0]
        l2 = [c_x-w/2, c_y+depth, c_z+l]
        l3 = [c_x+w/2, c_y+depth, c_z+l]
        l4 = [c_x+w/2, c_y+depth, c_z+0]
        lower_face_pts = np.array([l1, l2, l3, l4, l1])
        ax.plot(lower_face_pts[:,0], lower_face_pts[:,1], lower_face_pts[:,2], color=color)

        #edges
        self.drawConnectingEdge(ax, color, [[u1, l1], [u2, l2], [u3, l3], [u4, l4]])

        return upper_face_pts  #this is the layer that will be extruded (downwards) in the CAD 


    #######################################################################
    # Basic Shape Functions with x,y,z pts
    #######################################################################
    def drawCircularPoint(self, ax, x, y, z, color ="b"):
        ax.plot(x, y, z, 'o', color=color, linewidth=0.2)

    def rectangle(self, c, w, h, z):
        x = c[0]
        y = c[1]
        return [[x, y, z], [x + w, y, z], [x + w, y + h, z], [x, y + h, z]]

    def rectangleByCenter(self,c, w, h, z):
        x = c[0]
        y = c[1]
        return [[x-0.5*w, y-0.5*h, z], [x +0.5*w, y-0.5*h, z], [x+0.5*w, y+0.5*h, z], [x-0.5*w, y+0.5*h,z]]

    def circleByCenter(self,c, w, h, z):
        x = c[0]
        y = c[1]
        return [[x, y, z], [x + w, y, z], [x + w, y + h, z], [x, y + h, z]]

    #######################################################################
    # Basic Shape Functions
    #######################################################################

    def XYZptsSplit(self,pts):
        x = []
        y = []
        z = []
        ctr = 0
        for i in pts:
            ctr = ctr + 1
            x.append(i[0])
            y.append(i[1])
            z.append(i[2])
        # close figure if needed
        if ctr > 2:
            x.append(x[0])
            y.append(y[0])
            z.append(z[0])
        return x, y, z
