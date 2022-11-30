import osmnx as ox
import networkx as nx
import tkinter
import time
import random
from math import radians, sin, cos, atan2, sqrt
from PIL import Image, ImageTk

ox.config(log_console=True, use_cache=True)

# location where you want to find your route
place     = 'Sudbury, Ontario, Canada'
# find shortest route based on the mode of travel

mode      = 'drive'        # 'drive', 'bike', 'walk'

# find shortest path based on distance or time
optimizer = 'time'        # 'length','time'

# create graph from OSM within the boundaries of some 
# geocodable place(s)
graph = ox.graph_from_place(place, network_type = mode)
#graph = ox.graph_from_xml('sudbury.osm')
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

day_begin = 0
day_end = 8 * (60**2)

driver_speed = 60

# width of the animation window
animation_window_width=800
# height of the animation window
animation_window_height=600
# initial x position of the ball
animation_ball_start_xpos = 50
# initial y position of the ball
animation_ball_start_ypos = 50
# radius of the ball
animation_ball_radius = 5
# the pixel movement of ball for each iteration
animation_ball_min_movement = 5
# delay between successive frames in seconds
animation_refresh_seconds = 0.01

def latlng_lerp(p1, p2, t):
    return (p1[0] * (1 - t) + p2[0] * t, p1[1] * (1 - t) + p2[1] * t)

def geographical_distance(p1, p2):
    R = 6373
    dlat = radians(p2[0]) - radians(p1[0])
    dlon = radians(p2[1]) - radians(p1[1])
    a = (sin(dlat / 2)) ** 2 + cos(radians(p1[0])) * cos(radians(p2[0])) * (sin(dlon / 2)) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def to_screen_coords(bbox, resolution, latlng):
    west, south, east, north = bbox
    width, height = resolution
    lat, lng = latlng
    relative_x = (lng - west) / (east - west)
    relative_y = (lat - south) / (north - south)
    return (width * relative_x, height * (1 - relative_y))

def get_route_estimated_time(route, speed):
    pairs = zip(route[:-1], route[1:])
    total_time = 0
    for a, b in pairs:
        n1 = nodes[a]
        n2 = nodes[b]
        p1 = (n1['y'], n1['x'])
        p2 = (n2['y'], n2['x'])
        dist = geographical_distance(p1, p2)
        total_time += (dist / speed) * 60**2
    return total_time

def get_route_pos(route, speed, t, speed_multiplier = 1):
    distance = speed * (t / (60**2)) * speed_multiplier
    total_distance = 0
    pairs = zip(route[:-1], route[1:])
    for a, b in pairs:
        n1 = nodes[a]
        n2 = nodes[b]
        p1 = (n1['y'], n1['x'])
        p2 = (n2['y'], n2['x'])
        dist = geographical_distance(p1, p2)
        if total_distance + dist < distance:
            total_distance += dist
        else:
            t = (distance - total_distance) / dist
            if t < 0:
                t = 0
            elif t > 1:
                t = 1
            return latlng_lerp(p1, p2, t)
    end_node = nodes[route[-1]]
    return (end_node['y'], end_node['x'])

class Driver:
    def __init__(self, node):
        self.orders = []
        self.start_node = node
    def offer_order(self, n1, t1_end):
        prev_order_idx = None
        next_order_idx = None
        for i, (n2, t2_start, t2_end, route) in enumerate(self.orders):
            if t2_end < t1_end:
                prev_order_idx = i
            elif t2_end > t1_end:
                next_order_idx = i
                break
        start = self.start_node
        if prev_order_idx != None:
            start = self.orders[prev_order_idx][0]
        route = nx.shortest_path(graph, start, n1, weight=optimizer)
        t1_start = t1_end - get_route_estimated_time(route, driver_speed)
        if prev_order_idx != None:
            if self.orders[prev_order_idx][2] > t1_start:
                return False
        if next_order_idx != None:
            n2, _, t2_end, _ = self.orders[next_order_idx]
            next_route = nx.shortest_path(graph, n1, n2, weight=optimizer)
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
        position = nodes[self.start_node]
        for n1, t1_start, t1_end, route in self.orders:
            if t1_start < t < t1_end:
                return get_route_pos(route, driver_speed, t - t1_start)
            elif t1_end <= t:
                position = nodes[n1]
            elif t1_start > t:
                break
        return (position['y'], position['x'])
 
# The main window of the animation
def create_animation_window():
    window = tkinter.Tk()
    window.title("SFD Simulator")
    # Uses python 3.6+ string interpolation
    window.geometry(f'{animation_window_width}x{animation_window_height}')
    window.resizable(False, False)
    return window
 
# Create a canvas for animation and add it to main window
def create_animation_canvas(window):
    canvas = tkinter.Canvas(window)
    canvas.configure(bg="black")
    canvas.pack(fill="both", expand=True)
    return canvas

# Create and animate ball in an infinite loop
def animation_loop(window, canvas,xinc,yinc):
    dim = (animation_window_width, animation_window_height)
    start_time = time.time()
    pil_image = Image.open('graph.png').resize(dim)
    img = ImageTk.PhotoImage(pil_image)
    canvas.create_image(0, 0, image = img, anchor = 'nw')
    list_nodes = list(nodes)
    drivers = [Driver(random.choice(list_nodes)[0]) for _ in range(10)]
    driver_balls = []
    orders = [(random.choice(list_nodes)[0], random.randint(day_begin, day_end)) for _ in range(100)]
    for order in orders:
        for driver in drivers:
            if driver.offer_order(*order):
                break
    for driver in drivers:
        start_node = nodes[driver.start_node]
        start_latlng = (start_node['y'], start_node['x'])
        start_x, start_y = to_screen_coords(bounding_box, dim, start_latlng)
        ball = canvas.create_oval(  start_x - animation_ball_radius,
                                    start_y - animation_ball_radius,
                                    start_x + animation_ball_radius,
                                    start_y + animation_ball_radius,
                                    fill="red", outline="red", width=4)
        driver_balls.append(ball)
    '''for node_id in shortest_route:
        node = nodes[node_id]
        latlng = (node['y'], node['x'])
        x, y = to_screen_coords(bounding_box, (animation_window_width, animation_window_height), latlng)
        ball = canvas.create_oval(  x - animation_ball_radius,
                                    y - animation_ball_radius,
                                    x + animation_ball_radius,
                                    y + animation_ball_radius,
                fill="green", outline="green", width=4)'''
    while True:
        time_elapsed = (time.time() - start_time) * 100
        for i in range(len(drivers)):
            driver = drivers[i]
            ball = driver_balls[i]
            canvas.moveto(ball, *to_screen_coords(bounding_box, dim, driver.get_position(time_elapsed)))
        window.update()
        time.sleep(animation_refresh_seconds)

# The actual execution starts here
animation_window = create_animation_window()
animation_canvas = create_animation_canvas(animation_window)
animation_loop(animation_window,animation_canvas, animation_ball_min_movement, animation_ball_min_movement)
