import string

from zope.component import getGlobalSiteManager
from zope.interface import implements

from mr.cabot.interfaces import IUserDatabase

BAD = "AEIOUY"

def name_cmp(one, two):
    one = one.upper().encode("ascii","replace")
    two = two.upper().encode("ascii","replace")
    one = [l for l in one if l not in BAD and l not in string.uppercase]
    two = [l for l in two if l not in BAD and l not in string.uppercase]
    diffs = 0
    for ch1, ch2 in zip(one, two):
        if ch1 != ch2:
            diffs += 1
    return diffs < 3

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
        return [u for u in self.users if name_cmp(u.name, name)][0]

gsm = getGlobalSiteManager()
gsm.registerUtility(Users())
