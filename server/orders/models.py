from django.db import models

from django.contrib.auth.models import User
from menus.models import MenuItem

import uuid

from datetime import datetime

class Cart(models.Model):
    owner = models.OneToOneField(User, on_delete = models.CASCADE, blank = True, null = True)
    def items(self):
        return CartMenuItemQuantity.objects.filter(cart = self)

class Order(models.Model):
    uuid = models.UUIDField('uuid', default = uuid.uuid4, editable = False)
    order_time = models.DateTimeField('order time', default = datetime.now)
    placement_date = models.DateTimeField(auto_now_add = True)
    def items(self):
        return OrderMenuItemQuantity.objects.filter(order = self)

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