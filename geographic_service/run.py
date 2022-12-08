from geographic.service import GeographicService
from geographic.engines import OSMEngine, GoogleMapsEngine
import sys

if __name__ == '__main__':
    place = 'Sudbury, Ontario, Canada'
    flags = []
    if len(sys.argv) > 1:
        flags = sys.argv[1:]
    engine = None
    for flag in flags:
        if flag == 'maps':
            engine = GoogleMapsEngine(place)
        elif flag == 'osm':
            engine = OSMEngine(place)
        else:
            print('Invalid flag: ' + flag)
            exit()
    if engine == None:
        engine = OSMEngine(place)
    service = GeographicService()
    service.serve(6000, engine)