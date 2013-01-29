#!/usr/bin/env python

# TODO --> GENERIC TODOs
# TODO --> vector clase to operate (mainly sum) origins, sizes, corners....

import sys
import pygame
import numpy as N

from dofmodel import DOFModel
from common import ObserverInterface, SubjectInterface

# --------------------------------------------------------------------- 
# VIEW & DATA MODEL
# ---------------------------------------------------------------------
class ViewModel( SubjectInterface ):
    """ViewModel.
        Implements SubjectInterface"""
    # Default values for ViewModel. Class attributes.

    def __init__( self, mode=False ):
        #TODO --> mode=False for Landscape mode , True for Object mode --> TODO use enumeration type?

        # SUBJECT (observer pattern)
        self.observers = []  # List of observer objects

        # View State
        self.mode = mode

    # -------------------------------------------------------    
    # SUBJECT (observer pattern) methods
    def registerObserver( self, observer ):
        """Overrides the abstract registerObserver()"""
        print "Appending new observer",observer,"to",self.observers
        self.observers.append( observer )
        print "New list of observers:",self.observers
        
    def removeObserver( self ,observer ):
        """Overrides the abstract removeObserver()"""
        print "Removing observer",observer,"from",self.observers
        self.observers.remove( observer )
        print "New list of observers:",self.observers

    def notifyObservers( self ):
        """Overrides the abstract notifyObservers()"""
        for observer in self.observers:
            print( "Notifying"+str( observer )+"!" )  
            observer.update( self )  # Update the observer!
    # -------------------------------------------------------    

    def set_mode( self, mode ):
        self.mode = mode
        self.calculateModel( )
        self._printState( )
    def calculateModel( self ):
        self.notifyObservers( )
        
    def _printState(self):
        # DEBUG function for showing state of the MODEL
        print "==============================="
        print " VIEW MODEL"
        print "==============================="
        print " mode = ",self.mode
        print "==============================="

# ---------------------------------------------------------------------
# DOF WIDGETS
# ---------------------------------------------------------------------
     
class CompositeInterface( ):
    # Managing composite tree
    def addChild( self, child ):
        print >> sys.stderr,str(self)+" Method addChild() of CompositeInterface is abstract"
    def removeChild( self ):
        print >> sys.stderr,str(self)+" Method removeChild() of CompositeInterface is abstract"
    def getChilds( self ):
        print >> sys.stderr,str(self)+" Method getChilds() of CompositeInterface is abstract"
    # Specific functions of the composite


class DOFwidget( CompositeInterface, ObserverInterface ):
    """ Base class for our DOF widgets """
    """ Implements:
                    CompositeInterface
                    ObserverInterface
    """

    def __init__( self,
                    canvas, 
                    drawers = [],
                    handler = None,
                    origin = [ 0, 0],
                    f_origin = None,
                    vector_x = ( 1, 0),
                    vector_y = ( 0, 1),
                    corner = (0, 0),
                    f_corner = None,
                    size = ( 0, 0),
                    f_size = None,
                    visible = False,
                    name = "",
                    parent = None
                ):

        
        # NAME attribute
        self.name = name
        # GRAPHICAL attributes
        self.canvas = canvas       # Canvas where the widget will be drawn is Mandatory
        self.origin = origin       # Coordinates origin referred to parent's system of coordinates
        self.f_origin = f_origin    # Function for calculating origin from parent
        self.vector_x = vector_x   # Coordinate vector x referred to parent's system of coordinates 
        self.vector_y = vector_y   # Coordinate vector y referred to parent's system of coordinates 
        self.corner = corner       # Lower-left corner of the widget. 
        self.f_corner = f_corner   # Function for calculating corner from parent 
        self.size = size           # Width & height of the widget. (0,0) by default --> size will be inherited from parent when composing the widget tree
        self.f_size = f_size        # Function for calculating size from parent

        self.visible = visible       # By default, the widget is not visible
        #self.surface = pygame.Surface( self.size ) #__>TODO --> is this useful/needed?
        #self.rect = self.surface.get_rect( )   # __>TODO get a Rect with includes the widget


        # COMPOSITE attributes
        self.parent = parent       # Parent composite element
        if parent:  
            self.parent.addChild( self )  # Attach self as child of parent
        self.children = []         # Children composite elements

        # DRAWERS & HANDLER
        self.drawers = drawers      # Not mandatory, can be [] if not wanted to draw anything
        self.handler = handler
        if self.handler:
            self.handler.widget = self  # Backreference handler --> widget

        # RECTANGLE defined by the widget, absolute coords
        self.rectangle = pygame.Rect( 0,0,0,0 ) # 
        self._refresh_rectangle( )

    # COMPOSITE pattern
    # TODO
    def addChild( self, child ):
        # Append child to list of children
        self.children.append( child )
        # Set backreference from the child to self (parent)
        child.parent = self

    # OBSERVER pattern
    # TODO
    def update( self, caller):
        self.hide( )
        self.display( )
        #TODO--> hide() parece redundante al hacer display()
        #TODO--> Sera que Tkinter borra automaticamente al REdibujar si el item esta etiquetado (tags)
        #TODO-->    o sera que directamente se sobredibuja encima??

    # GRAPHICAL methods
    def setVisible( self, visible=True ):
        """ visible is a boolean, True by default"""
        self.visible = visible

    def display( self ):
        if self.visible == True:
            if not self.parent:     # If widget is root, clean canvas visibility stack
                self.canvas.clean_stack( ) 
            if self.handler:            # Only if there is a handler...
                self.canvas.pop( self ) # Add widget to canvas visibility stack 

            # Recalculate origin, corner, size if there is a function for it
            #    which recalculates those ones in function of parent widget
            if self.f_origin:
                self.origin = self.f_origin(self)
            if self.f_corner:
                self.corner = self.f_corner(self)
            # If child's size is (0,0), it will inherit the parent's size
            # Do this before trying f_size
            if self.size == (0,0):
                self.size = self.parent.size
            if self.f_size:
                self.size = self.f_size(self)
            # Do not forget: _refresh_rectangle
            self._refresh_rectangle()
            
            # Now trigger drawers
            for drawer in self.drawers:
                drawer.draw( self )
            # Finally: recursive call to children
            for child in self.children:
                child.display( )

    def hide( self ):
        """ Hides seletec widget node and all its children """
        """ Does NOT modify visible status """
        for child in self.children:
            child.hide( )
        #for drawer in self.drawers:
            #drawer.delete( self )

    # Refresh rectangle
    def _refresh_rectangle( self ):
        # 1) Four corners in local coordinates
        # 2) Translate them into absolute coordinates
        # 3) Choose the topleft corner --> rectangle's corner
        # 4) Renctangle's size is widget size
        
        # Four corners
        corners = self.translatePoints((
                                    ( self.corner[0], self.corner[1] ),
                                    ( self.corner[0]+self.size[0], self.corner[1] ),
                                    ( self.corner[0], self.corner[1]+self.size[1] ),
                                    ( self.corner[0]+self.size[0], self.corner[1]+self.size[1] ) 
                                        ))
        # Select topleftcorner
        corner =  min( corners )    #  Hope this works :-)
        self.rectangle.topleft = corner
        self.rectangle.size = self.size


    # Coordinates translation
    def translatePoints( self, points ):
        # points is a point list (list of 2-uples)
        points_translated = []
        for point in points:
            x,y = point
            # x,y --> translated to --> x_,y_
            x_ = self.origin[0] + x*self.vector_x[0] + y*self.vector_y[0]
            y_ = self.origin[1] + x*self.vector_x[1] + y*self.vector_y[1]
            # __>TODO - Matrix operation: vector_new_coords = vector_origin + vector_old_coords * M (M--> matrix with vector_x & vector_y in rows)
            points_translated.append( (x_, y_) )    
        # Recursive translation of coordinates to the parent
        if self.parent:
            points_translated = self.parent.translatePoints( points_translated )
        return points_translated
 
             
    def translatePoint( self, point ):
        # single point to be translated
        x,y = point
        # x,y --> translated to --> x_,y_
        x_ = self.origin[0] + x*self.vector_x[0] + y*self.vector_y[0]
        y_ = self.origin[1] + x*self.vector_x[1] + y*self.vector_y[1]
        # __>TODO - Matrix operation: vector_new_coords = vector_origin + vector_old_coords * M (M--> matrix with vector_x & vector_y in rows)
        point_translated = (x_,y_)
        if self.parent:
            point_translated = self.parent.translatePoint( point_translated )
        return point_translated

    # DINAMIC GEOMETRIC METHODS
    def setOrigin( self, point ):
        # DO always use this function to change origin, so that 
        #       self.rectangle is refreshed
        self.origin = point
        self._refresh_rectangle( )

    def setCorner( self, point ):
        # DO always use this function to change corner, so that 
        #       self.rectangle is refreshed
        self.corner = point
        self._refresh_rectangle( )
            
    def setSize( self, size ):
        # DO always use this function to change size, so that 
        #       self.rectangle is refreshed
        self.size = size
        self._refresh_rectangle( )

