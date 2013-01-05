import argparse
from ConfigParser import SafeConfigParser
import datetime
import inspect
import logging
import os
from operator import attrgetter
import pickle
import pkg_resources
import socket

socket.setdefaulttimeout(3)

join = None

#from mr.cabot.html import join
#from mr.cabot.googlestaticmap import join

logger = logging.getLogger("mr.cabot")

def find_base():
    path = os.getcwd()
    while path:
        if os.path.exists(os.path.join(path, 'mr.cabot.cfg')):
            break
        old_path = path
        path = os.path.dirname(path)
        if old_path == path:
            path = None
            break
    if path is None:
        raise IOError("mr.cabot.cfg not found")
    return path

class Sebastian(object):

    def generate_data(self):
        users = self.get_user_sources()
        sources = self.get_data_sources()
        self.data = set()
        
        for source_id, source in users.items():
            kwargs = inspect.getargspec(source.get_users).args
            kwargs = {kwarg for kwarg in kwargs if kwarg != 'self'}
            kwargs = {kwarg:self.config.get(source_id, kwarg) for kwarg in kwargs}
            source.get_users(**kwargs)        

        for source_id, source in sources.items():
            kwargs = inspect.getargspec(source.get_data).args
            kwargs = {kwarg for kwarg in kwargs if kwarg != 'self'}
            kwargs = {kwarg:self.config.get(source_id, kwarg) for kwarg in kwargs}
            local_data = source.get_data(**kwargs)
            self.data |= local_data
        
        day_filter = int(self.config.get("cabot", "days", "5"))
        ago = datetime.datetime.now() - datetime.timedelta(days=day_filter)
        self.data = {datum for datum in self.data if datum.date >= ago}
        sorted_data = sorted(self.data, key=attrgetter('date'))
        
        data_directory = os.path.join(find_base(), "var", "data")
        if not os.path.exists(data_directory):
            os.mkdir(data_directory)
        today = datetime.datetime.now().date()
        base_path = os.path.join(data_directory, today.isoformat())
        with open(base_path+".pickle", "wb") as todays_source:
            todays_source.write(pickle.dumps(sorted_data))
        return sorted_data
    
    def generate_map(self, data):
        users = self.get_user_sources()
        if not hasattr(self, 'data'):
            for source_id, source in users.items():
                kwargs = inspect.getargspec(source.get_users).args
                kwargs = {kwarg for kwarg in kwargs if kwarg != 'self'}
                kwargs = {kwarg:self.config.get(source_id, kwarg) for kwarg in kwargs}
                source.get_users(**kwargs)        
        print join(data)
            

    def get_user_sources(self):        
        source_ids = self.config.get("cabot", "users").split()
        found = {}
        for source_id in source_ids:
            source_class = self.config.get(source_id, "type")
            source_class = "mr.cabot.%s" % (source_class)
            kls = __import__(source_class, globals(), locals(), ['create'], -1)
            found[source_id] = kls.create(self.config.get(source_id, 'key'))
        return found

    def get_data_sources(self):        
        source_ids = self.config.get("cabot", "sources").split()
        found = {}
        for source_id in source_ids:
            source_class = self.config.get(source_id, "type")
            source_class = "mr.cabot.%s" % (source_class)
            kls = __import__(source_class, globals(), locals(), ['create'], -1)
            found[source_id] = kls.create(self.config.get(source_id, 'key'))
        return found

    def __call__(self, **kwargs):
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(ch)
        self.parser = argparse.ArgumentParser()
        version = pkg_resources.get_distribution("mr.cabot").version
        self.parser.add_argument('-v', '--version',
                    action='version',
                    version='mr.cabot %s' % version)
        self.parser.add_argument('--pickle',
                    help="path to the file where old pickled data is stored")
        self.parser.add_argument('--output',
                    action="store", default="googlestaticmap")
        self.parser.add_argument("-N", help="No updates, don't pull any git repos, use the caches", action="store_true")
        args = self.parser.parse_args()
        
        global join
        join = __import__("mr.cabot.%s" % args.output, globals(), locals(), ['join'], -1).join
        
        try:
            self.buildout_dir = find_base()
        except IOError, e:
            self.parser.print_help()
            print
            logger.error("You are not in a path which has mr.cabot installed (%s)." % e)
            return
        
        if args.N:
            import git
            git.BLOCKED_COMMANDS.add("pull")
            git.BLOCKED_COMMANDS.add("fetch")
        
        self.config = SafeConfigParser()
        self.config.read(os.path.join(self.buildout_dir, "mr.cabot.cfg"))        
        
        if args.pickle is None:
            # Load the user and sources to set up adapters            
            data = self.generate_data()
        else:
            self.get_data_sources()
            with open(args.pickle, "rb") as picklefile:
                data = pickle.loads(picklefile.read())
        
        self.generate_map(data)

sebastian = Sebastian()
