import datetime
from email.utils import mktime_tz
from email.utils import parsedate_tz
import email
from email.Header import decode_header
from email.message import Message
import json
from nntplib import NNTP
import re
import urllib2

from zope.component import adapts
from zope.component import getGlobalSiteManager, getUtility
from zope.interface import implements

from mr.cabot.interfaces import IGeolocation, IUserDatabase, IListing
from mr.cabot.sebastian import logger
from mr.cabot.users import User

IP = re.compile("\d+\.\d+\.\d+\.\d+")

def create(group):
	return MailingList(group)

class MailingList(object):
    
    def __init__(self, group):
        self.group = group
    
    @property
    def gmane(self):
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
        messages = int(messages)
        data = set()
        for item in range(self.latest-(messages-1), self.latest+1):
            try:
                data.add(self[item])
            except:
                pass
        return data
    
    def add_sender(self, message):
        def email_location():
            recieved = message.get_all('Original-Received')
            ips = [IP.findall(h) for h in recieved]
            ips = [ip[0] for ip in ips if ip and not ip[0].startswith("10.") and not ip[0].startswith("192.168")]
            likely = ips[-1]
            try:
                logger.info("geocoder: Getting location for %s" % (likely))
                url = "http://freegeoip.net/json/%s"%likely
                logger.debug("geocoder: Fetching %s" % (url))
                loc = json.loads(urllib2.urlopen(url).read())
                ll = float(loc['latitude']), float(loc['longitude'])
                if any(ll):
                    return ll, 0
            except:
                pass
        users = getUtility(IUserDatabase)
        from_ = list(email.utils.parseaddr(message.get("From")))
        
        # Remove quoted printable
        from_[0] = decode_header(from_[0])[0]
        encoding = from_[0][1]
        if encoding is None:
            encoding = "utf-8"
        from_[0] = from_[0][0].decode(encoding)
        
        users.add_user(User(from_[0], from_[1], location_func=email_location))


class GmaneGeolocation(object):
	
    adapts(Message)
    implements(IGeolocation)
    
    def __init__(self, email):
        self.email = email
    
    @property
    def coords(self):
        from_ = list(email.utils.parseaddr(self.email.get("From")))
        
        # Remove quoted printable
        from_[0] = decode_header(from_[0])[0]
        encoding = from_[0][1]
        if encoding is None:
            encoding = "utf-8"
        from_[0] = from_[0][0].decode(encoding)
        
        self.location = None
        try:
            self.user = getUtility(IUserDatabase).get_user_by_email(from_[1])
            self.location = user.location
        except:
            pass
        try:
            self.user = getUtility(IUserDatabase).get_user_by_email(from_[0])
            self.location = user.location
        except:
            pass
        
        return self.location
class GmaneListing(object):
	
    __name__ = "mailing-list"
    
    adapts(Message)
    implements(IListing)
    
    def __init__(self, email):
        self.email = email

    @property
    def summary(self):
        author = email.utils.parseaddr(self.email.get("From"))[0]
        subject = self.email.get("Subject")
        date = self.email.date
        return "%s sent the email <br />'%s' <br />at %s" % (author, subject, date.isoformat())

gsm = getGlobalSiteManager()
gsm.registerAdapter(GmaneGeolocation)
gsm.registerAdapter(GmaneListing)