# ---------------------------------------------------------------------
# DRAWERS
# ---------------------------------------------------------------------
class Drawer( ):
    """ Abstract Drawer for drawer objetcs associated to widget (composition)"""
    # Common VALUES for DRAWERS
    HYP_FRACTION = 0.8  # Hyperfocal distance fraction of the total size of the widget

    GREY_32 = "#%02x%02x%02x" % ( 32,32,32 )
    GREY_64 = "#%02x%02x%02x" % ( 64,64,64 )
    GREY_96 = "#%02x%02x%02x" % ( 96,96,96 )
    GREY_128 = "#%02x%02x%02x" % ( 128,128,128 )
    GREY_160 = "#%02x%02x%02x" % ( 160,160,160 )
    GREY_192 = "#%02x%02x%02x" % ( 192,192,192 )
    GREY_224 = "#%02x%02x%02x" % ( 224,224,224 )
    
    GREEN_32 = "#%02x%02x%02x" % ( 0,32,0 )
    GREEN_64 = "#%02x%02x%02x" % ( 0,64,0 )
    GREEN_96 = "#%02x%02x%02x" % ( 0,96,0 )
    GREEN_128 = "#%02x%02x%02x" % ( 0,128,0 )
    GREEN_160 = "#%02x%02x%02x" % ( 0,160,0 )
    GREEN_192 = "#%02x%02x%02x" % ( 0,192,0 )
    GREEN_224 = "#%02x%02x%02x" % ( 0,224,0 )

    def __init__( self, dofmodel=None, viewmodel=None, fill=(255,255,255) , outline="", width=1, alpha=255, image=None, text="" ):
        self.dofmodel = dofmodel
        self.viewmodel = viewmodel
        self.fill = fill
        self.outline = outline
        self.width = width
        self.alpha = alpha
        self.image = image
        self.text = text
    """TODO if take out several attributes among these to several child class"""

    def draw( self, widget ):
        print >> sys.stderr,str(self)+" Method draw() of DrawInterface is abstract"
    def delete( self, widget ):
        print >> sys.stderr,str(self)+" Method delete() of DrawInterface is abstract"
    #def delete( self, widget ):
        #widget.getCanvas().delete( Drawer.getWidgetTag( widget ) )    

    # Gets a tag for the canvas items from the position in memory of the widget
    @staticmethod
    def getWidgetTag( widget ):
        return str(widget).split()[-1]

         

class TxtDrawer( Drawer ):
    """ TxtDrawer implements Drawer, so it is a Drawer  """
    def draw( self, widget):
        font = pygame.font.SysFont( "georgia", 20 )
        widget.canvas.screen.blit( font.render( "kk", True, (150,150,150)), (0,0) )

class NameDrawer( Drawer ):
    """ TestDrawer implements Drawer, so it is a Drawer  """
    """ Shows drawer's name """
    def draw( self, widget):
        textpoint = (0,0)
        textpoint_tx = widget.translatePoint( textpoint )
        font = pygame.font.SysFont( "georgia", 10 )
        widget.canvas.screen.blit( font.render( widget.name , True, (150,150,150)), textpoint_tx )


class TestDrawer( Drawer ):
    """ TestDrawer implements Drawer, so it is a Drawer  """
    """ Depicts frame, origin, vectors of the widget"""
    def draw( self, widget):
        origin = widget.origin
        corner = widget.corner
        size = widget.size
        vector_x = widget.vector_x        
        vector_y = widget.vector_y        

        #Draw wdget frame
        framepoints = ( (corner[0]+1, corner[1]+1 ),
                        (corner[0]+1, corner[1]+size[1]-1),
                        (corner[0]+size[0]-2, corner[1]+size[1]-1),
                        (corner[0]+size[0]-2, corner[1]+1)
                      )
        framepoints_tx = widget.translatePoints( framepoints )
        pygame.draw.aalines( widget.canvas.screen,
                               (150,50,50),
                                True,
                                framepoints_tx
                            ) 
        #Draw origin
        center = ((0,0),)
        radius = 2
        center_tx = widget.translatePoints( center )
        pygame.draw.circle( widget.canvas.screen,
                                (0,255,0),
                                center_tx[0],
                                radius
                            )
        #Draw corner
        center = (corner,)
        radius = 2
        center_tx = widget.translatePoints( center )
        pygame.draw.circle( widget.canvas.screen,
                                (255,255,0),
                                center_tx[0],
                                radius
                            )
                                
        #Draw vectors
        vector_x_points = ( (0,0), (10,0) )
        vector_x_points_tx = widget.translatePoints( vector_x_points )
        vector_y_points = ( (0,0), (0,10) )
        vector_y_points_tx = widget.translatePoints( vector_y_points )
        pygame.draw.lines( widget.canvas.screen,
                               (0,255,255),
                                True,
                                vector_x_points_tx
                            ) 
        pygame.draw.lines( widget.canvas.screen,
                               (255,0,255),
                                True,
                                vector_y_points_tx
                            ) 

class SlateDrawer( Drawer ):
    """ SlateDrawer implements Drawer, so it is a Drawer  """
    def draw( self, widget ):
        # Get widget coordinates
        origin = widget.origin
        corner = widget.corner
        size = widget.size
        # Get drawer attributes
        fill = self.fill
        alpha = self.alpha
        
        corners = (     corner,
                        (corner[0]+size[0]-1,corner[1]),
                        (corner[0]+size[0]-1,corner[1]+size[1]),
                        (corner[0],corner[1]+size[1])
                    )
        corners_tx = widget.translatePoints( corners)
        surf = pygame.surface.Surface( SIZE )
        surf.set_clip( widget.rectangle )
        surf.fill( (0,0,0) )
        surf.set_colorkey( (0,0,0) )
        surf.set_alpha( alpha )
        pygame.draw.polygon(   surf,
                            fill,
                            corners_tx
                        ) 
        widget.canvas.screen.blit( surf, (0,0) )

class FrameDrawer( Drawer ):
    """ FrameDrawer implements Drawer, so it is a Drawer  """
    def draw( self, widget ):
        # Get widget coordinates
        origin = widget.origin
        corner = widget.corner
        size = widget.size
        # Get drawer attributes
        fill = self.fill
        alpha = self.alpha
        width = self.width

        corners = (     corner,
                        (corner[0]+size[0]-1,corner[1]),
                        (corner[0]+size[0]-1,corner[1]+size[1]-1),
                        (corner[0],corner[1]+size[1]-1)
                    )
        corners_tx = widget.translatePoints( corners)
        surf = pygame.surface.Surface( SIZE )
        surf.set_clip( widget.rectangle )
        surf.set_colorkey( (0,0,0) )
        surf.set_alpha( alpha )
        pygame.draw.polygon(   surf,
                            fill,
                            corners_tx,
                            width
                        ) 
        widget.canvas.screen.blit( surf, (0,0) )

class ImageDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        corner = widget.corner
        # Get drawer attributes
        image = self.image
    
        surf = pygame.image.load( image )
        point = corner
        point_tx = widget.translatePoint( point )

        widget.canvas.screen.blit( surf, point_tx )
            

                        
class NDrawer( Drawer ):
    """ ... implements Drawer, so it is a Drawer  """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get drawer attributes
        fille = self.fill
        # Get model values
        n = self.dofmodel.n
        n_text = str(int(n))
    
        font_n = pygame.font.SysFont( "helvetica", widget.size[1] )
        surf = font_n.render( n_text , True, COLOR_BLUR )
        point = ( (widget.size[0] - font_n.size(n_text)[0] )/2, 0 )
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf,
                                    point_tx
                                    )

class BlurInfiniteDrawer( Drawer ):
    """ ... implements Drawer, so it is a Drawer  """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get drawer attributes
        fille = self.fill
        # Get model values
        n = int(self.dofmodel.n)

        b = reversed([ i/float(n) for i in range(n) ] )
        a = []
        c = []
        for j in range ( 1+(widget.size[0]-n)/2):
            a.append(1.) 
            c.append(0.) 
        gradient = a
        gradient.extend(b)
        gradient.extend(c)
        
        surf = pygame.Surface( widget.size )
        surf.set_colorkey( (0,0,0) )
        surf.set_clip( widget.rectangle )
        for y in range( 0, size[1]-1):
            for x in range( 0, size[0]-1 ):
                point = (x, y)
                point_tx = widget.translatePoint( point )
                surf.set_at( point_tx, gradient[x]*COLOR_BLUR )
        
        widget.canvas.screen.blit( surf, (0,0))

class BreakLabelDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        corner = widget.corner
        # Get drawer attributes
        text = self.text
    
        font = pygame.font.SysFont( "helvetica", widget.size[1]-2 )
        surf = font.render( text, True, (200,200,200) )
        point = ( (widget.size[0]-font.size(text)[0])/2, 0 )
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf,
                                    point_tx 
                                    )

class BeamDrawer( Drawer ):
    """ BeamDrawer implements Drawer, so it is a Drawer  """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get model values
        Z = self.dofmodel.Z
        
        beampoints = (  (0,0),
                        (-size[1]/(2*Z),size[1]),
                        (size[1]/(2*Z),size[1]) 
                     )
        beampoints_tx = widget.translatePoints( beampoints )
        pygame.draw.polygon( widget.canvas.screen, 
                                (220,220,220),
                                beampoints_tx
                            )
        #TODO --> antialiased polygons, etc ---> pygame.gfxdraw ??
