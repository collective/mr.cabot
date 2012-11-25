import json
import os
import urllib2

import ggeocoder
from zope.component import getUtility

from mr.cabot.interfaces import IUserDatabase
from mr.cabot.git import GitRepo
from mr.cabot.users import User

class create(object):
    
    def __init__(self, org):
        self.org = org
    
    def _get_github_accounts(self, accounts, token):
        geocoder = ggeocoder.Geocoder()
        users = getUtility(IUserDatabase)
        i = 0.0
        for account in accounts:
            i+=1
            print "%2d%% complete" % ((i/len(accounts))*100.0)
            gh_api = urllib2.urlopen("https://api.github.com/users/%s?access_token=%s" % (account,token))
            user = json.loads(gh_api.read())
            try:
                location = geocoder.geocode(user['location'])[0].coordinates
            except:
                location = None
            users.add_user(User(user.get('name', user['login']), user.get('email', None), location))
    
    def get_data(self, token, checkout_directory):
        self.token = token
        if checkout_directory == "temp":
            checkout_directory = None
        org_repos = json.loads(urllib2.urlopen("https://api.github.com/orgs/%s/repos?access_token=%s" % (self.org, self.token)).read())
        self.repos = {}
        for repo in org_repos:
            repo_name = repo['name']
            repo_url = repo['git_url']
            if checkout_directory:
                location = os.path.join(checkout_directory, repo_name)
            else:
                location = None
            self.repos[repo_name] = GitRepo(repo_url, location=location)
        data = set()
        for repo in self.repos.values():
            data |= repo.get_data()
        return data
    
