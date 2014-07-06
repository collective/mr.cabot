import re

import ggeocoder

from mr.cabot.sebastian import logger

LINKS = re.compile("<(.*?)>; rel=\"(.*?)\",?")

ALREADY_FOUND = set()

ORDERED_TYPES = ["country", "administrative_area_level_1", 
    "administrative_area_level_2", "administrative_area_level_3", 
    "colloquial_area", "locality", "sublocality", "neighbourhood", 
    "postal_code", "premise"]

def get_location(location):
    geocoder = ggeocoder.Geocoder()
    if not location:
        return None, None
    result = geocoder.geocode(location)[0]
    coords = result.coordinates
    types = result.data['types']
    interesting_types = [t for t in types if t in ORDERED_TYPES]
    quality = max([ORDERED_TYPES.index(t) for t in interesting_types])
    logger.debug("geocoder: Getting coordinates for %s == %s (%s)" % (location, `coords`, " ".join(interesting_types)))
    return coords, quality
