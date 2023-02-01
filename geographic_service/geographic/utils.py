from math import radians, sin, cos, atan2, sqrt

def latlng_lerp(p1, p2, t):
    return (p1[0] * (1 - t) + p2[0] * t, p1[1] * (1 - t) + p2[1] * t)

def geographical_distance(p1, p2):
    R = 6373
    dlat = radians(p2[0]) - radians(p1[0])
    dlon = radians(p2[1]) - radians(p1[1])
    a = (sin(dlat / 2)) ** 2 + cos(radians(p1[0])) * cos(radians(p2[0])) * (sin(dlon / 2)) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def get_route_estimated_time(route, speed):
    pairs = zip(route[:-1], route[1:])
    total_time = 0
    for a, b in pairs:
        dist = geographical_distance(a, b)
        total_time += distance_to_time(dist, speed)
    return total_time

def distance_to_time(dist, speed):
    return (dist / speed) * 60**2

def get_route_distance(route):
    pairs = zip(route[:-1], route[1:])
    total_distance = 0
    for a, b in pairs:
        dist = geographical_distance(a, b)
        total_distance += dist
    return total_distance

def get_route_pos(route, speed, t, speed_multiplier = 1):
    distance = speed * (t / (60**2)) * speed_multiplier
    total_distance = 0
    pairs = zip(route[:-1], route[1:])
    for a, b in pairs:
        dist = geographical_distance(a, b)
        if total_distance + dist < distance:
            total_distance += dist
        else:
            t = (distance - total_distance) / dist
            if t < 0:
                t = 0
            elif t > 1:
                t = 1
            return latlng_lerp(a, b, t)
    return route[-1]