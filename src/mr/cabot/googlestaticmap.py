import datetime
import urllib
import os
import itertools

from mr.cabot.interfaces import IListing, IGeolocation
import sebastian

colors = {"commit": "green", "mailing-list": "blue", "answer": "yellow"}

def join(objs):
    markers = ""
    unique_locations = set()
    activities = []
    for obj in objs:
        loc = IGeolocation(obj).coords
        if loc not in unique_locations:
            unique_locations.add(loc)
            activities.append(obj)
    
    name=lambda x:x.__class__.__name__
    by_type = itertools.groupby(sorted(activities, key=name),key=name)
    for t,objs in by_type:
        m = static_map_marker(objs)
        if m is not None:
            markers += "&markers=%s" % m
    
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
    

def static_map_marker(objs):
    locations = []
    for obj in objs:
        loc = IGeolocation(obj).coords
        if not loc:
            continue
        else:
            locations.append(loc)
    if locations:
        listing = IListing(obj)
        listing_type = listing.__name__
        colour = colors[listing_type]
        locations = "|".join("%.1f,%.1f" % (l[0],l[1]) for l in locations)
        return urllib.quote('color:%s|size:tiny|%s' % (colour, locations))