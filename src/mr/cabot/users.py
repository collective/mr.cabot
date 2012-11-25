import string

from zope.component import getGlobalSiteManager
from zope.interface import implements

from mr.cabot.interfaces import IUserDatabase
from mr.cabot.sebastian import logger

BAD = "AEIOUY"

def name_cmp(one, two):
    if not one or not two:
        return False
    one = one.upper().encode("ascii","replace")
    two = two.upper().encode("ascii","replace")
    one = [l for l in one if l not in BAD and l in string.uppercase]
    two = [l for l in two if l not in BAD and l in string.uppercase]
    diffs = 0
    if len(one) < 7 or len(two) < 7:
        return one == two
    for ch1, ch2 in zip(one, two):
        if ch1 != ch2:
            diffs += 1
    return diffs <= 2

class User(object):
    
    def __init__(self, name, email, location=None, location_func = None):
        self.name = name
        self.email = email
        self._location = location
        self._location_func = location_func
    
    @property
    def location(self):
        if not self._location and self._location_func:
            self._location = self._location_func()
        return self._location
    
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
        user = [u for u in self.users if name_cmp(u.name, name)][0]
        logger.debug("users: Found user %s when searching for %s" % (user.name, name))
        return user

gsm = getGlobalSiteManager()
gsm.registerUtility(Users())
