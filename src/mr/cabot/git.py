import collections
import datetime
from email.utils import parsedate_tz, parseaddr, mktime_tz
import os
import subprocess
import tempfile
import shutil

from zope.component import adapts, getGlobalSiteManager
from zope.interface import implements

from mr.cabot.interfaces import IGeolocation

def create(url):
	return GitRepo(url)

class Commit(object):
    
    def __init__(self, kwargs, package):
        self.__dict__.update(kwargs)
        self.package = package

class GitRepo(object):
    
    def __init__(self, url, location=None):
        self.url = url
        if location is None:
            self.location = self._directory = tempfile.mkdtemp()
            self._git_command("clone", self.url)
            self.package = os.listdir(self._directory)[0]
            self.location = os.path.join(self._directory, self.package)
            self.remove = True
        else:
            location = os.path.normpath(os.path.realpath(location))
            if not os.path.exists(location):
                # First time!
                self.location = os.path.split(location)[0]
                self._git_command("clone", self.url)
            self.location = location
            self.package = os.path.split(location)[-1]
            self._git_command("pull")
            self.remove = False
    
    def __del__(self):
        if self.remove:
            shutil.rmtree(self._directory)
        
    def _git_command(self, *args):
        cwd = os.getcwd()
        try:
            return subprocess.check_output(["git"] + list(args), stderr=subprocess.STDOUT, cwd=self.location)
        finally:
            os.chdir(cwd)
    
    def commits_since(self, date):
        return {commit for commit in self.commits() if commit.date > date}
    
    def commits(self):
        log = self._git_command("log")
        log = ["commit:"+commit for commit in log.split("commit") if commit]
        return set(map(self._parse_commit, log))
    
    def _parse_commit(self, message):
        lines = message.split('\n')
        data = [line.split(":",1) for line in lines if line and line[0]!=' ']
        data = {line[0].strip().lower():line[1].strip() for line in data}
        message = "\n".join(line.strip() for line in lines if line and line[0]==' ')
        data['message'] = message
        try:
            data['date'] = datetime.datetime.fromtimestamp(mktime_tz(parsedate_tz(data['date'])))
        except KeyError:
            data['date'] = datetime.datetime(1970, 1, 1)
        try:
            data['author'] = parseaddr(data['author'])
        except KeyError:
            data['author'] = ('','')
        return Commit(data, package=self.package)
    
    def get_data(self):
        now = datetime.datetime.now()
        past = now - datetime.timedelta(days=5)
        return set(self.commits_since(past))
    

class GitGeolocation(object):
	
    adapts(Commit)
    implements(IGeolocation)
    
    def __init__(self, commit):
        self.commit = commit
    
    @property
    def coords(self):
        users = getUtility(IUserDatabase)
        author = None
        try:
            author = users.get_user_by_email(self.commit.author[1])
        except:
            try:
                author = users.get_user_by_name(self.commit.author[0])
            except:
                pass
        if author is None:
            return None
        else:
            return author.location

gsm = getGlobalSiteManager()
gsm.registerAdapter(GitGeolocation)
