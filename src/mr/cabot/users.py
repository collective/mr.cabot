import string

from zope.component import getGlobalSiteManager
from zope.interface import implements

from mr.cabot.interfaces import IUserDatabase
from mr.cabot.sebastian import logger

class User(object):
    
    def __init__(self, username, display_name, default_location):
        self.id = username
        if not display_name:
            display_name = username
        self.display_name = display_name
        self.default_location = default_location
        self.linked = {}
    
    def __repr__(self):
        return "<User %s>" % (self.display_name)
    
class Users(set, object):
    implements(IUserDatabase)

gsm = getGlobalSiteManager()
gsm.registerUtility(Users())
