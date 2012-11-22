from zope.interface import Interface

class IGeolocation(Interface):
	pass

class IUserDatabase(Interface):
    pass

class IListing(Interface):
    
    def summary():
        pass
    