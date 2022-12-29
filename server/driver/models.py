from django.db import models
from django.contrib.auth.models import User

from orders.models import Order

class Driver(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    accepted = models.ManyToManyField(Order, related_name = 'driver_accepted')
    declined = models.ManyToManyField(Order, related_name = 'driver_declined')
    recommended = models.ManyToManyField(Order, related_name = 'driver_recommended')

    def accept(self, order):
        order.driver_accepted.clear()
        order.driver_recommended.clear()
        self.accepted.add(order)
        on_accept_order(self, order)
    
    def decline(self, order):
        self.recommended.remove(order)
        self.accepted.remove(order)
        self.declined.add(order)
        on_decline_order(self, order)
    
    def recommend(self, order):
        order.driver_accepted.clear()
        self.recommended.add(order)

from .selection import on_accept_order, on_decline_order