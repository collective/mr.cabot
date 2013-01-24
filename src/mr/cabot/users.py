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

def location_match_quality(geocode_result):
    import pdb; pdb.set_trace()

class User(object):
    
    def __init__(self, name, email, location=None, location_func=None):
        self.name = name
        self.email = email
        self._location = location
        self._location_func = [location_func]
    
    def __repr__(self):
        prefix = ""
        if self._location is not None:
            prefix = "Geolocated"
        return "<%sUser %s at %s>" % (prefix, self.name, self.email)
    
    def _get_location(self):
        if not self._location:
            while self._location_func:
                lf = self._location_func.pop()
                location = lf()
                if location and location[1] > self.location_quality:
                    logger.debug("users: Location %s found to replace %s for %s" % (location, self._location, self))
                    self._location = location
        return self._location
    
    @property
    def location(self):
        location = self._get_location()
        if location:
            return location[0]
    
    @property
    def location_quality(self):
        if self._location is None:
            return None
        return self._get_location()[1]
    
    def __cmp__(self, other):
        return cmp(self.name, other.name)
    
    def __hash__(self):
        return hash(self.name) + hash(self.email)

class Users(object):

    implements(IUserDatabase)
	
    def __init__(self):
        self.users = set()
    
    def add_user(self, user):
        try:
            existing = self.get_user_by_name(user.name)
        except IndexError:
            self.users.add(user)
        else:
            # Merge in new location functions
            existing._location_func += user._location_func
            if existing.email is None and user.email:
                existing.email = user.email            
    
    def get_user_by_email(self, email):
        raise NotImplementedError
        return [u for u in self.users if u.email == email][0]

    def get_user_by_name(self, name):
        user = [u for u in self.users if name_cmp(u.name, name)][0]
        logger.debug("users: Found user %s when searching for %s" % (user.name, name))
        return user

gsm = getGlobalSiteManager()
gsm.registerUtility(Users())
