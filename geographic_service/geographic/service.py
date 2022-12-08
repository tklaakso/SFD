from .engines import GoogleMapsEngine, OSMEngine
from multiprocessing.connection import Listener
from inspect import signature

class GeographicService:
    def __init__(self):
        pass
    def handle_command(self, conn, cmd, engine):
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
    def serve(self, port, engine):
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
                    self.handle_command(conn, msg, engine)
                except Exception:
                    break