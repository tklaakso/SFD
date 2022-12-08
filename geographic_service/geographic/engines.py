import googlemaps
import osmnx as ox
import networkx as nx

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
        self.client = googlemaps.Client(key = 'AIzaSyB-yNql09AeAYM2ys8QYv1RxpUdJFPxgrI')
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

class OSMEngine(Engine):
    def __init__(self, place):
        super().__init__(place)
        ox.config(log_console=True, use_cache=True)
        self.graph = ox.graph_from_place(place, network_type = 'drive')
        self.nodes = self.graph.nodes(data = True)
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
        return ox.geocode(addr)