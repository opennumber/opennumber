#! /usr/bin/env python
# -*- coding: utf-8 -*-

from _imports import *

import requests
import settings
import urlparse

class Test(unittest.TestCase):
    def setUp(self):
        self.server = os.getenv('opennumber_server', '127.0.0.1:2000')
        if not re.match(r'^https?:', self.server):
            self.server = 'http://%s' % self.server
            
        logging.info("opennumber_server: %s", self.server)
        pass

    def test_ping(self):
        url = urlparse.urljoin(self.server, '/ping')
        response = requests.get(url)
        self.assertTrue(response.status_code == 200, 'ping failure')
        
    pass #end class TestFoo


if __name__ == "__main__":
    unittest.main(failfast=True)
