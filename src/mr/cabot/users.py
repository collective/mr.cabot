from zope.component import getGlobalSiteManager

from zope.interface import implements

from mr.cabot.interfaces import IUserDatabase

class User(object):
    
    def __init__(self, name, email, location=None):
        self.name = name
        self.email = email
        self.location = location
    
    def __cmp__(self, other):
        return cmp((self.name, self.email), (other.name, other.email))
    
    def __hash__(self):
        return hash(self.name) + hash(self.email)

class Users(object):

    implements(IUserDatabase)
	
    def __init__(self):
        self.users = set()
    
    def add_user(self, user):
        self.users.add(user)
    
    def get_user_by_email(self, email):
        return [u for u in self.users if u.email == email][0]

    def get_user_by_name(self, name):
        return [u for u in self.users if u.name == name][0]

gsm = getGlobalSiteManager()
gsm.registerUtility(Users())
