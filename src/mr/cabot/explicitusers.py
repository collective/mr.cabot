from mr.cabot.users import UserDB, User

def create(tag):
    return ExplicitUsers()

class ExplicitUsers(object):
    
    def get_data(self, users):
        users = users.strip().split("\n")
        users = [user.strip().split(" ") for user in users if user]
        for user in users:
            new_user = User(user[0], user[1])
            UserDB.add(new_user)
        return set()