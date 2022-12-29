from multiprocessing.connection import Client

class GeographicInterface:
    def __init__(self):
        self.conn = Client(('localhost', 6000), authkey = b'sfd')
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()
    def close(self):
        self.conn.send('close')
    def __getattr__(self, name):
        def method(*args):
            self.conn.send([name] + list(args))
            return self.conn.recv()
        return method