import datetime
import json
import os
import re
import urllib2

from mr.cabot.git import GitRepo
from mr.cabot.sebastian import logger

LINKS = re.compile("<(.*?)>; rel=\"(.*?)\",?")

ALREADY_FOUND = set()


class create(object):
    
    def __init__(self, org):
        self.org = org
    
    def get_data(self, token, checkout_directory):
        self.token = token
        
        if checkout_directory == "temp":
            checkout_directory = None
        
        five_days_ago = (datetime.datetime.now() - datetime.timedelta(days=5)).date().isoformat()
        url = "https://api.github.com/orgs/%s/issues?access_token=%s&filter=all&since=%s" % (self.org, self.token, five_days_ago)
        while True:
            logger.debug("github: getting %s" % url)
            issues_resp = urllib2.urlopen(url)
            issues = json.loads(issues_resp.read())
            for issue in issues:
                yield Issue(issue)
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
                for datum in self.repos[repo_name].get_data():
                    if datum:
                        yield datum
            links = LINKS.findall(org_repos_resp.headers.get('Link', ''))
            links = {link[1]:link[0] for link in links}
            if 'next' in links:
                logger.debug("github: %s has too many repos, requesting more" % (self.org))
                url = links['next']
            else:
                logger.info("github: Got all repos for %s" % (self.org))
                break
        logger.debug("github: Got data for %d repos in %s" % (len(self.repos), self.org))

class Issue(object):
    __name__ = "issue"
    type = 'issue'
    
    def __init__(self, data):
        self.data = data
    
    @property
    def date(self):
        date = self.data['updated_at']
        date_components = map(int, date.split("T")[0].split("-"))
        date = datetime.date(*date_components)
        return datetime.datetime.combine(date, datetime.time(0,0))
    
    @property
    def id(self):
        return "github-issue:%s" % self.data['id']
    
    @property
    def identity(self):
        return "github:%s" % self.data['user']['login']
    
    
