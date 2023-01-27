from django.db.models import Count

from .models import Driver
from orders.models import Order

import threading

update_lock = threading.Lock()
lock = threading.Lock()

def update():
    update_lock.acquire()
    query = Order.objects.filter(active = True, driver_recommended__isnull = True, driver_accepted__isnull = True)
    for order in query:
        drivers = Driver.objects.filter(active = True).exclude(declined__in = [order]).annotate(num_accepted = Count('accepted'), num_recommended = Count('recommended')).order_by('num_accepted', 'num_recommended')
        driver = drivers.first()
        if driver == None:
            continue
        driver.recommend(order)
    update_lock.release()

def on_accept_order(driver, order):
    update()

def on_decline_order(driver, order):
    update()

def on_place_order(order):
    update()

def on_new_driver(driver):
    update()