#        pygame.draw.aalines( widget.canvas.screen, 
#                                (200,200,200),
#                                True,
#                                beampoints_tx
#                            )
class MaskDrawer( Drawer ):
    """ ... implements Drawer, so it is a Drawer  """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get drawer attributes
        fill = self.fill
        alpha = self.alpha
        # Get model values
        Z = self.dofmodel.Z
        H = self.dofmodel.H
        x_near = self.dofmodel.x_near
        x_far = self.dofmodel.x_far
    
        x_n = x_near /  H * size[1] * Drawer.HYP_FRACTION  
        try:
            x_f = x_far  /  H * size[1] * Drawer.HYP_FRACTION  
        except TypeError:
            x_f = size[1]

        lowermask = (   ( 0,0 ),
                        ( x_n / (2*Z) , x_n ),
                        ( -x_n/ (2*Z) , x_n )
                    )
        uppermask = (   ( x_f / (2*Z) , x_f ),
                        ( -x_f/ (2*Z) , x_f ),
                        (-size[1] / (2*Z), size[1]),
                        ( size[1] / (2*Z), size[1])
                    )
        
        lowermask_tx = widget.translatePoints( lowermask )
        uppermask_tx = widget.translatePoints( uppermask )

        # Temporal object image (ball) to test semi-transparent mask
        ballimage = pygame.image.load( "ball.gif" ).convert_alpha( )
        
        p_tx = widget.translatePoint( (-50,200) )
        widget.canvas.screen.blit( ballimage, p_tx )

        # Auxiliary surface for mask
        tempsurface = pygame.Surface( SIZE )
        tempsurface.set_colorkey( (0,0,0) )
        tempsurface.set_alpha( alpha )
        tempsurface.fill( (0,0,0) )
        pygame.draw.polygon( tempsurface,
                                self.fill,
                                lowermask_tx
                            )
        pygame.draw.polygon( tempsurface,
                                self.fill,
                                uppermask_tx
                            )
        widget.canvas.screen.blit( tempsurface, (0,0)  )


class HypLineDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get model values
        H = self.dofmodel.H
        
        #Line points
        start = (-size[0]/2,   int(size[1] * Drawer.HYP_FRACTION) )
        end   = ( size[0]/2,   int(size[1] * Drawer.HYP_FRACTION) )
    
        start_tx = widget.translatePoint( start )
        end_tx = widget.translatePoint( end )

        pygame.draw.line(widget.canvas.screen, (0,0,0) , start_tx, end_tx, 2 )
           
class FocusLineDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get model values
        x0 = self.dofmodel.x0
        H = self.dofmodel.H
        x_near = self.dofmodel.x_near
        x_far = self.dofmodel.x_far
            

        #Line points - FOCUS LINE
        start = (-size[0]/2,   size[1] * Drawer.HYP_FRACTION * x0 / H )
        end   = ( size[0]/2,   size[1] * Drawer.HYP_FRACTION * x0 / H )
        start_tx = widget.translatePoint( start )
        end_tx = widget.translatePoint( end )
        pygame.draw.line(widget.canvas.screen, (0,0,0) , start_tx, end_tx, 1 )
        #Line points - NEAR LINE
        start = (-size[0]/2,   size[1] * Drawer.HYP_FRACTION * x_near / H )
        end   = ( size[0]/2,   size[1] * Drawer.HYP_FRACTION * x_near / H )
        start_tx = widget.translatePoint( start )
        end_tx = widget.translatePoint( end )
        pygame.draw.line(widget.canvas.screen, (0,0,0) , start_tx, end_tx, 1 )
        #Line points - FAR LINE
        try:
            start = (-size[0]/2,   size[1] * Drawer.HYP_FRACTION * x_far / H )
            end   = ( size[0]/2,   size[1] * Drawer.HYP_FRACTION * x_far / H )
        except TypeError:
            # Raised if x_far is "infinite"
            start = (-size[0]/2,   size[1]+1 )
            end   = ( size[0]/2,   size[1]+1 )
            
        start_tx = widget.translatePoint( start )
        end_tx = widget.translatePoint( end )
        pygame.draw.line(widget.canvas.screen, (0,0,0) , start_tx, end_tx, 1 )
        
class BlurConeDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get model values
        x0 = self.dofmodel.x0
        H = self.dofmodel.H
        n = self.dofmodel.n
        
        # Aux function for calculating blur at each distance
        def blur( x_px ):  # returns blur for the real x distance corresponding to position x_px in the bar
            x = H * x_px / ( size[1] * Drawer.HYP_FRACTION ) 
            try:
                blur = n * abs((x-x0)/x)
            except ZeroDivisionError, e:
                blur = "infinite"
            return blur
        
        surf = pygame.Surface( SIZE )
        surf.set_colorkey( (0,0,0) )
        surf.set_clip( widget.rectangle )
        for x_px in range( 1, size[1]):
            b = blur( x_px )
            if b < 0. : b=1.
            for y_px in range( -size[0]/2, size[0]/2 ):
                if y_px < -b/2:
                    val = 1.
                elif -b/2 <= y_px < b/2:
                    val =  1.0/2 - 1/b * (y_px )
                else:
                    val = 0.
                point = ( y_px, x_px )
                point_tx = widget.translatePoint( point )
                surf.set_at( point_tx, val*COLOR_BLUR )
                #widget.canvas.screen.set_at( point_tx, (255*val, 0, 0) )
        widget.canvas.screen.blit( surf, (0,0))
        
class FocusedRangeDrawer( Drawer ):
    """ ... is a Drawer """
    """ Focused range in Distance Bar"""
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get drawer attributes
        fill = self.fill
        alpha = self.alpha
        # Get model values
        x0 = self.dofmodel.x0
        H = self.dofmodel.H
        n = self.dofmodel.n
        x_near = self.dofmodel.x_near
        x_far = self.dofmodel.x_far
    
        x_n = x_near /  H * size[1] * Drawer.HYP_FRACTION  
        try:
            x_f = x_far  /  H * size[1] * Drawer.HYP_FRACTION  
        except TypeError:
            x_f = size[1]

        # Focused range 
        points = (      (0, x_n ),
                        (size[0], x_n),
                        (size[0], min(x_f,size[1])),
                        (0, min(x_f,size[1]))
                    )
        points_tx = widget.translatePoints( points )
        pygame.draw.polygon( widget.canvas.screen,
                            fill,
                            points_tx,
                            )
        
        # DOF labels
        font_x0 = pygame.font.SysFont( "arial", 16 )
        font_dof = pygame.font.SysFont( "arial", 10 )
        x0_ =  x0 / H * size[1] * Drawer.HYP_FRACTION
        x_n = x_near / H * size[1] * Drawer.HYP_FRACTION  
        try:
            x_f = x_far / H * size[1] * Drawer.HYP_FRACTION 
        except TypeError:
            x_f = "inf"
           
        hyp_ = H * Drawer.HYP_FRACTION
        
        if x0 >= 10.:
            x0_text = "%.0f" % x0
        elif x0 >= 1.:
            x0_text = "%1.1f" % x0
        else:
            x0_text = "%.2f" % x0

        if x_near >= 10.:
            x_near_text = "%.0f" % x_near
        elif x_near >= 1.:
            x_near_text = "%1.1f" % x_near
        else:
            x_near_text = "%.2f" % x_near

        if x_far == "infinite":
            x_far_text = x_far
        elif x_far >= 10.:
            x_far_text = "%.0f" % x_far
        elif x_far >= 1.:
            x_far_text = "%1.1f" % x_far
        else:
            x_far_text = "%.2f" % x_far
    
        if x0_-x_n > font_dof.get_linesize():
            x_pos = x0_
        else:
            x_pos = x_f

        widget.canvas.screen.blit( 
                                    font_x0.render(  
                                                    x0_text,
                                                    True,
                                                    (250,250,250)
                                                ),
                                    widget.translatePoint( ( 4, x_pos+font_x0.get_linesize() ) )
                                )

        if x0_-x_n > font_dof.get_linesize():
            widget.canvas.screen.blit( 
                                        font_dof.render(  
                                                        x_near_text,
                                                        True,
                                                        (250,250,250)
                                                    ),
                                        widget.translatePoint( ( 4, x_n +font_dof.get_linesize() ) )
                                    )
            if x_f < size[1]:
                widget.canvas.screen.blit( 
                                            font_dof.render(  
                                                            x_far_text,
                                                            True,
                                                            (250,250,250)
                                                        ),
                                            widget.translatePoint( ( 4, x_f +font_dof.get_linesize() ) )
                                        )
class DragButtonDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        corner = widget.corner
        origin = widget.origin
        # Get drawer attributes

        # Get model values
        x0 = self.dofmodel.x0
        H = self.dofmodel.H
        x_near = self.dofmodel.x_near

        # Focused & near distance in pixels
        focusdist_px = widget.parent.size[1] * Drawer.HYP_FRACTION * x0 / H   
        neardist_px  = widget.parent.size[1] * Drawer.HYP_FRACTION * x_near / H
        

        # Point where the widget is anchored
        if x0 <= H/Drawer.HYP_FRACTION :        # Dragbutton is at focused distance
            point = (   widget.parent.size[0]/2-40-40-widget.size[0],
                        focusdist_px + widget.size[1]/2 )
        else:                                   # Dragbutton at x_near
            point = (   widget.parent.size[0]/2-40-40-widget.size[0],
                        neardist_px + widget.size[1]/2 )
        # 1st of all: set widget position dinamically!!!
        widget.setOrigin( point )

        # 2nd: now we load the dragbutton image
        # Image anchor point
        anchorpoint = (0,0)
        anchorpoint_tx = widget.translatePoint( anchorpoint )
        # Translate coordinates

        imagepath = "images/dragbutton.png"
        surf = pygame.image.load(imagepath)
        # Attach image to canvas
        widget.canvas.screen.blit( surf, anchorpoint_tx )
        
        
        # 3rd: add a black segment in the middle
        segment_start = (0,  widget.size[1]/2)
        segment_end   = (widget.size[0], widget.size[1]/2 )

        segment_start_tx = widget.translatePoint( segment_start )
        segment_end_tx = widget.translatePoint( segment_end )
              
        pygame.draw.line( widget.canvas.screen, 
                            (0,0,0),
                            segment_start_tx,
                            segment_end_tx,
                            1
                        )
        
class CloseConeDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        origin = widget.origin
        corner = widget.corner
        size = widget.size 
        # Get drawer attributes
        fill = self.fill
        alpha = self.alpha
        # Get model data
        Z = self.dofmodel.Z
        x0 = self.dofmodel.x0
        x_far = self.dofmodel.x_far
        x_near = self.dofmodel.x_near


        # Draw cone on auxiliary tempsurface
        cone = (    (0,0),
                    ( (corner[1]+size[1])/(2*Z), corner[1]+size[1]),
                    ( -(corner[1]+size[1])/(2*Z), corner[1]+size[1])
               )
        cone_tx = widget.translatePoints( cone )
        
        tempsurface = pygame.Surface( SIZE )
        tempsurface.set_clip( widget.rectangle )
        tempsurface.set_colorkey( (0,0,0) )
        tempsurface.set_alpha( alpha )
        tempsurface.fill( (0,0,0) )
        pygame.draw.polygon( tempsurface,
                                self.fill,
                                cone_tx
                            )
        widget.canvas.screen.blit( tempsurface, (0,0)  )

        # Draw focused line (temporal) TODO
        focus_segment = (   (-size[0]/2, corner[1]+size[1]/2),
                            ( size[0]/2, corner[1]+size[1]/2)
                        )
        focus_segment_tx = widget.translatePoints( focus_segment )
        pygame.draw.line( widget.canvas.screen,
                                (0,0,0),
                                *focus_segment_tx
                            ) 
        # Draw far line (temporal) TODO
        focus_dist_px = corner[1]+size[1]/2  # Focused distance in pixels
        far_dist_px = (x_far/x0 ) * focus_dist_px
        far_segment = (     (-size[0]/2, far_dist_px),
                            (+size[0]/2, far_dist_px)
                        )
        far_segment_tx = widget.translatePoints( far_segment )
        pygame.draw.line( widget.canvas.screen,
                                (0,0,0),
                                *far_segment_tx
                            ) 
        # Draw near line (temporal) TODO
        focus_dist_px = corner[1]+size[1]/2  # Focused distance in pixels
        near_dist_px = (x_near/x0 ) * focus_dist_px
        near_segment = (     (-size[0]/2, near_dist_px),
                            (+size[0]/2, near_dist_px)
                        )
        near_segment_tx = widget.translatePoints( near_segment )
        pygame.draw.line( widget.canvas.screen,
                                (0,0,0),
                                *near_segment_tx
                            ) 
        

# DEPRECATED ..
class CloseupConeDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        # Get drawer attributes
        fill = self.fill
        alpha = self.alpha
        # Get model data
        x0 = self.dofmodel.x0
        Z = self.dofmodel.Z
        x_near = self.dofmodel.x_near
        x_far = self.dofmodel.x_far

        FRAMEPIXELS = 300 # This is the length of the "focused segment"
        
        # Distance to camera in px
        pixels_to_camera = FRAMEPIXELS * Z
        print "ASH__> pixels_to_camera = ",pixels_to_camera
        # Set widget origin
        new_origin = (  widget.size[0]/2,
                        widget.size[1]/2 + pixels_to_camera )
        new_corner = (  -new_origin[0],
                        new_origin[1]-widget.size[1] )
        widget.setOrigin( new_origin )
        widget.setCorner( new_corner )

        # Draw beam
        beampoints = (      ( -widget.corner[1]/(Z*2), widget.corner[1] ),
                            ( widget.corner[1]/(Z*2) , widget.corner[1] ),
                            ( (widget.corner[1]+widget.size[1])/(Z*2), widget.corner[1]+widget.size[1]),
                            ( -(widget.corner[1]+widget.size[1])/(Z*2), widget.corner[1]+widget.size[1])
                    )
        beampoints_tx = widget.translatePoints( beampoints) 
        pygame.draw.polygon(    widget.canvas.screen,
                                (220,220,220),
                                beampoints_tx
                            )
        # Draw mask
        
        x_near_px = pixels_to_camera * x_near / x0
        x_far_px = pixels_to_camera * x_far / x0

        lowermask = (       ( -widget.corner[1]/(Z*2), widget.corner[1] ),
                            ( widget.corner[1]/(Z*2) , widget.corner[1] ),
                            ( x_near_px/(Z*2), x_near_px ),
                            ( -x_near_px/(Z*2), x_near_px)
                    )
        uppermask = (      ( -x_far/(Z*2), x_far ),
                            ( x_far/(Z*2) , x_far ),
                            ( (widget.corner[1]+widget.size[1])/(Z*2), widget.corner[1]+widget.size[1]),
                            ( -(widget.corner[1]+widget.size[1])/(Z*2), widget.corner[1]+widget.size[1])
                    )
        lowermask_tx = widget.translatePoints( lowermask )
        uppermask_tx = widget.translatePoints( uppermask )
        ## Auxiliary surface for mask
        #tempsurface = pygame.Surface( SIZE )
        #tempsurface.set_colorkey( (0,0,0) )
        #tempsurface.set_alpha( alpha )
        #tempsurface.fill( (0,0,0) )
        #pygame.draw.polygon( tempsurface,
                                #self.fill,
                                #lowermask_tx
                            #)
        #pygame.draw.polygon( tempsurface,
                                #self.fill,
                                #uppermask_tx
                            #)
        #widget.canvas.screen.blit( tempsurface, (0,0)  )
        
        # Draw focus segment (temporal)
        point_left = ( -FRAMEPIXELS/2 , pixels_to_camera )
        point_right = ( FRAMEPIXELS/2 , pixels_to_camera )
        point_left_tx = widget.translatePoint( point_left )
        point_right_tx = widget.translatePoint( point_right )
        pygame.draw.line( widget.canvas.screen, 
                            (0,0,0),
                            point_left_tx,
                            point_right_tx
                        )
        # Draw near segment (temporal)
        point_left = ( -x_near_px/Z , x_near_px )
        point_right = ( x_near_px/Z , x_near_px )
        point_left_tx = widget.translatePoint( point_left )
        point_right_tx = widget.translatePoint( point_right )
        pygame.draw.line( widget.canvas.screen, 
                            (0,0,0),
                            point_left_tx,
                            point_right_tx
                        )
        # Draw far segment (temporal)
        point_left = ( -x_far_px/Z , x_far_px )
        point_right = ( x_far_px/Z , x_far_px )
        point_left_tx = widget.translatePoint( point_left )
        point_right_tx = widget.translatePoint( point_right )
        pygame.draw.line( widget.canvas.screen, 
                            (0,0,0),
                            point_left_tx,
                            point_right_tx
                        )

        
        
        
                                                    
class LabelDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        corner = widget.corner
        # Get drawer attributes
        text = self.text
    
        font = pygame.font.SysFont( "helvetica", widget.size[1]/3 )
        surf = font.render( text, True, (200,200,200) )
        point = ( 0, widget.size[1]/3 )
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf,
                                    point_tx 
                                    )

class DisplayfDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size # Get model values
        f = self.dofmodel.f
        f_txt = "%1.1f" % f

        # White background, 1px black border
        points = (  (0, 0),
                    (0, size[1]-1),
                    (size[0]-1, size[1]-1),
                    (size[0]-1, 0)
                )
        points_tx = widget.translatePoints( points )
        pygame.draw.polygon( widget.canvas.screen,
                                (0,0,0),
                                points_tx 
                            )
        pygame.draw.polygon( widget.canvas.screen,
                                (50,50,50),
                                points_tx,
                                1
                            )
                    
        font = pygame.font.SysFont( "helvetica", int(widget.size[1]*0.5) )
        surf = font.render( f_txt, True, (0,255,0) )
        point = ( widget.size[0]*0.25, widget.size[1]*0.25 )
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf,
                                    point_tx 
                                    )

class DisplayFDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get model values
        F = self.dofmodel.F
        F_txt = "%1.0f" % F

        # White background, 1px black border
        points = (  (0, 0),
                    (0, size[1]-1),
                    (size[0]-1, size[1]-1),
                    (size[0]-1, 0)
                )
        points_tx = widget.translatePoints( points )
        pygame.draw.polygon( widget.canvas.screen,
                                (0,0,0),
                                points_tx 
                            )
        pygame.draw.polygon( widget.canvas.screen,
                                (50,50,50),
                                points_tx,
                                1
                            )
                    
        font = pygame.font.SysFont( "helvetica", int(widget.size[1]*0.5) )
        surf = font.render( F_txt, True, (0,255,0) )
        point = ( widget.size[0]*0.25, widget.size[1]*0.25 )
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf,
                                    point_tx 
                                    )

class DisplaySDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get model values
        S = self.dofmodel.S
        S_txt = "%1.0f" % S

        # White background, 1px black border
        points = (  (0, 0),
                    (0, size[1]-1),
                    (size[0]-1, size[1]-1),
                    (size[0]-1, 0)
                )
        points_tx = widget.translatePoints( points )
        pygame.draw.polygon( widget.canvas.screen,
                                (0,0,0),
                                points_tx 
                            )
        pygame.draw.polygon( widget.canvas.screen,
                                (50,50,50),
                                points_tx,
                                1
                            )
                    
        font = pygame.font.SysFont( "helvetica", int(widget.size[1]*0.5) )
        surf = font.render( S_txt, True, (0,128,255) )
        point = ( widget.size[0]*0.25, widget.size[1]*0.25 )
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf,
                                    point_tx 
                                    )

class DisplaymDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get model values
        m = self.dofmodel.m
        m_txt = "%4d" % m

        # White background, 1px black border
        points = (  (0, 0),
                    (0, size[1]-1),
                    (size[0]-1, size[1]-1),
                    (size[0]-1, 0)
                )
        points_tx = widget.translatePoints( points )
        pygame.draw.polygon( widget.canvas.screen,
                                (0,0,0),
                                points_tx 
                            )
        pygame.draw.polygon( widget.canvas.screen,
                                (50,50,50),
                                points_tx,
                                1
                            )
                    
        font = pygame.font.SysFont( "helvetica", int(widget.size[1]*0.4) )
        surf = font.render( m_txt, True, (0,128,255) )
        point = ( 1, widget.size[1]*0.25 )
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf,
                                    point_tx 
                                    )
        
class LandscapeButtonDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get model values
        mode = self.viewmodel.mode
        if not mode:    # Landscape mode
            bcolor = ( 255, 100, 100 )  #Selected
        else:           # Object mode
            bcolor = ( 100, 100, 100 ) # Not selected
        
        o = (0, 0)
        o_tx = widget.translatePoint( o )
        rect = pygame.Rect( o_tx, size )
        
        pygame.draw.rect( widget.canvas.screen,
                            bcolor,
                            rect 
                        )
                            
class ObjectButtonDrawer( Drawer ):
    """ ... is a Drawer """
    def draw( self, widget ):
        # Get widget coordinates
        size = widget.size
        # Get model values
        mode = self.viewmodel.mode
        if not mode:    # Landscape mode
            bcolor = ( 100, 100, 100 ) # Not selected
        else:           # Object mode
            bcolor = ( 255, 100, 100 )  #Selected
        
        o = (0, 0)
        o_tx = widget.translatePoint( o )
        rect = pygame.Rect( o_tx, size )
        
        pygame.draw.rect( widget.canvas.screen,
                            bcolor,
                            rect 
                        )

    
# HANDLERS
class Handler( ):
    """ Abstract Handler for drawer objetcs associated to widget (composition)"""
    def handle( self, event=None ):
        print >> sys.stderr,str(self)+" Method handle() of DrawInterface is abstract"

    def __init__( self, dofmodel=None, viewmodel=None, fill="white", outline="", width=1 ):
        # TODO --> see if dofmodel should not be a parameter here and gotten 
        #           from widget. Same for viewmodel
        self.dofmodel = dofmodel
        self.viewmodel = viewmodel
        self.fill = fill
        self.outline = outline
        self.width = width
        self.widget=None #Backreference to widget, initialized by widget when handler is attached

class DragButtonHandler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        # Get handler attributes
        widget = self.widget
        dofmodel = self.dofmodel
        # Get widget coordinates
        corner = widget.corner
        # Get model data
        x0 = dofmodel.x0
        x_near = dofmodel.x_near
        H = dofmodel.H
        
        def _load_turnedOnImage():
            # 1st we turn the button on
            surf = pygame.image.load( "images/dragbutton_green.png" )
            point = corner
            point_tx = widget.translatePoint( point )
            widget.canvas.screen.blit( surf, point_tx )
            # Refresh image
            pygame.display.update( )

        _load_turnedOnImage( )
        # Then wait for button release to update the model

        #       Get model data
        # Init relative movement of the mouse
        pygame.mouse.get_rel( )
        while True:
            for localevent in pygame.event.get( ):
                if localevent.type == pygame.MOUSEBUTTONUP:
                    # Forces redraw and exits
                    dofmodel.set_x0( dofmodel.x0 )
                    return
                if localevent.type == pygame.MOUSEMOTION:
                    delta_x, delta_y = pygame.mouse.get_rel( )
                    # Convert delta_y (px) to change in x0 or x_near
                    if delta_y != 0:

                        if  x0 <= H/Drawer.HYP_FRACTION :       # Dragbutton is at focused distance 
                            x0_px = widget.parent.size[1] * Drawer.HYP_FRACTION * x0 / H
                            # Add pixel increment
                            x0_px -= delta_y
                            # Convert back to x0 in meters
                            x0 = x0_px * H / ( widget.parent.size[1] * Drawer.HYP_FRACTION )
                            dofmodel.set_x0( x0 )
                        else:                                   # Dragbutton at x_near
                             
                            x_near_px = widget.parent.size[1] * Drawer.HYP_FRACTION * x_near / H
                            # Add pixel increment
                            x_near_px -= delta_y
                            # Convert back to x0 in meters
                            x_near = x_near_px * H / ( widget.parent.size[1] * Drawer.HYP_FRACTION )
                            dofmodel.set_x_near( x_near )
                    _load_turnedOnImage( )
                        
                   #TODO  __> 20110411 --> CONTINUE HERE      
                    
class QuitButton_Handler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        # Set closeup widget to NOT visible
        print "ASH__>",self.widget.parent.name
        print dir(self.widget.parent)
        self.widget.parent.setVisible( False )
        self.widget.parent.hide()
        # Now sets x0 so that n=5 , the limit of the detail 
        H = self.dofmodel.H
        self.dofmodel.set_x0(H/5) 
        
        

class x0_WheelHandler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        pygame.mouse.set_cursor( *pygame.cursors.diamond )
        x_init, y_init = event.pos
        x0_init = self.dofmodel.x0
        while True:
            for localevent in pygame.event.get( )[:3]:
                if localevent.type == pygame.MOUSEBUTTONUP:
                    pygame.mouse.set_cursor( *pygame.cursors.arrow )
                    return
                if localevent.type == pygame.MOUSEMOTION:
                    x_current, y_current = pygame.mouse.get_pos( )
                    x_val = x_current-x_init
                    if not x_val%2:
                        self.dofmodel.set_x0( x0_init + x_val/2 )
                        print self.dofmodel.set_x0

class F_WheelHandler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        pygame.mouse.set_cursor( *pygame.cursors.diamond )
        x_init, y_init = event.pos
        F_init = self.dofmodel.F
        while True:
            for localevent in pygame.event.get( )[:3]:
                if localevent.type == pygame.MOUSEBUTTONUP:
                    pygame.mouse.set_cursor( *pygame.cursors.arrow )
                    return
                if localevent.type == pygame.MOUSEMOTION:
                    x_current, y_current = pygame.mouse.get_pos( )
                    x_val = x_current-x_init
                    print x_val
                    if not x_val%2:
                        self.dofmodel.set_F( F_init + x_val/2 )

class ButtonLeft_f_Handler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        # Get handler attributes
        widget = self.widget
        dofmodel = self.dofmodel
        # Get widget coordinates
        corner = widget.corner

        # 1st we turn the button on
        surf = pygame.image.load( "images/buttonleft_green.png" )
        point = corner
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf, point_tx )
        # Refresh
        pygame.display.update( )
    
        # Then wait for button release to update the model
        while True:
            for localevent in pygame.event.get( ):
                if localevent.type == pygame.MOUSEBUTTONUP:
                    dofmodel.decrease_f( ) 
                    return

class ButtonRight_f_Handler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        # Get handler attributes
        widget = self.widget
        dofmodel = self.dofmodel
        # Get widget coordinates
        corner = widget.corner

        # 1st we turn the button on
        surf = pygame.image.load( "images/buttonright_green.png" )
        point = corner
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf, point_tx )
        # Refresh
        pygame.display.update( )
    
        # Then wait for button release to update the model
        while True:
            for localevent in pygame.event.get( ):
                if localevent.type == pygame.MOUSEBUTTONUP:
                    dofmodel.increase_f( ) 
                    return

class ButtonLeft_F_Handler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        # Get handler attributes
        widget = self.widget
        dofmodel = self.dofmodel
        # Get widget coordinates
        corner = widget.corner

        # 1st we turn the button on
        surf = pygame.image.load( "images/buttonleft_green.png" )
        point = corner
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf, point_tx )
        # Refresh
        pygame.display.update( )
    
        # Then wait for button release to update the model
        while True:
            for localevent in pygame.event.get( ):
                if localevent.type == pygame.MOUSEBUTTONUP:
                    dofmodel.decrease_F( ) 
                    return

