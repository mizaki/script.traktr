# -*- coding: utf-8 -*-
"""Module for running non-blocking HTTPS requests to trakt"""

import time
import thread
import threading

try:
    # Python 3.0 +
    import http.client as httplib
except ImportError:
    # Python 2.7 and earlier
    import httplib

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Andrew Etches"
__email__ = "andrew.etches@dur.ac.uk"
__status__ = "Production"

class NBConnection():
    """Allows non-blocking HTTP(S) requests to trakt"""
    def __init__(self, host):
        self._raw_connection = httplib.HTTPSConnection(host)
        self._response = None
        self._response_lock = threading.Lock()
        self._closing = False

    def request(self, method, url, body = None, headers=None):
        """Send raw HTTPS request to trakt"""
        if headers == None:
            headers = {}

        self._raw_connection.request(method, url, body, headers)

    def has_result(self):
        """Checks if a result is available, doesn't block"""
        if self._response_lock.acquire(False):
            self._response_lock.release()
            return True
        else:
            return False

    def get_result(self):
        """Block until a result's available and return it when it is"""
        while not self.has_result() and not self._closing:
            time.sleep(1)
        return self._response

    def fire(self):
        """Create the new thread to run a request to trakt in"""
        self._response_lock.acquire()
        thread.start_new_thread(NBConnection._run, (self,))

    def _run(self):
        """Get a response from trakt in a new thread"""
        self._response = self._raw_connection.getresponse()
        self._response_lock.release()

    def close(self):
        """Close the connection to trakt"""
        self._closing = True
        self._raw_connection.close()

