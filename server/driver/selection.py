from django.db.models import IntegerField, Case, When, Count, Q

from .models import Driver, DriverOrder
from orders.models import Order

from geo.utils import make_route, get_route_estimated_time

import threading
from datetime import timedelta

from geographic.utils import geographical_distance, distance_to_time

update_lock = threading.Lock()
lock = threading.Lock()

def get_bounding_orders(driver, order):
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
    return previous_order, next_order

def distance_heuristic(prev_order, order, next_order, driver):
    value = 0
    next_order_bias = None
    starting_point = driver.home_location
    if prev_order:
        starting_point = prev_order.location
    order_restaurant = order.restaurants.first().location
    order_destination = order.location
    starting_point_latlng = (starting_point.latitude, starting_point.longitude)
    order_restaurant_latlng = (order_restaurant.latitude, order_restaurant.longitude)
    order_destination_latlng = (order_destination.latitude, order_destination.longitude)
    if next_order:
        next_restaurant = next_order.restaurants.first().location
        next_restaurant_latlng = (next_restaurant.latitude, next_restaurant.longitude)
        next_order_bias = geographical_distance(order_destination_latlng, next_restaurant_latlng) - geographical_distance(starting_point_latlng, next_restaurant_latlng)
        value += next_order_bias
    value += geographical_distance(starting_point_latlng, order_restaurant_latlng)
    value += geographical_distance(order_restaurant_latlng, order_destination_latlng)
    return value, next_order_bias

def update(modified_order = None, modified_driver = None):
    update_lock.acquire()
    active = Order.objects.filter(active = True)
    drivers = [modified_driver] if modified_driver else list(Driver.objects.filter(active = True).annotate(num_accepted = Count('accepted'), num_recommended = Count('recommended')).order_by('num_accepted', 'num_recommended'))
    has_recommended = True
    while has_recommended:
        has_recommended = False
        for driver in drivers:
            query = active.annotate(driver_recommended_accepted_count = Count(
                Case(When(~Q(driverorder__driver_recommended__isnull = True, driverorder__driver_accepted__isnull = True), then = 1),
                    output_field = IntegerField(),
                )
            )).exclude(driverorder__driver_declined__in = [driver]).filter(driver_recommended_accepted_count = 0).distinct()
            orders = [modified_order.order] if modified_order else query
            bounding_orders = [get_bounding_orders(driver, order) for order in orders]
            heuristics = [distance_heuristic(bounding_orders[i][0]['order'].order if bounding_orders[i][0] else None, orders[i], bounding_orders[i][1]['order'].order if bounding_orders[i][1] else None, driver) for i in range(len(orders))]
            biases = [bias for value, bias in heuristics if bias != None]
            average_bias = sum(biases) / max(1, len(biases))
            heuristic_dict = {order: (heuristic[0] + average_bias if heuristic[1] == None else heuristic[0]) for order, heuristic in zip(orders, heuristics)}
            orders, bounding_orders = zip(*list(sorted(zip(orders, bounding_orders), key = lambda x: heuristic_dict[x[0]])))
            for i, order in enumerate(orders):
                previous_order, next_order = bounding_orders[i]
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
                    has_recommended = True
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