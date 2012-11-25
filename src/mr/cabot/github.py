import json
import os
import re
import urllib2

import ggeocoder
from zope.component import getUtility

from mr.cabot.interfaces import IUserDatabase
from mr.cabot.git import GitRepo
from mr.cabot.users import User
from mr.cabot.sebastian import logger

LINKS = re.compile("<(.*?)>; rel=\"(.*?)\",?")

class create(object):
    
    def __init__(self, org):
        self.org = org
    
    def _get_github_accounts(self, accounts, token):
        geocoder = ggeocoder.Geocoder()
        users = getUtility(IUserDatabase)
        i = 0.0
        for account in accounts:
            i+=1
            if not (i % 10):
                logger.info("github: geocoder: %2d%% complete" % ((i/len(accounts))*100.0))
            gh_api = urllib2.urlopen("https://api.github.com/users/%s?access_token=%s" % (account,token))
            user = json.loads(gh_api.read())
            try:
                logger.debug("geocoder: Getting coordinates for %s" % (user['location']))
                location = geocoder.geocode(user['location'])[0].coordinates
            except:
                location = None
            users.add_user(User(user.get('name', user['login']), user.get('email', None), location))
    
    def get_github_accounts(self):
        url = "https://api.github.com/orgs/%s/members?access_token=%s" % (self.org, self.token)
        while True:
            logger.debug("github: getting %s" % url)
            members_resp = urllib2.urlopen(url)
            members = json.loads(members_resp.read())
            all_members = set()
            for member in members:
                all_members.add(member['login'])
            links = LINKS.findall(members_resp.headers.get('Link', ''))
            links = {link[1]:link[0] for link in links}
            if 'next' in links:
                logger.debug("github: %s has too many users, requesting more" % (self.org))
                url = links['next']
            else:
                logger.info("github: Got %s users for %s" % (len(members), self.org))
                break
        return self._get_github_accounts(all_members, self.token)
    
    def get_data(self, token, checkout_directory):
        self.token = token
        self.get_github_accounts()
        
        if checkout_directory == "temp":
            checkout_directory = None
        
        url = "https://api.github.com/orgs/%s/repos?access_token=%s" % (self.org, self.token)
        while True:
            logger.debug("github: getting %s" % url)
            org_repos_resp = urllib2.urlopen(url)
            org_repos = json.loads(org_repos_resp.read())
            self.repos = {}
            for repo in org_repos:
                repo_name = repo['name']
                repo_url = repo['git_url']
                if checkout_directory:
                    location = os.path.join(checkout_directory, repo_name)
                else:
                    location = None
                logger.info("github: Getting changes for %s/%s" % (self.org, repo_name))
                self.repos[repo_name] = GitRepo(repo_url, location=location)
            links = LINKS.findall(org_repos_resp.headers.get('Link', ''))
            links = {link[1]:link[0] for link in links}
            if 'next' in links:
                logger.debug("github: %s has too many repos, requesting more" % (self.org))
                url = links['next']
            else:
                logger.info("github: Got all repos for %s" % (self.org))
                break
        data = set()
        for repo in self.repos.values():
            data |= repo.get_data()
        return data
    
