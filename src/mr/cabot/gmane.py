import email
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

IP = re.compile("\d+\.\d+\.\d+\.\d+")

def create(group):
	return MailingList(group)

class MailingList(object):
    
    def __init__(self, group):
        self.group = group
    
    @property
    def gmane(self):
        gmane = NNTP("news.gmane.org")
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
        return email.message_from_string(message)
    
    def get_data(self, messages):
        messages = int(messages)
        return {self[item] for item in range(self.latest-(messages-1), self.latest+1)}


class GmaneGeolocation(object):
	
    adapts(Message)
    implements(IGeolocation)
    
    def __init__(self, email):
        self.email = email
    
    @property
    def coords(self):
        from_ = email.utils.parseaddr(self.email.get("From"))
        try:
            return getUtility(IUserDatabase).get_user_by_email(from_[1]).coords
        except:
            pass
        try:
            return getUtility(IUserDatabase).get_user_by_name(from_[0]).coords
        except:
            pass

        recieved = self.email.get_all('Original-Received')
        ips = [IP.findall(h) for h in recieved]
        ips = [ip[0] for ip in ips if ip and not ip[0].startswith("10.")]
        likely = ips[-1]
        try:
            loc = json.loads(urllib2.urlopen("http://freegeoip.net/json/%s"%likely).read())
            ll = float(loc['latitude']), float(loc['longitude'])
            if any(ll):
                return ll
        except:
            return None

class GmaneListing(object):
	
    adapts(Message)
    implements(IListing)
    
    def __init__(self, email):
        self.email = email

    @property
    def summary(self):
        author = email.utils.parseaddr(self.email.get("From"))[0]
        subject = self.email.get("Subject")
        date = self.email.get("Date")
        return "%s sent the email '%s' at %s" % (author, subject, date)

gsm = getGlobalSiteManager()
gsm.registerAdapter(GmaneGeolocation)
gsm.registerAdapter(GmaneListing)