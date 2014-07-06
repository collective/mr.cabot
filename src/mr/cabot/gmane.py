import datetime
from email.utils import mktime_tz
from email.utils import parsedate_tz
import email
from email.Header import decode_header
from nntplib import NNTP
import re

from mr.cabot.sebastian import logger

IP = re.compile("\d+\.\d+\.\d+\.\d+")

def create(group):
    return MailingList(group)

class MailingList(object):
    
    def __init__(self, group):
        self.group = group
    
    @property
    def gmane(self):
        for attempt in range(5):
            # You spin me right round, baby, right round.
            try:
                gmane = NNTP("news.gmane.org")
            except:
                return self.gmane
            gmane.group(self.group)
            return gmane
    
    @property
    def group_info(self):
        logger.debug("gmane: Switching to archive %s" % (self.group))
        return self.gmane.group(self.group)
    
    @property
    def latest(self):
        return int(self.group_info[3])
    
    def __getitem__(self, key):
        logger.debug("gmane: Getting article %d for archive %s" % (key, self.group))
        article = self.gmane.article(str(key))
        message = "\n".join(article[-1])
        mail = email.message_from_string(message)
        mail.date=datetime.datetime.fromtimestamp(mktime_tz(parsedate_tz(mail['date'])))
        self.add_sender(mail)
        return mail
    
    def get_data(self, messages):
        return set() # gmane is broken
        messages = int(messages)
        data = set()
        for item in range(self.latest-(messages-1), self.latest+1):
            try:
                data.add(self[item])
            except:
                pass
        return data
    
    @property
    def sender_info(self, message):
        from_ = list(email.utils.parseaddr(message.get("From")))
        
        # Remove quoted printable
        from_[0] = decode_header(from_[0])[0]
        encoding = from_[0][1]
        if encoding is None:
            encoding = "utf-8"
        from_[0] = from_[0][0].decode(encoding)
        
        users.get(from_[0])


