import datetime
import urllib
import os

import simplekml

from mr.cabot.interfaces import IListing, IGeolocation
import sebastian

colors = {"commit": "ff00ff00", "mailing-list": "ffff0000", "answer": "ff00ffff"}

def join(objs):
    kml = simplekml.Kml()
    
    unique_locations = set()
    for obj in objs:
        loc = IGeolocation(obj).coords
        if loc not in unique_locations:
            unique_locations.add(loc)
            add_point(kml, obj)
    return kml.kml()
    

def add_point(kml, obj):
    loc = IGeolocation(obj).coords
    if not loc:
        return ''
    else:
        lat, lon = loc
    listing = IListing(obj)
    listing_type = listing.__name__
    summary = listing.summary
    if isinstance(summary, str):
        summary = listing.summary.decode("utf-8", "ignore")
    summary = summary.encode("ascii","xmlcharrefreplace")
    point = kml.newpoint(name=listing.__name__, description=summary, coords=[(lon, lat)])
    point.style.iconstyle.color = colors[listing_type]
    point.style.iconstyle.scale = 1
    