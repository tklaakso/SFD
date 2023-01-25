import osmnx as ox
import networkx as nx
import tkinter
import time
import random
import datetime
from PIL import Image, ImageTk
from geographic.interface import GeographicInterface
from geographic.utils import *
from server_interface import *

def node_pos(n):
    node = nodes[n]
    return (node['y'], node['x'])

def to_screen_coords(bbox, resolution, latlng):
    west, south, east, north = bbox
    width, height = resolution
    lat, lng = latlng
    relative_x = (lng - west) / (east - west)
    relative_y = (lat - south) / (north - south)
    return (width * relative_x, height * (1 - relative_y))

class Driver:
    def __init__(self, index, pos):
        self.orders = []
        self.start_pos = pos
        self.index = index
        self.session = new_session()
        login_driver(self.session, index)
    def get_recommended_orders(self):
        return get_recommended(self.session)
    def offer_order(self, order):
        loc = order['location']
        n1 = (loc['latitude'], loc['longitude'])
        uuid = order['uuid']
        end_time = datetime.datetime.strptime(order['order_time'], '%Y-%m-%dT%H:%M:%S')
        t1_end = (end_time.hour * 60 + end_time.minute) * 60
        if self.order_accepted(n1, t1_end):
            accept_order(self.session, uuid)
            return True
        else:
            decline_order(self.session, uuid)
            return False
    def order_accepted(self, n1, t1_end):
        prev_order_idx = None
        next_order_idx = None
        for i, (n2, t2_start, t2_end, route) in enumerate(self.orders):
            if t2_end < t1_end:
                prev_order_idx = i
            elif t2_end > t1_end:
                next_order_idx = i
                break
        start = self.start_pos
        if prev_order_idx != None:
            start = self.orders[prev_order_idx][0]
        route = interface.route(start, n1)
        t1_start = t1_end - get_route_estimated_time(route, driver_speed)
        if prev_order_idx != None:
            if self.orders[prev_order_idx][2] > t1_start:
                return False
        if next_order_idx != None:
            n2, _, t2_end, _ = self.orders[next_order_idx]
            next_route = interface.route(n1, n2)
            t2_start = t2_end - get_route_estimated_time(next_route, driver_speed)
            if t2_start < t1_end:
                return False
            self.orders[next_order_idx] = (n2, t2_start, t2_end, next_route)
        insert_pos = 0
        if prev_order_idx != None:
            insert_pos = prev_order_idx + 1
        self.orders.insert(insert_pos, (n1, t1_start, t1_end, route))
        return True
    def get_position(self, t):
        position = self.start_pos
        for n1, t1_start, t1_end, route in self.orders:
            if t1_start < t < t1_end:
                return get_route_pos(route, driver_speed, t - t1_start)
            elif t1_end <= t:
                position = n1
            elif t1_start > t:
                break
        return position
    def leave(self):
        logout(self.session)

def create_animation_window():
    window = tkinter.Tk()
    window.title("SFD Simulator")
    window.geometry(f'{animation_window_width}x{animation_window_height}')
    window.resizable(False, False)
    return window

def create_animation_canvas(window):
    canvas = tkinter.Canvas(window)
    canvas.configure(bg="black")
    canvas.pack(fill="both", expand=True)
    return canvas

def animation_loop(window, canvas,xinc,yinc):
    dim = (animation_window_width, animation_window_height)
    pil_image = Image.open('graph.png').resize(dim)
    img = ImageTk.PhotoImage(pil_image)
    canvas.create_image(0, 0, image = img, anchor = 'nw')
    list_nodes = list(nodes)
    drivers = [Driver(i, node_pos(random.choice(list_nodes)[0])) for i in range(100)]
    driver_balls = []
    #orders = [(node_pos(random.choice(list_nodes)[0]), random.randint(day_begin, day_end)) for _ in range(100)]
    declined_order = True
    while declined_order:
        declined_order = False
        for driver in drivers:
            orders = driver.get_recommended_orders()
            for order in orders:
                declined_order = declined_order or not driver.offer_order(order)
    #for order in orders:
    #    for driver in drivers:
    #        if driver.offer_order(*order):
    #            break
    simulator_session = new_session()
    for driver in drivers:
        start_latlng = driver.start_pos
        start_x, start_y = to_screen_coords(bounding_box, dim, start_latlng)
        ball = canvas.create_oval(  start_x - animation_ball_radius,
                                    start_y - animation_ball_radius,
                                    start_x + animation_ball_radius,
                                    start_y + animation_ball_radius,
                                    fill="red", outline="red", width=4)
        driver_balls.append(ball)
    day_finished = False
    start_time = time.time()
    while True:
        time_elapsed = day_begin + (time.time() - start_time) * 1000
        if not day_finished and time_elapsed > day_end:
            day_finished = True
            for driver in drivers:
                driver.leave()
            reset_orders(simulator_session)
        for i in range(len(drivers)):
            driver = drivers[i]
            ball = driver_balls[i]
            canvas.moveto(ball, *to_screen_coords(bounding_box, dim, driver.get_position(time_elapsed)))
        window.update()
        time.sleep(animation_refresh_seconds)

if __name__ == '__main__':
    ox.config(log_console=True, use_cache=True)
    place = 'Sudbury, Ontario, Canada'
    mode = 'drive'
    optimizer = 'time'
    graph = ox.graph_from_place(place, network_type = mode)
    nodes = graph.nodes(data = True)

    fig, ax = ox.plot_graph(graph, filepath='graph.png', save=True, show=False, close=True)

    gdf_edges = ox.graph_to_gdfs(graph, nodes=False)['geometry']

    padding = 0.02
    west, south, east, north = gdf_edges.total_bounds
    padding_ns = (north - south) * padding
    padding_ew = (east - west) * padding
    west -= padding_ew
    south -= padding_ns
    east += padding_ew
    north += padding_ns
    bounding_box = (west, south, east, north)

    day_begin = 8 * (60**2)
    day_end = 17 * (60**2)

    driver_speed = 60

    animation_window_width = 800
    animation_window_height = 600
    animation_ball_start_xpos = 50
    animation_ball_start_ypos = 50
    animation_ball_radius = 5
    animation_ball_min_movement = 5
    animation_refresh_seconds = 0.01
    
    interface = GeographicInterface()

    animation_window = create_animation_window()
    animation_canvas = create_animation_canvas(animation_window)
    animation_loop(animation_window,animation_canvas, animation_ball_min_movement, animation_ball_min_movement)
