from django.db.models import IntegerField, Case, When, Count, Q

from .models import Driver, DriverOrder
from orders.models import Order

from geo.utils import make_route, get_route_estimated_time

import threading
from datetime import timedelta

from geographic.utils import geographical_distance, distance_to_time

update_lock = threading.Lock()
lock = threading.Lock()

def update(modified_order = None, modified_driver = None):
    update_lock.acquire()
    active = Order.objects.filter(active = True)
    query = active.annotate(driver_recommended_accepted_count = Count(
        Case(When(~Q(driverorder__driver_recommended__isnull = True, driverorder__driver_accepted__isnull = True), then = 1),
            output_field = IntegerField(),
        )
    )).filter(driver_recommended_accepted_count = 0).distinct()
    for order in ([modified_order.order] if modified_order else query):
        drivers = Driver.objects.filter(active = True).exclude(declined__order__in = [order]).annotate(num_accepted = Count('accepted'), num_recommended = Count('recommended')).order_by('num_accepted', 'num_recommended')
        for driver in ([modified_driver] if modified_driver else drivers):
            schedule = driver.get_schedule()
            previous_order = None
            next_order = None
            for i in range(len(schedule)):
                item = schedule[i]
                if item['end_time'] < order.order_time:
                    previous_order = item
                else:
                    next_order = item
                    break
            driver_pos = previous_order['order'].order.location if previous_order else driver.home_location
            driver_latlng = (driver_pos.latitude, driver_pos.longitude)
            current_restaurant_latlng = (order.restaurants.first().location.latitude, order.restaurants.first().location.longitude)
            order_latlng = (order.location.latitude, order.location.longitude)
            next_start_time_upper_bound = None
            if next_order:
                next_restaurant_latlng = (next_order['order'].order.restaurants.first().location.latitude, next_order['order'].order.restaurants.first().location.longitude)
                next_start_time_upper_bound = next_order['end_time'] - timedelta(seconds = get_route_estimated_time(next_order['order'].order.restaurant_to_destination) + distance_to_time(geographical_distance(order_latlng, next_restaurant_latlng), 60))
            current_start_time_upper_bound = order.order_time - timedelta(seconds = get_route_estimated_time(order.restaurant_to_destination) + distance_to_time(geographical_distance(driver_latlng, current_restaurant_latlng), 60))
            if (next_order and order.order_time > next_start_time_upper_bound) or (previous_order and previous_order['end_time'] > current_start_time_upper_bound):
                continue
            driver_to_restaurant = make_route(driver_pos, order.restaurants.first().location)
            if next_order:
                next_route = make_route(order.location, next_order['order'].order.restaurants.first().location)
                next_start_time = next_order['end_time'] - timedelta(seconds = get_route_estimated_time(next_order['order'].order.restaurant_to_destination) + get_route_estimated_time(next_route))
            driver_order = DriverOrder(order = order, driver_to_restaurant = driver_to_restaurant)
            start_time, end_time = driver_order.get_time_bounds()
            if (previous_order == None or start_time >= previous_order['end_time']) and (next_order == None or end_time <= next_start_time):
                driver_order.save()
                if next_order:
                    next_order['order'].driver_to_restaurant = next_route
                    next_order['order'].save()
                driver.recommend(driver_order)
                break
    update_lock.release()

def on_accept_order(driver, order):
    pass

def on_decline_order(driver, order):
    update(modified_order = order)

def on_place_order(order):
    update(modified_order = order)

def on_new_driver(driver):
    update(modified_driver = driver)