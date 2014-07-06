class UserDatabase(object):
    def __init__(self):
        self.users = []
    
    def add(self, user):
        self.users.append(user)
    
    def get(self, term):
        for user in self.users:
            if term in user.names:
                return user
        raise KeyError(term)


UserDB = UserDatabase()

class User(object):
    
    def __init__(self, username, display_name):
        self.username = username
        self.display_name = display_name
        self.names = [username, display_name]
    
    def __repr__(self):
        return "<User %s>" % (self.display_name)
    