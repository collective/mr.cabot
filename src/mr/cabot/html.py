from mr.cabot.interfaces import IListing, IGeolocation

def join(objs):
    objs = [html_snippet(obj) for obj in objs]
    return "\n\n".join(objs)

def html_snippet(obj):
    loc = IGeolocation(obj).coords
    if not loc:
        return ''
    else:
        lat, lon = loc
    listing = IListing(obj)
    listing_type = listing.__name__
    content = listing.summary
    if lon < 0:
        hemi = "west"
    else:
        hemi = "east"
    return """<div class="homepage-pin homepage-pin-%s homepage-pin-%s">
	  <span class="latitude">%f</span>
	  <span class="longitude">%f</span>
	  <div class="content">%s</div>
	</div>""" % (listing_type, hemi, lat, lon, content)