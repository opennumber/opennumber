#! /usr/bin/env python
# -*- coding: utf-8 -*-

from _imports import *

#
import err
import models
import constants
import requests
import settings
import urlparse

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.server = os.getenv('opennumber_server', '127.0.0.1:2000')
        if not re.match(r'^https?:', self.server):
            self.server = 'http://%s' % self.server
            
        logging.info("opennumber_server: %s", self.server)
        pass

    pass


class TestPing(BaseTest):
    def test_ping(self):
        url = urlparse.urljoin(self.server, '/ping')
        response = requests.get(url)
        self.assertTrue(response.status_code == 200, 'ping failure')
        return
    
    pass #end class TestFoo

        
class Test(BaseTest):
    def test_user_auth_quota_redis(self):
        user_id = random.randint(10000000, 99990000)

        user_auth = list(constants.AuthEnum)[0].value
        quota = 1

        r = models.UserAuthQuotaRedis(user_id, user_auth, quota)
        
        used = r.access()
        self.assertTrue(used==1)
        try:
            r.access()
        except err.QuotaOverFlow as e:
            pass

        r.flush()
        return

    pass
        

if __name__ == "__main__":
    unittest.main(failfast=True)
