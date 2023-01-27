import sys
import xmltodict
from server_interface import *

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 3:
        print('Usage: python generate_accounts.py [generate | clear] [accounts | restaurants | orders | all]')
        exit()
    accounts = args[2] == 'accounts' or args[2] == 'all'
    restaurants = args[2] == 'restaurants' or args[2] == 'all'
    orders = args[2] == 'orders' or args[2] == 'all'
    if restaurants:
        print('Reading menu metadata...')
        with open('generation/menus.meta', 'r') as file:
            menu_files = file.read().split('\n')
        print('Reading menu files...')
        menus = []
        for menu_file in menu_files:
            with open('generation/' + menu_file + '.xml', 'r') as file:
                menus.append(xmltodict.parse(file.read())['restaurant'])
    if args[1] == 'generate':
        if accounts:
            for i in range(1000):
                print('Generating driver ' + str(i))
                generate_driver(i)
                print('Generating customer ' + str(i))
                generate_customer(i)
                print('Generating merchant ' + str(i))
                generate_merchant(i)
        if restaurants:
            for i, menu in enumerate(menus):
                print('Making restaurant ' + menu['name'])
                generate_restaurant(i, menu)
        if orders:
            addresses = set()
            for i in range(1000):
                print('Generating order ' + str(i))
                address = generate_order(i, addresses)
                addresses.add(address)
    elif args[1] == 'clear':
        if orders:
            for i in range(1000):
                print('Deleting order ' + str(i))
                delete_order(i)
        if restaurants:
            for i in range(len(menus)):
                print('Deleting restaurant ' + str(i))
                delete_restaurant(i)
        if accounts:
            for i in range(1000):
                print('Deleting driver ' + str(i))
                delete_driver(i)
                print('Deleting customer ' + str(i))
                delete_customer(i)
                print('Deleting merchant ' + str(i))
                delete_merchant(i)
