from mr.cabot.interfaces import IListing, IGeolocation

def html_snippet(obj):
    loc = IGeolocation(obj).coords
    if not loc:
        return
    else:
        lat, lon = loc
    content = IListing(obj).summary
    if lat > 0:
        hemi = "west"
    else:
        hemi = "east"
    return """<div class="homepage-pin homepage-pin-doc homepage-pin-%s">
	  <span class="latitude">%f</span>
	  <span class="longitude">%f</span>
	  <div class="content">%s</div>
	</div>""" % (hemi, lat, lon, content)