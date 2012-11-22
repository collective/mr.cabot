import collections
import datetime
from email.utils import parsedate_tz, parseaddr, mktime_tz
import os
import subprocess
import tempfile
import shutil

class GitRepo(object):
    
    def __init__(self, url):
        self.url = url
        self.location = self._directory = tempfile.mkdtemp()
        self._git_command("clone", self.url)
        self.package = os.listdir(self._directory)[0]
        self.location = os.path.join(self._directory, self.package)
    
    def __del__(self):
        shutil.rmtree(self._directory)
        
    def _git_command(self, *args):
        cwd = os.getcwd()
        try:
            return subprocess.check_output(["git"] + list(args), cwd=self.location)
        finally:
            os.chdir(cwd)
    
    def commits_since(self, date):
        return {commit for commit in self.commits() if commit['date'] > date}
    
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
        return collections.frozendict(data)

def repo_objects(repos):
    return {i[0]:GitRepo(i[1]) for i in repos.items()}
