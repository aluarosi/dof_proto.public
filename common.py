# ---------------------------------------------------------------------
# OBSERVER pattern
# ---------------------------------------------------------------------
class ObserverInterface:
    """ Observer Interface """
    def update( self, caller ):
        print >> sys.stderr,str(self)+" Method update() of ObserverInterface is abstract"

class SubjectInterface:
    """Subject Interface"""
    def registerObserver( self ):
        print >> sys.stderr,str(self)+" Method registerObserver() of SubjectInterface is abstract"

    def removeObserver( self ):
        print >> sys.stderr,str(self)+" Method removeObserver() of SubjectInterface is abstract"
    
    def notifyObservers( self ):
        print >> sys.stderr,str(self)+" Method notifyObservers() of SubjectInterface is abstract"
