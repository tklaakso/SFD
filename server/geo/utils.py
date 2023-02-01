from .models import Route, RouteLocation

from geographic.interface import GeographicInterface
from geographic.utils import get_route_estimated_time as route_time, get_route_distance as route_distance

def location_to_latlng(loc):
    return (loc.latitude, loc.longitude)

def geocode(addr):
    with GeographicInterface() as inter:
        latlng = inter.geocode(str(addr))
    return latlng

def make_route(start, end):
    with GeographicInterface() as inter:
        route = inter.route(location_to_latlng(start), location_to_latlng(end))
    res = Route(start_location = start, end_location = end)
    res.save()
    for i, (lat, lng) in enumerate(route):
        RouteLocation(index = i, latitude = lat, longitude = lng, route = res).save()
    res.save()
    return res

def to_latlng_route(route):
    query = RouteLocation.objects.filter(route = route).order_by('index')
    res = []
    for loc in query:
        res.append((loc.latitude, loc.longitude))
    return res

def get_route_estimated_time(route):
    latlng_route = to_latlng_route(route)
    time = route_time(latlng_route, 60)
    return time

def get_route_distance(route):
    latlng_route = to_latlng_route(route)
    dist = route_distance(latlng_route)
    return dist
