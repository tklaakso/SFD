from django.db import models
from django.contrib.auth.models import User
from common.models import Address
from geo.models import Location

import uuid

class Restaurant(models.Model):
    name = models.CharField('name', max_length = 100)
    address = models.ForeignKey(Address, on_delete = models.CASCADE, blank = True, null = True)
    location = models.ForeignKey(Location, on_delete = models.CASCADE, blank = True, null = True)
    owner = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    uuid = models.UUIDField('uuid', default = uuid.uuid4, editable = False)

    def serialize(self):
        return {'name' : self.name, 'address' : self.address.serialize(), 'location' : self.location.serialize()}