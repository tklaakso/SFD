from engines import GoogleMapsEngine, OSMEngine
from multiprocessing.connection import Listener
from inspect import signature
import sys

def handle_command(conn, cmd, engine):
    if type(cmd) != list:
        print('Invalid command: ' + str(cmd))
        return
    cmd_name = cmd[0]
    cmd_args = cmd[1:]
    if not (type(cmd_name) == str and hasattr(engine, cmd_name)):
        print('Invalid command: ' + str(cmd_name))
        conn.send(None)
        return
    func = getattr(engine, cmd_name)
    sig = signature(func)
    if len(sig.parameters) != len(cmd_args):
        print('Command ' + cmd_name + ' takes ' + str(len(sig.parameters)) + ' arguments, received ' + str(len(cmd_args)))
        conn.send(None)
        return
    try:
        conn.send(func(*cmd_args))
    except Exception as ex:
        print(ex)
        conn.send(None)

def serve(port, engine):
    address = ('localhost', port)
    listener = Listener(address, authkey = b'sfd')
    print('Listening on port ' + str(port))
    while True:
        conn = listener.accept()
        print('Received connection from ' + str(listener.last_accepted))
        while True:
            try:
                msg = conn.recv()
                if msg == 'close':
                    print('Connection closed')
                    break
                handle_command(conn, msg, engine)
            except Exception:
                break

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
    serve(6000, engine)