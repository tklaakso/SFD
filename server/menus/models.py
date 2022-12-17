from django.db import models

import uuid

from restaurants.models import Restaurant

class Menu(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete = models.CASCADE, primary_key = False, blank = True, null = True)

class MenuItem(models.Model):
    uuid = models.UUIDField('uuid', default = uuid.uuid4, editable = False)
    menu = models.ForeignKey(Menu, on_delete = models.CASCADE, blank = True, null = True)
    name = models.CharField('name', max_length = 100)
    description = models.CharField('description', max_length = 500)
    price = models.FloatField('price')