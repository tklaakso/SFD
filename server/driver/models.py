from django.db import models
from django.contrib.auth.models import User

from orders.models import Order
from geo.models import Route, Location

from geo.utils import make_route, get_route_estimated_time

from datetime import timedelta

class Driver(models.Model):
    active = models.BooleanField(default = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    home_location = models.ForeignKey(Location, on_delete = models.CASCADE, blank = True, null = True)

    def get_schedule(self):
        query = (self.accepted.all() | self.recommended.all()).order_by('order__order_time')
        res = []
        for order in query:
            start_time, end_time = order.get_time_bounds()
            res.append({'start_time' : start_time, 'end_time' : end_time, 'order' : order})
        return res

    def accept(self, order):
        order.driver_accepted = self
        order.driver_recommended = None
        order.driver_declined = None
        order.save()
        on_accept_order(self, order)
    
    def decline(self, order):
        schedule = self.get_schedule()
        idx = list(map(lambda x: x['order'], schedule)).index(order)
        previous_order = None
        next_order = None
        if idx - 1 >= 0:
            previous_order = schedule[idx - 1]
        if idx + 1 < len(schedule):
            next_order = schedule[idx + 1]
        if next_order:
            start = self.home_location
            if previous_order:
                start = previous_order['order'].order.location
            next_order['order'].driver_to_restaurant = make_route(start, next_order['order'].order.restaurants.first().location)
            next_order['order'].save()
        order.driver_accepted = None
        order.driver_recommended = None
        order.driver_declined = self
        order.save()
        on_decline_order(self, order)
    
    def recommend(self, order):
        order.driver_accepted = None
        order.driver_recommended = self
        order.driver_declined = None
        order.save()
    
    def serialize(self):
        return {'name' : self.user.username, 'start_location' : self.home_location.serialize()}

class DriverOrder(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE, blank = True, null = True)
    driver_to_restaurant = models.ForeignKey(Route, on_delete = models.CASCADE, blank = True, null = True)
    driver_accepted = models.ForeignKey(Driver, related_name = 'accepted', on_delete = models.CASCADE, blank = True, null = True)
    driver_declined = models.ForeignKey(Driver, related_name = 'declined', on_delete = models.CASCADE, blank = True, null = True)
    driver_recommended = models.ForeignKey(Driver, related_name = 'recommended', on_delete = models.CASCADE, blank = True, null = True)

    def get_time_bounds(self):
        end_time = self.order.order_time
        route_length = get_route_estimated_time(self.driver_to_restaurant) + get_route_estimated_time(self.order.restaurant_to_destination)
        start_time = end_time - timedelta(seconds = route_length)
        return (start_time, end_time)

    def serialize(self):
        return self.order.serialize()

from .selection import on_accept_order, on_decline_order