class ButtonRight_F_Handler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        # Get handler attributes
        widget = self.widget
        dofmodel = self.dofmodel
        # Get widget coordinates
        corner = widget.corner

        # 1st we turn the button on
        surf = pygame.image.load( "images/buttonright_green.png" )
        point = corner
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf, point_tx )
        # Refresh
        pygame.display.update( )
    
        # Then wait for button release to update the model
        while True:
            for localevent in pygame.event.get( ):
                if localevent.type == pygame.MOUSEBUTTONUP:
                    dofmodel.increase_F( ) 
                    return

class ButtonLeft_S_Handler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        # Get handler attributes
        widget = self.widget
        dofmodel = self.dofmodel
        # Get widget coordinates
        corner = widget.corner

        # 1st we turn the button on
        surf = pygame.image.load( "images/buttonleft_blue.png" )
        point = corner
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf, point_tx )
        # Refresh
        pygame.display.update( )
    
        # Then wait for button release to update the model
        while True:
            for localevent in pygame.event.get( ):
                if localevent.type == pygame.MOUSEBUTTONUP:
                    dofmodel.decrease_S( ) 
                    return

class ButtonRight_S_Handler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        # Get handler attributes
        widget = self.widget
        dofmodel = self.dofmodel
        # Get widget coordinates
        corner = widget.corner

        # 1st we turn the button on
        surf = pygame.image.load( "images/buttonright_blue.png" )
        point = corner
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf, point_tx )
        # Refresh
        pygame.display.update( )
    
        # Then wait for button release to update the model
        while True:
            for localevent in pygame.event.get( ):
                if localevent.type == pygame.MOUSEBUTTONUP:
                    dofmodel.increase_S( ) 
                    return

class ButtonLeft_m_Handler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        # Get handler attributes
        widget = self.widget
        dofmodel = self.dofmodel
        # Get widget coordinates
        corner = widget.corner

        # 1st we turn the button on
        surf = pygame.image.load( "images/buttonleft_blue.png" )
        point = corner
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf, point_tx )
        # Refresh
        pygame.display.update( )
    
        # Then wait for button release to update the model
        while True:
            for localevent in pygame.event.get( ):
                if localevent.type == pygame.MOUSEBUTTONUP:
                    dofmodel.decrease_m( ) 
                    return

class ButtonRight_m_Handler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        # Get handler attributes
        widget = self.widget
        dofmodel = self.dofmodel
        # Get widget coordinates
        corner = widget.corner

        # 1st we turn the button on
        surf = pygame.image.load( "images/buttonright_blue.png" )
        point = corner
        point_tx = widget.translatePoint( point )
        widget.canvas.screen.blit( surf, point_tx )
        # Refresh
        pygame.display.update( )

        # Then wait for button release to update the model while True:
        while True:
            for localevent in pygame.event.get( ):
                if localevent.type == pygame.MOUSEBUTTONUP:
                    dofmodel.increase_m( ) 
                    return

class LandscapeButtonHandler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        print "HANDLER in ", self.widget.name
        print self.viewmodel.mode
        if self.viewmodel.mode is True:
            self.viewmodel.set_mode( False )

class ObjectButtonHandler( Handler ):
    """ ... is a Handler """
    def handle( self, event=None ):
        print "HANDLER in ", self.widget.name
        print self.viewmodel.mode
        if self.viewmodel.mode is False:
            self.viewmodel.set_mode( True )
    

# ---------------------------------------------------------------------
# CANVAS
# ---------------------------------------------------------------------
class MyCanvas( ):

    def __init__( self, size ):
        self.screen = pygame.display.set_mode( size, 0, 32 ) 
        
        # Widget visibility stack
        self.widget_stack = []

    def pop( self , widget ):
        if widget.handler:
            self.widget_stack.append( widget )

    def clean_stack( self ):
        self.widget_stack = []
        
    def get_focused_widget( self ):
        position = pygame.mouse.get_pos( ) # Get mouse position
        for widget in reversed( self.widget_stack ):
            if widget.rectangle.collidepoint( position ):
                return widget
        return None
                 
    def get_focused_handler( self ):
        position = pygame.mouse.get_pos( ) # Get mouse position
        for widget in reversed( self.widget_stack ):
            print widget.rectangle,widget.name #__>ASH
            if widget.rectangle.collidepoint( position ):
                if widget.handler:
                    return widget.handler
        return None
        

# ---------------------------------------------------------------------
# CONTROLLER
# ---------------------------------------------------------------------

