import urllib

from mr.cabot.interfaces import IListing, IGeolocation

colors = {"commit": "green", "mailing-list": "blue", "answer": "yellow"}

def join(objs):
    markers = ""
    unique_locations = set()
    for obj in objs:
        loc = IGeolocation(obj).coords
        if loc not in unique_locations:
            unique_locations.add(loc)
            markers += "&markers=%s" % static_map_marker(obj)
    return "https://maps.googleapis.com/maps/api/staticmap?size=600x300&maptype=terrain%s&sensor=false&center=tripoli" % (markers)

def static_map_marker(obj):
    loc = IGeolocation(obj).coords
    if not loc:
        return ''
    else:
        lat, lon = loc
    listing = IListing(obj)
    listing_type = listing.__name__
    colour = colors[listing_type]
    return urllib.quote('color:%s|size:tiny|label:%s|%f,%f' % (colour, listing_type[0].upper(), lat, lon))