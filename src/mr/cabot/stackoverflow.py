from mr.cabot.interfaces import IGeolocation
from zope.component import getGlobalSiteManager, adapts
from zope.interface import implements
import calendar
import datetime
import json
import gzip
from StringIO import StringIO
import urllib2

import ggeocoder

BASE = "https://api.stackexchange.com/2.1/questions?site=stackoverflow&filter=!9hnGssUZw"


class Question(object):
    
    def __init__(self, kwargs):
        if 'answers' not in kwargs:
            kwargs['answers'] = []
        kwargs['answers'] = map(Answer, kwargs['answers'])
        self.__dict__.update(kwargs)

class Answer(object):
    
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)

class StackOverflow(object):
    
    def __init__(self, tags):
        self.tags = tags
    
    def get_questions_since(self, date, method='activity'):
        ts_from = calendar.timegm(date.utctimetuple())
        ts_to = calendar.timegm(datetime.datetime.now().utctimetuple())
        url = BASE
        url += "&sort=%s" % (method)
        url += "&min=%d&max=%d" % (ts_from, ts_to)
        url += "&tagged=%s" % (";".join(self.tags))
        resp = urllib2.urlopen(url).read()
        resp = gzip.GzipFile(fileobj=StringIO(resp)).read()
        questions = json.loads(resp)['items']
        questions = map(Question, questions)
        return questions


class SOGeolocation(object):
	
    adapts(Answer)
    implements(IGeolocation)
    
    def __init__(self, answer):
        self.answer = answer
    
    @property
    def coords(self):
        geocoder = ggeocoder.Geocoder()
        user = self.answer.owner['user_id']
        url = "https://api.stackexchange.com/2.1/users/%s?site=stackoverflow"
        url %= (user)
        resp = urllib2.urlopen(url).read()
        resp = gzip.GzipFile(fileobj=StringIO(resp)).read()
        try:
            user = json.loads(resp)['items'][0]
        except:
            return None
        try:
            location = geocoder.geocode(user['location'])[0].coordinates
        except:
            location = None
        return location

class SOListing(object):
	
    adapts(Message)
    implements(IListing)
    
    def __init__(self, answer):
        self.answer = answer

    @property
    def summary(self):
        author = email.utils.parseaddr(self.email.get("From"))[0]
        subject = self.email.get("Subject")
        date = self.email.get("Date")
        return "%s sent the email '%s' at %s" % (author, subject, date)

gsm = getGlobalSiteManager()
gsm.registerAdapter(GmaneGeolocation)
gsm.registerAdapter(GmaneListing)

gsm = getGlobalSiteManager()
gsm.registerAdapter(SOGeolocation)