class MyController( ObserverInterface ):
    
    def update( self, caller ):
        if caller is self.dofmodel: 
            # If n>5 , trigger closeup widget
            if self.dofmodel.n > 6:
                self.widgets['close'].setVisible( True )
            else:
                self.widgets['close'].setVisible( False )
        if caller is self.viewmodel: 
            # mode
            mode = self.viewmodel.mode
            if mode is False:
                self.widgets['landscapemode'].setVisible( True )
                self.widgets['objectmode'].setVisible( False )
            else:
                self.widgets['landscapemode'].setVisible( False )
                self.widgets['objectmode'].setVisible( True )
        self._redraw_widgets( )
    
    def _redraw_widgets( self ):
        self.canvas.screen.fill( (0,0,0) )
        self.widgets["root"].display( )
        pygame.display.flip( )
    
                  
        

    def __init__( self ):
        pygame.init( )
        self.canvas = MyCanvas( SIZE )

        # OBSERVER attributes
        self.dofmodel = DOFModel( F=35, x0=2.0 )
        self.dofmodel.registerObserver( self ) # Registers into the model
        
        self.viewmodel = ViewModel( )
        self.viewmodel.registerObserver( self ) # Registers into the model
        self.viewmodel._printState( )
        

        # VIEW - Widget composite
        self.widgets = self._build_mainview( )
        self._redraw_widgets( )


        # EVENT LOOP        
        delta_F=0
        while True:
            for event in pygame.event.get( ):
                if event.type == pygame.QUIT: sys.exit( )
            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        #self.viewmodel.set_mode( True )
                        x0=self.dofmodel.x0
                        self.dofmodel.set_x0( x0 *2 )
                    if event.key == pygame.K_DOWN:
                        #self.viewmodel.set_mode( False )
                        x0=self.dofmodel.x0
                        self.dofmodel.set_x0( x0 *0.5 )
                    if event.key == pygame.K_LEFT:
                        delta_F = -10
                    if event.key == pygame.K_RIGHT:
                        delta_F = +10
                    if event.key == pygame.K_ESCAPE:
                        pass
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        delta_F = 0
                    if event.key == pygame.K_RIGHT:
                        delta_F = 0

                # MOUSEBUTTONDOWN is like finger on display
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # ASH__> 
                    print "ASH__> M= ",self.dofmodel.M
                    # 1st we need to get a handler if there is one under the position
                    handler = self.canvas.get_focused_handler( )
                    print handler
                    print [ item.name for item in  self.canvas.widget_stack ] #__>ASH
                    print event.pos
                    if  handler:
                        handler.handle( event )

            if delta_F != 0:
                self.dofmodel.set_F( self.dofmodel.F + delta_F )
            
            
    def _build_mainview( self ):
        # Returns widgets in a dictionary

        # Drawers 
        d_test = TestDrawer( dofmodel = self.dofmodel )
        
        #Slates
        d_slate_background = SlateDrawer ( dofmodel = self.dofmodel )
        d_slate_distancebar = SlateDrawer ( fill=(50,50,50), alpha = 200 )
        d_slate_framebar = SlateDrawer( fill=(200,200,200) )
        d_slate_infinite = SlateDrawer( fill=(0,0,0) )
        d_slate_cameracontrols = SlateDrawer( fill=(50,50,50) )
        d_slate_closeup = SlateDrawer ( fill=(50,50,50), alpha = 100 )
        d_slate_closeup_inner = SlateDrawer( fill=(1,1,1) )
        d_slate_close = SlateDrawer ( fill=(50,50,50), alpha = 100 )
        d_slate_close_inner0 = SlateDrawer( fill=(1,1,1), alpha = 200 )

        d_test = TestDrawer( dofmodel= self.dofmodel ) 
        d_name = NameDrawer( )

        d_blurinfinite = BlurInfiniteDrawer( dofmodel = self.dofmodel )
        d_n = NDrawer( dofmodel = self.dofmodel )
        
        d_blurlabel = BreakLabelDrawer( text="blur" )
        d_distancelabel = BreakLabelDrawer( text="dist" )
        d_unitslabel = BreakLabelDrawer( text="m" )
    
        d_beam = BeamDrawer( dofmodel = self.dofmodel )
        d_hypline = HypLineDrawer( dofmodel = self.dofmodel )
        d_focusline = FocusLineDrawer( dofmodel = self.dofmodel )
        d_mask = MaskDrawer( dofmodel = self.dofmodel, fill=(10,10,10), alpha=128 )
        d_blurcone = BlurConeDrawer( dofmodel = self.dofmodel )
        d_focusedrange = FocusedRangeDrawer( self.dofmodel, fill=(80,80,80) )
        d_dragbutton = DragButtonDrawer( dofmodel = self.dofmodel )

        d_close_cone = CloseConeDrawer( dofmodel = self.dofmodel, fill =(200,200,200), alpha=255 )

        d_camera = ImageDrawer( image= "images/camera.png" )
        d_frame_camerainputs = FrameDrawer( fill=(100,100,100), width = 1 )
        d_frame_group = FrameDrawer( fill=(100,100,100), width = 1 )
        d_label_f = LabelDrawer( text="    f" )
        d_label_F = LabelDrawer( text="F(mm)" )
        d_label_S = LabelDrawer( text="S(mm)" )
        d_label_m = LabelDrawer( text="  tiles" )
        d_display_f = DisplayfDrawer( dofmodel = self.dofmodel )
        d_display_F = DisplayFDrawer( dofmodel = self.dofmodel )
        d_display_S = DisplaySDrawer( dofmodel = self.dofmodel )
        d_display_m = DisplaymDrawer( dofmodel = self.dofmodel )
        d_buttonleft = ImageDrawer( image="images/buttonleft.png" ) 
        d_buttonright = ImageDrawer( image="images/buttonright.png" ) 
        d_quitbutton = ImageDrawer( image="images/quitbutton.png" )
        
        # Handlers
        h_dragbutton = DragButtonHandler( dofmodel = self.dofmodel )
        h_quitbutton = QuitButton_Handler( dofmodel = self.dofmodel, viewmodel = self.viewmodel )
        h_buttonleft_f = ButtonLeft_f_Handler( dofmodel = self.dofmodel )
        h_buttonright_f = ButtonRight_f_Handler( dofmodel = self.dofmodel )
        h_buttonleft_F = ButtonLeft_F_Handler( dofmodel = self.dofmodel )
        h_buttonright_F = ButtonRight_F_Handler( dofmodel = self.dofmodel )
        h_buttonleft_S = ButtonLeft_S_Handler( dofmodel = self.dofmodel )
        h_buttonright_S = ButtonRight_S_Handler( dofmodel = self.dofmodel )
        h_buttonleft_m = ButtonLeft_m_Handler( dofmodel = self.dofmodel )
        h_buttonright_m = ButtonRight_m_Handler( dofmodel = self.dofmodel )
        h_landscapebutton = LandscapeButtonHandler( viewmodel = self.viewmodel )
        h_objectbutton = ObjectButtonHandler( viewmodel = self.viewmodel )
        
        #TODO --> coordinates start in 0 or 1?
        w_root = DOFwidget( self.canvas, 
                                    drawers = [ ], 
                                    size = SIZE, 
                                    origin = (0, 0),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "root"
                                )

        w_landscapemode = DOFwidget( self.canvas, 
                                    drawers = [ ], 
                                    size = (WIDTH, 760),
                                    origin = (0, 0),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "landscapemode",
                                    parent = w_root
                                )
        w_objectmode = DOFwidget( self.canvas, 
                                    drawers = [ d_test, d_name ], 
                                    size = (WIDTH, 760), 
                                    origin = (0, 0),
                                    corner = (0, 0),
                                    visible = False,
                                    name = "objectmode",
                                    parent = w_root
                                )

        # INFINITE
        w_infinite = DOFwidget( self.canvas, 
                                    drawers = [ d_slate_infinite ], 
                                    size = (WIDTH, 100),
                                    origin = (0, 0),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "infinite",
                                    parent = w_landscapemode
                                )
        w_blurinfinite = DOFwidget( self.canvas, 
                                    drawers = [ d_blurinfinite ], 
                                    size = (80, 30),
                                    origin = (0, 0),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "blurinfinite",
                                    parent = w_infinite
                                )
        w_n = DOFwidget( self.canvas, 
                                    drawers = [ d_n ], 
                                    size = (80, 70),
                                    origin = (0, 30),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "n",
                                    parent = w_infinite
                                )
        # BREAK
        w_break = DOFwidget( self.canvas, 
                                    drawers = [ ], 
                                    size = (WIDTH, 20),
                                    origin = (0, 100),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "break",
                                    parent = w_landscapemode
                                )
        w_blurlabel = DOFwidget( self.canvas,
                                    drawers = [ d_blurlabel ],
                                    size = (80, 20),
                                    origin = (0, 0),
                                    visible = True,
                                    name = "blurlabel",
                                    parent = w_break
                                )
        w_distancelabel = DOFwidget( self.canvas,
                                    drawers = [ d_distancelabel ],
                                    size = (40, 20),
                                    origin = (WIDTH-2*40, 0),
                                    visible = True,
                                    name = "distancelabels",
                                    parent = w_break
                                )
        w_unitslabel = DOFwidget( self.canvas,
                                    drawers = [ d_unitslabel ],
                                    size = (40, 20),
                                    origin = (WIDTH-40, 0),
                                    visible = True,
                                    name = "unitslabel",
                                    parent = w_break
                                )
        # MAINLANDSCAPE
        w_mainlandscape = DOFwidget( self.canvas, 
                                    drawers = [ d_beam, d_mask ], 
                                    size = (WIDTH, 500),
                                    origin = (WIDTH/2, 620),
                                    corner = (WIDTH/2, 0),
                                    vector_y = (0,-1),
                                    visible = True,
                                    name = "mainlandscape",
                                    parent = w_landscapemode
                                )

        w_blurcone = DOFwidget( self.canvas, 
                                    drawers = [ d_blurcone ], 
                                    size = (80, 500),
                                    origin = (-WIDTH/2+40, 0),
                                    corner = (-50, 0),
                                    visible = False,
                                    name = "blurcone",
                                    parent = w_mainlandscape
                                )
        w_framebar = DOFwidget( self.canvas, 
                                    drawers = [ d_slate_framebar ], 
                                    size = (40, 500),
                                    origin = ( WIDTH/2-80, 0),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "framebar",
                                    parent = w_mainlandscape
                                )
        w_distancebar = DOFwidget( self.canvas, 
                                    drawers = [ d_slate_distancebar, d_focusedrange ], 
                                    size = (40, 500),
                                    origin = ( WIDTH/2-40, 0),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "distancebar",
                                    parent = w_mainlandscape
                                )
                                    
        w_mainlines = DOFwidget( self.canvas, 
                                    drawers = [ d_hypline, d_focusline ], 
                                    visible = True,
                                    name = "mainlines",
                                    parent = w_mainlandscape
                                )
        w_dragbutton = DOFwidget( self.canvas,
                                    drawers = [ d_dragbutton ],
                                    handler = h_dragbutton, 
                                    size = (24, 24),
                                    origin = [0, 0],
                                    corner = (0, 0),
                                    vector_y = (0, -1),
                                    visible = True,
                                    name = "dragbutton",
                                    parent = w_mainlandscape
                                )

        """        #Closeup - Detail for short distances
        #   --> Replaced by widget "close"
        #   --> (DEPRECATED)
        w_closeup_slate = DOFwidget( self.canvas,
                                    drawers = [ d_slate_closeup ],
                                    size = ( WIDTH, 200 ),
                                    origin = [ 0, 280 ],
                                    corner = [0, 0],
                                    visible = False,
                                    name = "closeup_slate",
                                    parent = w_landscapemode
                                )
        w_closeup_inner = DOFwidget( self.canvas,
                                    drawers = [ d_slate_closeup_inner  ],
                                    size = ( WIDTH-24, 200-24-24 ),
                                    origin = ( 24, 24 ),
                                    corner = (0,0),
                                    visible = True,
                                    name = "closeup_inner",
                                    parent = w_closeup_slate,
                                )
        w_closeup_cone = DOFwidget( self.canvas,
                                    drawers = [ d_closeupcone, d_test, d_name ],
                                    size = ( WIDTH-24, 200-24-24 ),
                                    origin = ( 100, 300 ),
                                    corner = (-100, 300-(200-24-24)),
                                    vector_y =(0, -1),
                                    visible = True,
                                    name = "closeup_cone",
                                    parent = w_closeup_inner,
                                )
        w_closeup_quit = DOFwidget( self.canvas,
                                    drawers = [ d_quitbutton ],
                                    handler = h_quitbutton,
                                    size = ( 24, 24 ),
                                    origin = ( 0, 0 ),
                                    corner = (0,0),
                                    visible = True,
                                    name = "closeup_quit",
                                    parent = w_closeup_slate,
                                )"""

        # CLOSE --> detail for short distances  
        # Replaces Closeup
        w_close_slate = DOFwidget( self.canvas,
                                    drawers = [ d_slate_close ],
                                    size = ( WIDTH, 280 ),
                                    origin = [0, 250 ],
                                    corner = [0, 0],
                                    visible = False,
                                    name = "close_slate",
                                    parent = w_landscapemode
                                )
        w_close_quit = DOFwidget( self.canvas,
                                    drawers = [ d_quitbutton ],
                                    handler = h_quitbutton,
                                    size = ( 24, 24 ),
                                    origin = ( 0, 0 ),
                                    corner = (0,0),
                                    visible = True,
                                    name = "closeup_quit",
                                    parent = w_close_slate,
                                )
        w_close_inner0 = DOFwidget( self.canvas,
                                    drawers = [ d_slate_close_inner0 ],
                                    f_origin = lambda self: (4,self.parent.size[1]-4),
                                    f_size = lambda self: (self.parent.size[0]-4-4,self.parent.size[1]-24-4),
                                    vector_y = (0, -1),
                                    visible = True,
                                    name = "close_inner0",
                                    parent = w_close_slate,
                                )
        w_close_inner1 = DOFwidget( self.canvas,
                                    drawers = [],
                                    f_origin = lambda self: (self.parent.size[0]/2, -300),
                                    f_size = lambda self: self.parent.size,
                                    f_corner = lambda self: (-self.origin[0],-self.origin[1]),
                                    visible = True,
                                    name = "close_inner1",
                                    parent = w_close_inner0,
                                )
        w_close_cone = DOFwidget( self.canvas,
                                    drawers = [ d_close_cone ],
                                    origin = ( 0, 0 ),
                                    f_corner = lambda self: self.parent.corner,
                                    visible = True,
                                    name = "close_cone",
                                    parent = w_close_inner1,
                                )
        """w_close_cone = DOFwidget( self.canvas,
                                    drawers = [ d_test, d_name ],
                                    origin = ( 0, 0 ),
                                    f_corner = lambda parent: parent.corner ,
                                    visible = True,
                                    name = "close_cone",
                                    parent = w_close_inner1,
                                )"""
        # TODO --> 20110511 --> substitute drawers for setting coords relative to parent
        #                   for lambda functions !!!!!!!!! :-) cool!!!
        #                   and see if function can take over static params

        #CAMERA CONTROLS 
        w_cameracontrols = DOFwidget( self.canvas, 
                                    drawers = [ d_slate_cameracontrols  ], 
                                    size = (WIDTH, 140),
                                    origin = (0, 620),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "cameracontrols",
                                    parent = w_landscapemode
                                )
        w_camera = DOFwidget( self.canvas, 
                                    drawers = [ d_camera ], 
                                    size = (60, 44),
                                    origin = (WIDTH/2, 0),
                                    corner = (-26, 0),
                                    visible = True,
                                    name = "camera",
                                    parent = w_cameracontrols
                                )

        ## Input wheels discarded
        #w_wheel_x0 = DOFwidget( self.canvas, 
                                    #drawers = [ d_test, d_name],
                                    #handler = h_x0_wheel,
                                    #size = ( 200, 20),
                                    #origin = (10, 10),
                                    #corner = (0, 0),
                                    #visible = False,
                                    #name = "wheel_x0",
                                    #parent = w_cameracontrols
                                #)
        #w_wheel_F = DOFwidget( self.canvas, 
                                    #drawers = [ d_test, d_name],
                                    #handler = h_f_wheel,
                                    #size = ( 200, 20),
                                    #origin = (10, 60),
                                    #corner = (0, 0),
                                    #visible = False,
                                    #name = "wheel_F",
                                    #parent = w_cameracontrols
                                #)

        #GROUP for camera inputs
        w_camerainputs = DOFwidget( self.canvas, 
                                    drawers = [ d_frame_camerainputs ], 
                                    size = (124, 135),
                                    origin = (2, 2),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "camerainputs",
                                    parent = w_cameracontrols
                                )
        #Control f
        w_group_f = DOFwidget( self.canvas, 
                                    drawers = [ d_frame_group ],
                                    size = ( 120, 32),
                                    origin = (2, 2),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "group_f",
                                    parent = w_camerainputs
                                )
        w_display_f = DOFwidget( self.canvas, 
                                    drawers = [ d_display_f ],
                                    size = ( 30, 30),
                                    origin = (89, 1),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "display_f",
                                    parent = w_group_f
                                )
        w_label_f = DOFwidget( self.canvas, 
                                    drawers = [ d_label_f ],
                                    size = ( 32, 32),
                                    origin = (56, 0),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "label_f",
                                    parent = w_group_f
                                )
        w_buttonleft_f = DOFwidget( self.canvas, 
                                    drawers = [ d_buttonleft ],
                                    handler = h_buttonleft_f,
                                    size = ( 24, 24 ),
                                    origin = (4, 4),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "buttonleft_f",
                                    parent = w_group_f
                                )
        w_buttonright_f = DOFwidget( self.canvas, 
                                    drawers = [ d_buttonright ],
                                    handler = h_buttonright_f,
                                    size = ( 24, 24 ),
                                    origin = (28, 4),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "buttonright_f",
                                    parent = w_group_f
                                )
        #Control F
        w_group_F = DOFwidget( self.canvas, 
                                    drawers = [ d_frame_group ],
                                    size = ( 120, 32),
                                    origin = (2, 35),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "group_F",
                                    parent = w_camerainputs
                                )
        w_display_F = DOFwidget( self.canvas, 
                                    drawers = [ d_display_F ],
                                    size = ( 30, 30),
                                    origin = (89, 1),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "display_F",
                                    parent = w_group_F
                                )
        w_label_F = DOFwidget( self.canvas, 
                                    drawers = [ d_label_F ],
                                    size = ( 32, 32),
                                    origin = (56, 0),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "label_F",
                                    parent = w_group_F
                                )
        w_buttonleft_F = DOFwidget( self.canvas, 
                                    drawers = [ d_buttonleft ],
                                    handler = h_buttonleft_F,
                                    size = ( 24, 24 ),
                                    origin = (4, 4),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "buttonleft_F",
                                    parent = w_group_F
                                )
        w_buttonright_F = DOFwidget( self.canvas, 
                                    drawers = [ d_buttonright ],
                                    handler = h_buttonright_F,
                                    size = ( 24, 24 ),
                                    origin = (28, 4),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "buttonright_F",
                                    parent = w_group_F
                                )
        #Control S
        w_group_S = DOFwidget( self.canvas, 
                                    drawers = [ d_frame_group ],
                                    size = ( 120, 32),
                                    origin = (2, 68),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "group_S",
                                    parent = w_camerainputs
                                )
        w_display_S = DOFwidget( self.canvas, 
                                    drawers = [ d_display_S ],
                                    size = ( 30, 30),
                                    origin = (89, 1),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "display_S",
                                    parent = w_group_S
                                )
        w_label_S = DOFwidget( self.canvas, 
                                    drawers = [ d_label_S ],
                                    size = ( 32, 32),
                                    origin = (56, 0),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "label_S",
                                    parent = w_group_S
                                )
        w_buttonleft_S = DOFwidget( self.canvas, 
                                    drawers = [ d_buttonleft ],
                                    handler = h_buttonleft_S,
                                    size = ( 24, 24 ),
                                    origin = (4, 4),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "buttonleft_S",
                                    parent = w_group_S
                                )
        w_buttonright_S = DOFwidget( self.canvas, 
                                    drawers = [ d_buttonright ],
                                    handler = h_buttonright_S,
                                    size = ( 24, 24 ),
                                    origin = (28, 4),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "buttonright_S",
                                    parent = w_group_S
                                )
        #Control m
        w_group_m = DOFwidget( self.canvas, 
                                    drawers = [ d_frame_group ],
                                    size = ( 120, 32),
                                    origin = (2, 101),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "group_m",
                                    parent = w_camerainputs
                                )
        w_display_m = DOFwidget( self.canvas, 
                                    drawers = [ d_display_m ],
                                    size = ( 30, 30),
                                    origin = (89, 1),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "display_m",
                                    parent = w_group_m
                                )
        w_label_m = DOFwidget( self.canvas, 
                                    drawers = [ d_label_m ],
                                    size = ( 32, 32),
                                    origin = (56, 0),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "label_m",
                                    parent = w_group_m
                                )
        w_buttonleft_m = DOFwidget( self.canvas, 
                                    drawers = [ d_buttonleft ],
                                    handler = h_buttonleft_m,
                                    size = ( 24, 24 ),
                                    origin = (4, 4),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "buttonleft_m",
                                    parent = w_group_m
                                )
        w_buttonright_m = DOFwidget( self.canvas, 
                                    drawers = [ d_buttonright ],
                                    handler = h_buttonright_m,
                                    size = ( 24, 24 ),
                                    origin = (28, 4),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "buttonright_m",
                                    parent = w_group_m
                                )
        
        #Control Panel
        d_landscapebutton = LandscapeButtonDrawer( viewmodel=self.viewmodel )
        d_objectbutton = ObjectButtonDrawer( viewmodel=self.viewmodel )
        w_controlpanel = DOFwidget( self.canvas, 
                                    drawers = [ d_test, d_name ], 
                                    size = (WIDTH, 40),
                                    origin = (0, 760),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "controlpanel",
                                    parent = w_root
                                )
        w_landscapebutton = DOFwidget( self.canvas,
                                    drawers = [ d_test, d_name, d_landscapebutton ], 
                                    handler = h_landscapebutton,
                                    size = (128, 32),
                                    origin = (4, 4),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "landscapebutton",
                                    parent = w_controlpanel
                                )
        w_objectbutton = DOFwidget( self.canvas,
                                    drawers = [ d_test, d_name, d_objectbutton ], 
                                    handler = h_objectbutton,
                                    size = (128, 32),
                                    origin = (136, 4),
                                    corner = (0, 0),
                                    visible = True,
                                    name = "objectbutton",
                                    parent = w_controlpanel
                                )
                                        


        # returns main widgets in a dictionary
        widgets =   {   'root' : w_root , 
                        'close' : w_close_slate ,
                        'landscapemode' : w_landscapemode , 
                        'objectmode' : w_objectmode
                    }
        return widgets

        

#GLOBAL VARS
SIZE = WIDTH, HEIGHT = (480, 800) 
COLOR_BLUR = N.array((0,250,100))
# My test code
def main( ):
    controller = MyController( )

main( )
