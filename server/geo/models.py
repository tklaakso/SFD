from django.db import models
from django.contrib.auth.models import User

from common.models import Address

class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def serialize(self):
        return {'latitude' : self.latitude, 'longitude' : self.longitude}

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    address = models.ForeignKey(Address, on_delete = models.CASCADE, blank = True, null = True)
    location = models.ForeignKey(Location, on_delete = models.CASCADE, blank = True, null = True)
