import datetime
import urllib
import os

from mr.cabot.interfaces import IListing, IGeolocation
import sebastian

colors = {"commit": "green", "mailing-list": "blue", "answer": "yellow"}

def join(objs):
    markers = ""
    unique_locations = set()
    for obj in objs:
        loc = IGeolocation(obj).coords
        if loc not in unique_locations:
            unique_locations.add(loc)
            markers += "&markers=%s" % static_map_marker(obj)
    image_location = "http://maps.googleapis.com/maps/api/staticmap?size=600x300&maptype=terrain%s&sensor=false&center=tripoli" % (markers)
    try:
        image = urllib.urlopen(image_location).read()
    except:
        pass
    else:
        image_directory = os.path.join(sebastian.find_base(), "var", "staticmaps")
        if not os.path.exists(image_directory):
            os.mkdir(image_directory)
        today = datetime.datetime.now().date()
        base_path = os.path.join(image_directory, today.isoformat())
        with open(base_path+".png", "wb") as todays_image:
            todays_image.write(image)
    return image_location
    

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