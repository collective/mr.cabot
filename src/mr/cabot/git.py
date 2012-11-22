import os
import tempfile
import shutil

class GitRepo(object):
    
    def __init__(self, url):
        self.url = url
        self.directory = tempfile.mkdirtemp()
        
    def _git_command(self, *args):
        cwd = os.getcwd()
        try:
            return subprocess.check_output(["git"] + list(args))
        finally:
            os.chdir(cwd)
    
    def commits_since(self, date):
        import pdb; pdb.set_trace()
        return None
        