from django.db import models

import uuid

from restaurants.models import Restaurant

from decimal import Decimal

class Menu(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete = models.CASCADE, primary_key = False, blank = True, null = True)

class MenuItem(models.Model):
    uuid = models.UUIDField('uuid', default = uuid.uuid4, editable = False)
    menu = models.ForeignKey(Menu, on_delete = models.CASCADE, blank = True, null = True)
    name = models.CharField('name', max_length = 100)
    description = models.CharField('description', max_length = 500)
    price = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))