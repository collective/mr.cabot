import string

class User(object):
    
    def __init__(self, username, display_name):
        self.username = username
        self.display_name = display_name
    
    def __repr__(self):
        return "<User %s>" % (self.display_name)
    