import time
import json

import tornado.httpclient

http_client = tornado.httpclient.HTTPClient()

class HTTPServiceProxy(object):

    def __init__(self, host='localhost', port=6999, cache_timeout=5.0):
        self._host = host
        self._port = port
        self._cache_timeout = cache_timeout

        self._cache = {}
        self._cache_time = {}

    def get(self, *path):
        if path in self._cache and \
            self._cache_time[path] + self._cache_timeout > time.time():
            return self._cache[path]

        try:
            response = http_client.fetch('http://%s:%d/%s' % (self._host, self._port, '/'.join(path)))
            self._cache[path] = response.body
            self._cache_time[path] = time.time()
            return response.body
        except tornado.httpclient.HTTPError as e:
            if path in self._cache:
                del self._cache[path]
            return None

    def post(self, data='', *path):
        pass

class MonitorProxy(HTTPServiceProxy):
    """
    Proxy object for the challenge monitor service.
    """

    def __init__(self):
        super(MonitorProxy, self).__init__(host='localhost', port=6999, cache_timeout=5.0)
        
    @property
    def challenges(self):
        return json.loads(self.get('list'))
    
    def status(self, challenge):
        try:
            return json.loads(self.get('status')).get(challenge, None)
        except TypeError:
            return None

    def start(self, challenge):
        self.post('start', challenge)

    def stop(self, challenge):
        self.post('stop', challenge)

    def metadata(self, challenge):
        try:
            return json.loads(self.get('metadata', challenge))
        except TypeError:
            return None

monitor = MonitorProxy()

class AuthProxy(HTTPServiceProxy):
    """
    Proxy object for the user authentication serivce.
    """

    def __init__(self, host='127.0.0.1', port=6998, cache_timeout=1.0):
        super(AuthProxy, self).__init__(host='localhost', port=6998, cache_timeout=1.0)

    @property
    def users(self):
        return json.loads(self.get('list'))

    def set_password(self, user, password):
        pass # TODO

auth = AuthProxy()