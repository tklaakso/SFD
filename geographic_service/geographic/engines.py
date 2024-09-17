import googlemaps
import osmnx as ox
import networkx as nx
import random
from collections import OrderedDict

class Engine:
    def __init__(self, place):
        self.place = place
    def route(self, a, b):
        pass
    def geocode(self, addr):
        pass

class GoogleMapsEngine(Engine):
    def __init__(self, place):
        super().__init__(place)
        self.client = googlemaps.Client(key = '')
    def route(self, a, b):
        res = []
        dirs = self.client.directions(a, b, mode = 'driving')
        for i, leg in enumerate(dirs[0].get('legs')):
            for j, step in enumerate(leg.get('steps')):
                if i == 0 and j == 0:
                    res.append((step['start_location']['lat'], step['start_location']['lng']))
                res.append((step['end_location']['lat'], step['end_location']['lng']))
        return res
    def geocode(self, addr):
        geo_data = self.client.geocode(addr)
        latlng = geo_data[0]['geometry']['location']
        return (latlng['lat'], latlng['lng'])
    def reverse_geocode(self, latlng):
        resp = self.client.reverse_geocode(latlng)[0]
        res = {}
        for component in resp['address_components']:
            types = component['types']
            if 'street_number' in types:
                res['street_num'] = component['long_name']
            elif 'route' in types:
                res['street_name'] = component['long_name']
            elif 'postal_code' in types:
                res['postal_code'] = component['long_name']
            elif 'locality' in types:
                res['city'] = component['long_name']
            elif 'administrative_area_level_1' in types:
                res['province'] = component['long_name']
            elif 'country' in types:
                res['country'] = component['long_name']
        return res

class OSMEngine(Engine):
    def __init__(self, place):
        super().__init__(place)
        ox.config(log_console=True, use_cache=True)
        self.graph = ox.graph_from_place(place, network_type = 'drive')
        self.nodes = self.graph.nodes(data = True)
        self.nodes_list = list(self.nodes)
    def route(self, a, b):
        res = []
        na = ox.nearest_nodes(self.graph, *a[::-1])
        nb = ox.nearest_nodes(self.graph, *b[::-1])
        node_route = nx.shortest_path(self.graph, na, nb, weight = 'time')
        for node_id in node_route:
            node = self.nodes[node_id]
            res.append((node['y'], node['x']))
        return res
    def geocode(self, addr):
        try:
            return ox.geocode(addr)
        except Exception as ex:
            print(ex)
        return None
    def reverse_geocode(self, latlng):
        try:
            params = OrderedDict()
            params['lat'] = latlng[0]
            params['lon'] = latlng[1]
            params['format'] = 'json'
            resp = ox.downloader.nominatim_request(params = params, request_type = 'reverse')
            return {'street_name' : resp['address']['road'],
                    'street_num' : resp['address']['house_number'],
                    'city' : resp['address']['city'],
                    'province' : resp['address']['state'],
                    'country' : resp['address']['country'],
                    'postal_code' : resp['address']['postcode']}
        except Exception as ex:
            print(ex)
        return None
    def random_address(self):
        res = None
        while not (res and self.geocode(res['street_num'] + ' ' + res['street_name'] + ', ' + res['city'] + ', ' + res['province'] + ', ' + res['country'] + ', ' + res['postal_code'])):
            latlng = self.random_node_location()
            res = self.reverse_geocode(latlng)
        return res
    def random_node_location(self):
        node = self.nodes[random.choice(self.nodes_list)[0]]
        latlng = (node['y'] + random.uniform(-0.003, 0.003), node['x'] + random.uniform(-0.003, 0.003))
        return latlng
