import calendar
import datetime
import json
import gzip
from StringIO import StringIO
import urllib2

from mr.cabot.sebastian import logger

BASE = "https://api.stackexchange.com/2.1/questions?site=stackoverflow&filter=!9hnGssUZw"

def create(tag):
    return StackOverflow([tag])

class Question(object):
    
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)
        self.answers = set()
        if 'answers' not in kwargs:
            kwargs['answers'] = []
        for answer in kwargs['answers']:
            self.answers.add(Answer(answer, title=self.title))

class Answer(object):
    
    def __init__(self, kwargs, title):
        self.__dict__.update(kwargs)
        self.date = datetime.datetime.fromtimestamp(self.creation_date)
        self.title = title

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
        logger.debug("stackoverflow: getting %s" % url)
        resp = urllib2.urlopen(url).read()
        resp = gzip.GzipFile(fileobj=StringIO(resp)).read()
        questions = json.loads(resp)['items']
        logger.info("stackoverflow: Getting questions for tags: %s" % (",".join(self.tags)))
        questions = map(Question, questions)
        return questions
    
    def get_data(self, days):
        now = datetime.datetime.now()
        days = int(days)
        past = now - datetime.timedelta(days=days)
        questions = set(self.get_questions_since(past))
        answers = set()
        for question in questions:
            answers |= question.answers
        return answers


