 # -*- coding: utf-8 -*-


from unittest import TestCase

from mr.cabot.users import User, Users

class TestUserLookup(TestCase):
    
    def test_search_by_name(self):
        user = User("Joe Bloggs", "joe@example.com")
        users = Users()
        
        users.add_user(user)
        self.assertEqual(users.get_user_by_name("Joe Bloggs"), user)
    
    def test_search_by_email(self):
        user = User("Joe Bloggs", "joe@example.com")
        users = Users()
        
        users.add_user(user)
        self.assertEqual(users.get_user_by_email("joe@example.com"), user)
    
    def test_search_by_name_matches_with_missing_accents(self):
        user = User("Joe Bloggs", "joe@example.com")
        users = Users()
        
        users.add_user(user)
        self.assertEqual(users.get_user_by_name(u"Joé Bloggs"), user)
    
    def test_get_location(self):
        user = User("Joe Bloggs", "joe@example.com", location_func=lambda:((0,0),0))
        users = Users()
        
        users.add_user(user)
        self.assertEqual(users.get_user_by_name(u"Joe Bloggs").location, (0,0))

    def test_adding_user_twice_doesnt_cause_dupes(self):
        user = User("Joe Bloggs", "joe@example.com", location_func=lambda:((0,0),0))
        users = Users()
        
        users.add_user(user)
        users.add_user(User("Joe Bloggs", "joe@example.com", location_func=lambda:((90,90),0)))
        self.assertEqual(len(users.users), 1)

    def test_supplying_better_location_function_overrides(self):
        user = User("Joe Bloggs", "joe@example.com", location_func=lambda:((0,0),0))
        users = Users()
        
        users.add_user(user)
        users.add_user(User("Joe Bloggs", "joe@example.com", location_func=lambda:((90,90),1)))
        self.assertEqual(users.get_user_by_name(u"Joe Bloggs").location, (90,90))
    
