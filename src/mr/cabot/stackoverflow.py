import datetime
import json
import gzip
from StringIO import StringIO
import urllib2

from mr.cabot.sebastian import logger

BASE = "https://api.stackexchange.com/2.2/search?pagesize=100&order=desc&sort=activity&tagged=%s&site=stackoverflow"

def create(tag):
    return StackOverflow([tag])

class Question(object):
    type = 'question'
    
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)
        self.answers = set()
        if 'answers' not in kwargs:
            kwargs['answers'] = []
        for answer in kwargs['answers']:
            self.answers.add(Answer(answer, title=self.title))

    @property
    def date(self):
        date = self.data['updated_at']
        date_components = map(int, date.split("T")[0].split("-"))
        date = datetime.date(*date_components)
        return datetime.datetime.combine(date, datetime.time(0,0))
    
    @property
    def id(self):
        return "so:%s" % self.question_id
    
    @property
    def identity(self):
        return "so:%s" % self.owner['user_id']
    
class Answer(object):
    type = 'answer'
    
    def __init__(self, kwargs, title):
        self.__dict__.update(kwargs)
        self.date = datetime.datetime.fromtimestamp(self.creation_date)
        self.title = title

    @property
    def id(self):
        return "so:%d" % self.answer_id
    
    @property
    def identity(self):
        return "so:%s" % self.owner['user_id']

class StackOverflow(object):
    
    def __init__(self, tags):
        self.tags = tags
    
    def get_data(self):
        page = 1
        while True:
            url = BASE % ";".join(self.tags)
            url += "&page=%d" % (page)
            page += 1
            
            logger.debug("stackoverflow: getting %s" % url)
            resp = urllib2.urlopen(url).read()
            resp = gzip.GzipFile(fileobj=StringIO(resp)).read()
            response = json.loads(resp)
            questions = response['items']
            logger.info("stackoverflow: Getting questions for tags: %s" % (",".join(self.tags)))
            for question in questions:
                question = Question(question)
                if question.owner['user_type'] == 'registered' and hasattr(question, 'data'):
                    yield question
                for answer in question.answers:
                    if answer.owner['user_type'] == 'registered' and hasattr(answer, 'data'):
                        yield answer
            if not response['has_more']:
                break
    
  

