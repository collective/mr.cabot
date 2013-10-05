import datetime
import json
import os
import re
import urllib2

import ggeocoder
from zope.component import getUtility
from zope.interface import implements

from mr.cabot.interfaces import IGeolocation, IListing
from mr.cabot.interfaces import IUserDatabase
from mr.cabot.git import GitRepo
from mr.cabot.users import User
from mr.cabot.sebastian import logger

LINKS = re.compile("<(.*?)>; rel=\"(.*?)\",?")

ALREADY_FOUND = set()

ORDERED_TYPES = ["country", "administrative_area_level_1", 
    "administrative_area_level_2", "administrative_area_level_3", 
    "colloquial_area", "locality", "sublocality", "neighbourhood", 
    "postal_code", "premise"]

def lazy_location(user):
    geocoder = ggeocoder.Geocoder()
    def get_location():
        if not user.get("location", None):
            return None
        try:
            result = geocoder.geocode(user['location'])[0]
            coords = result.coordinates
            types = result.data['types']
            interesting_types = [t for t in types if t in ORDERED_TYPES]
            quality = max([ORDERED_TYPES.index(t) for t in interesting_types])
            if not quality:
                quality = 1 # We trust github more than geoip
            logger.debug("geocoder: Getting coordinates for user %s at %s == %s (%s)" % (user['login'], user['location'], `coords`, " ".join(interesting_types)))
            return coords, quality
        except:
            return None, None
    return get_location


class create(object):
    
    def __init__(self, org):
        self.org = org
    
    def _get_github_accounts(self, accounts, token):
        users = getUtility(IUserDatabase)
        i = 0.0
        for account in accounts:
            i+=1
            if account in ALREADY_FOUND:
                continue
            url = "https://api.github.com/users/%s?access_token=%s" % (account,token)
            logger.debug("github: getting %s" % url)
            gh_api = urllib2.urlopen(url)
            user = json.loads(gh_api.read())
            ALREADY_FOUND.add(account)
            users.add_user(User(user.get('name', user['login']), user.get('email', None), username=user['login'], location_func=lazy_location(user)))
    
    def get_users(self, token):
        url = "https://api.github.com/orgs/%s/members?access_token=%s" % (self.org, token)
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
        return self._get_github_accounts(all_members, token)
    
    def get_data(self, token, checkout_directory):
        self.token = token
        data = set()
        
        if checkout_directory == "temp":
            checkout_directory = None
        
        five_days_ago = (datetime.datetime.now() - datetime.timedelta(days=5)).date().isoformat()
        url = "https://api.github.com/orgs/%s/issues?access_token=%s&filter=all&since=%s" % (self.org, self.token, five_days_ago)
        while True:
            logger.debug("github: getting %s" % url)
            issues_resp = urllib2.urlopen(url)
            issues = json.loads(issues_resp.read())
            for issue in issues:
                data.add(Issue(issue))
            links = LINKS.findall(issues_resp.headers.get('Link', ''))
            links = {link[1]:link[0] for link in links}
            if 'next' in links:
                logger.debug("github: %s has too many issues, requesting more" % (self.org))
                url = links['next']
            else:
                logger.info("github: Got all issues for %s" % (self.org))
                break

        url = "https://api.github.com/orgs/%s/repos?access_token=%s&type=public" % (self.org, self.token)
        self.repos = {}
        while True:
            logger.debug("github: getting %s" % url)
            org_repos_resp = urllib2.urlopen(url)
            org_repos = json.loads(org_repos_resp.read())
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
        logger.debug("github: Got data for %d repos in %s" % (len(self.repos), self.org))
        for repo in self.repos.values():
            data |= repo.get_data()
        return data

class Issue(object):
    implements(IGeolocation, IListing)
    
    __name__ = "issue"
    
    def __init__(self, data):
        self.data = data
    
    @property
    def date(self):
        date = self.data['updated_at']
        date_components = map(int, date.split("T")[0].split("-"))
        date = datetime.date(*date_components)
        return datetime.datetime.combine(date, datetime.time(0,0))
        
    
    @property
    def coords(self):
        users = getUtility(IUserDatabase)
        try:
            self.user = users.get_user_by_name(self.data['user']['login'])
            return self.user.location
        except:
            return None
    
    @property
    def summary(self):
        return self.data['title']
