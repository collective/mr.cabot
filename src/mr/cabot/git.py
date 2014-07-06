import datetime
from email.utils import parsedate_tz, parseaddr, mktime_tz
import os
import subprocess
import tempfile
import shutil

BLOCKED_COMMANDS = set()

def create(url):
    return GitRepo(url)

class Commit(object):
    type = 'commit'
    
    def __init__(self, kwargs, package, numcommits=None):
        self.__dict__.update(kwargs)
        self.package = package
        if numcommits is None:
            self._num_commits = 1
        else:
            self._num_commits = numcommits
    
    def __add__(self, other):
        if self.package != other.package:
            raise ValueError("Different packages")
        if self.author != other.author:
            raise ValueError("Different committers")
        else:
            num = self._num_commits + other._num_commits
            data = {"author":self.author, "date":min(self.date, other.date), "message":"%d commits" % (num)}
            return Commit(data, self.package, numcommits=num)
        
    
    @property
    def id(self):
        return "git:%s" % self.commit
    
    @property
    def identity(self):
        return "git:%s" % self.author[-1]
    

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
            try:
                self._git_command("pull")
            except:
                pass
            self.remove = False
    
    def __del__(self):
        if self.remove:
            shutil.rmtree(self._directory)
        
    def _git_command(self, *args):
        if args[0] in BLOCKED_COMMANDS:
            return
        cwd = os.getcwd()
        try:
            return subprocess.check_output(["git"] + list(args), stderr=subprocess.STDOUT, cwd=self.location)
        finally:
            os.chdir(cwd)
    
    def commits(self):
        try:
            log = self._git_command("log")
        except:
            return set()
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
            return None
        
        return Commit(data, package=self.package)
    
    def get_data(self):
        return set(self.commits())
    
