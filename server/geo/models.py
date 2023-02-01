from django.db import models
from django.contrib.auth.models import User

from common.models import Address

class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def serialize(self):
        return {'latitude' : self.latitude, 'longitude' : self.longitude}

class Route(models.Model):
    start_location = models.ForeignKey(Location, on_delete = models.CASCADE, blank = True, null = True, related_name = 'route_start_set')
    end_location = models.ForeignKey(Location, on_delete = models.CASCADE, blank = True, null = True, related_name = 'route_end_set')

class RouteLocation(models.Model):
    route = models.ForeignKey(Route, on_delete = models.CASCADE, blank = True, null = True)
    index = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    address = models.ForeignKey(Address, on_delete = models.CASCADE, blank = True, null = True)
    location = models.ForeignKey(Location, on_delete = models.CASCADE, blank = True, null = True)
