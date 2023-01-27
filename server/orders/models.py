from django.db import models

from django.contrib.auth.models import User
from menus.models import MenuItem
from common.models import Address
from restaurants.models import Restaurant
from geo.models import Location

import uuid

from datetime import datetime

from decimal import Decimal

class Cart(models.Model):
    owner = models.OneToOneField(User, on_delete = models.CASCADE, blank = True, null = True)

    def items(self):
        return CartMenuItemQuantity.objects.filter(cart = self)

class Order(models.Model):
    active = models.BooleanField(default = True)
    owner = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    uuid = models.UUIDField('uuid', default = uuid.uuid4, editable = False)
    restaurants = models.ManyToManyField(Restaurant)
    price = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
    order_time = models.DateTimeField('order time', default = datetime.now)
    address = models.ForeignKey(Address, on_delete = models.CASCADE, blank = True, null = True)
    location = models.ForeignKey(Location, on_delete = models.CASCADE, blank = True, null = True)
    placement_date = models.DateTimeField(auto_now_add = True)

    def items(self):
        return OrderMenuItemQuantity.objects.filter(order = self)
    
    def serialize(self):
        return {
            'uuid' : self.uuid,
            'order_time' : self.order_time,
            'address' : self.address.serialize(),
            'location' : self.location.serialize(),
            'restaurants' : [restaurant.serialize() for restaurant in self.restaurants.all()],
        }

class CartMenuItemQuantity(models.Model):
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE, blank = True, null = True)
    uuid = models.UUIDField('uuid', default = uuid.uuid4, editable = False)
    item = models.ForeignKey(MenuItem, on_delete = models.CASCADE, blank = True, null = True)
    quantity = models.IntegerField('quantity')

class OrderMenuItemQuantity(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE, blank = True, null = True)
    uuid = models.UUIDField('uuid', default = uuid.uuid4, editable = False)
    item = models.ForeignKey(MenuItem, on_delete = models.CASCADE, blank = True, null = True)
    quantity = models.IntegerField('quantity')