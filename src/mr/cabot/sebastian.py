import os
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from .models import (
    DBSession,
    Base,
    Identity,
    Activity
    )
from sqlalchemy.orm.exc import NoResultFound

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

socket.setdefaulttimeout(25)

join = None

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
        
        self.data = set()
        sources = self._get_sources_by_type("sources")
        
        for source_id, source in sources.items():
            kwargs = inspect.getargspec(source.get_data).args
            kwargs = {kwarg for kwarg in kwargs if kwarg != 'self'}
            kwargs = {kwarg:self.config.get(source_id, kwarg) for kwarg in kwargs}
            for datum in source.get_data(**kwargs):
                yield datum
    
    def generate_map(self, data):
        if not hasattr(self, 'data'):
            self.populate_user_database()
        print join(data)
    
    def _get_sources_by_type(self, type):
        source_ids = self.config.get("cabot", type).split()
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
        self.parser.add_argument('configuration', nargs=1)
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
        
        config_uri = args.configuration[0]
        setup_logging(config_uri)
        settings = get_appsettings(config_uri)
        engine = engine_from_config(settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)
        
        self.config = SafeConfigParser()
        self.config.read(os.path.join(self.buildout_dir, "mr.cabot.cfg"))        
        
        used_native = set()
        
        with transaction.manager:
            for datum in self.generate_data():
                try:
                    ident = DBSession.query(Identity).filter_by(uri=datum.identity).one()
                except NoResultFound:
                    ident = Identity(uri=datum.identity)
                    DBSession.add(ident)
                if datum.id not in used_native:
                    act = Activity(type=datum.type, native_id=datum.id, date=datum.date, identity=ident)
                    used_native.add(datum.id)
                    DBSession.add(act)
                else:
                    continue
                
        
sebastian = Sebastian()
