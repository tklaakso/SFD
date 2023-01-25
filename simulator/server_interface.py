import requests
import random
import datetime

from geographic.interface import GeographicInterface

server_addr = 'http://127.0.0.1:8000/'

def get_token(session):
    session.get(server_addr + 'accounts/session/')

def login_customer(session, i):
    session.post(server_addr + 'accounts/login/', json = {'username' : 'Customer' + str(i), 'password' : 'password'}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def login_merchant(session, i):
    session.post(server_addr + 'accounts/login/', json = {'username' : 'Merchant' + str(i), 'password' : 'password'}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def login_driver(session, i):
    session.post(server_addr + 'accounts/login/', json = {'username' : 'Driver' + str(i), 'password' : 'password'}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def get_restaurants(session, address):
    response = session.post(server_addr + 'restaurants/browse/', json = address, headers = {'X-CSRFToken' : session.cookies['csrftoken']})
    return response.json()

def get_menu(session, uuid):
    response = session.get(server_addr + 'restaurants/menu?id=' + uuid, headers = {'X-CSRFToken' : session.cookies['csrftoken']})
    return response.json()

def add_item(session, uuid):
    session.post(server_addr + 'orders/add/', json = {'item' : uuid, 'quantity' : 1}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def logout(session):
    session.post(server_addr + 'accounts/logout/', headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def place_order(session, time):
    session.post(server_addr + 'orders/place/', json = {'time' : time}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def get_orders(session):
    response = session.get(server_addr + 'orders/view_all/', headers = {'X-CSRFToken' : session.cookies['csrftoken']})
    return response.json()

def cancel_order(session, uuid):
    session.post(server_addr + 'orders/cancel/', json = {'uuid' : uuid}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def new_session():
    session = requests.Session()
    get_token(session)
    return session

def signup_driver(session, i):
    session.post(server_addr + 'accounts/signup/', json = {'username' : 'Driver' + str(i), 'password' : 'password'}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def signup_customer(session, i):
    session.post(server_addr + 'accounts/signup/', json = {'username' : 'Customer' + str(i), 'password' : 'password'}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def signup_merchant(session, i):
    session.post(server_addr + 'accounts/signup/', json = {'username' : 'Merchant' + str(i), 'password' : 'password'}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def driver_signup(session):
    session.post(server_addr + 'driver/signup/', headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def delete_account(session):
    session.post(server_addr + 'accounts/delete/', json = {'password' : 'password'}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def reset_orders(session):
    session.post(server_addr + 'orders/reset/', headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def generate_driver(i):
    session = new_session()
    signup_driver(session, i)
    login_driver(session, i)
    driver_signup(session)
    logout(session)

def delete_driver(i):
    session = new_session()
    login_driver(session, i)
    delete_account(session)

def accept_order(session, uuid):
    session.post(server_addr + 'driver/accept/', json = {'uuid' : uuid}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def decline_order(session, uuid):
    session.post(server_addr + 'driver/decline/', json = {'uuid' : uuid}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def get_recommended(session):
    response = session.get(server_addr + 'driver/recommended/', headers = {'X-CSRFToken' : session.cookies['csrftoken']})
    return response.json()

def generate_customer(i):
    session = new_session()
    signup_customer(session, i)

def delete_customer(i):
    session = new_session()
    login_customer(session, i)
    delete_account(session)

def generate_merchant(i):
    session = new_session()
    signup_merchant(session, i)

def delete_merchant(i):
    session = new_session()
    login_merchant(session, i)
    delete_account(session)

def generate_restaurant(i, menu):
    session = new_session()
    login_merchant(session, i)
    resp = session.post(server_addr + 'restaurants/create/', json = {'name' : menu['name'], 'address' : menu['address']}, headers = {'X-CSRFToken' : session.cookies['csrftoken']})
    for item in menu['items']['item']:
        resp = session.post(server_addr + 'menus/add/', json = item, headers = {'X-CSRFToken' : session.cookies['csrftoken']})
    session.post(server_addr + 'accounts/logout/', headers = {'X-CSRFToken' : session.cookies['csrftoken']})

def delete_restaurant(i):
    session = new_session()
    login_merchant(session, i)
    session.post(server_addr + 'restaurants/delete/', headers = {'X-CSRFToken' : session.cookies['csrftoken']})
    logout(session)

def generate_order(i):
    session = new_session()
    login_customer(session, i)
    with GeographicInterface() as inter:
        address = inter.random_address()
    print('Generated customer address ' + address['street_num'] + ' ' + address['street_name'] + ', ' + address['city'] + ', ' + address['province'] + ', ' + address['country'] + ', ' + address['postal_code'])
    restaurants = get_restaurants(session, address)
    restaurant = random.choice(restaurants)
    print('Chose restaurant ' + restaurant['name'])
    uuid = restaurant['uuid']
    menu = get_menu(session, uuid)
    num_items = random.randint(1, 5)
    for _ in range(num_items):
        item = random.choice(menu)
        print('Selected item ' + item['name'])
        add_item(session, item['uuid'])
    now = datetime.datetime.now()
    order_time = datetime.datetime(year = now.year, month = now.month, day = now.day, hour = random.randint(9, 16), minute = random.randint(0, 59))
    print('ORDER TIME')
    print(order_time)
    place_order(session, str(order_time))
    logout(session)

def delete_order(i):
    session = new_session()
    login_customer(session, i)
    orders = get_orders(session)
    for order in orders:
        cancel_order(session, order['uuid'])
    logout(session)