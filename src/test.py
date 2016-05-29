#! /usr/bin/env python
# -*- coding: utf-8 -*-

from _imports import *
import ipaddress


#
import utils
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

        # create user
        phone = '133' + str(random.randint(10000000, 99999999))
        name = phone
        email = phone+'@test.org'
        user = models.UserModel.create(phone=phone, name=name, email=email, company_name=phone, company_url=phone)
        
        # create user auth
        for auth in constants.AuthEnum:
            user_auth = models.UserAuthModel.create(user.id, auth.value, quota=1000)
            pass
        
        self.user = user
        
        pass

    def tearDown(self):
        # delete user and user auth
        session = models.session
        UserAuthModel = models.UserAuthModel
        session.query(UserAuthModel).filter_by(user_id=self.user.id).delete()
        session.flush()
        logging.warn('delte user auth')

        #session.query(models.UserModel).get(self.user.id).delete()
        session.flush()
        logging.warn('delete user')
        return
    
    def get_random_phone_number(self):
        return '133' + str(random.randint(10000000, 99999999))
    
    pass


class TestPing(BaseTest):
    def test_ping(self):
        url = urlparse.urljoin(self.server, '/ping')
        response = requests.get(url)
        self.assertTrue(response.status_code == 200, 'ping failure')
        return
    
    pass #end class TestFoo

        
class Test(BaseTest):
    def test_rating(self):
        RatingEnum = constants.RatingEnum
        r = 'white'
        self.assertTrue(RatingEnum.next(r) == 'green')
        self.assertTrue(RatingEnum.next('black'), 'black')
        self.assertTrue(RatingEnum.greater_than('green', 'white'))
        self.assertTrue(RatingEnum.greater_than('black', 'red'))
        
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

    def test_user(self):
        # create user
        phone = '133' + str(random.randint(10000000, 99999999))
        name = phone
        email = phone+'@test.org'
        user = models.UserModel.create(phone=phone, name=name, email=email, company_name=phone, company_url=phone)
        
        # create user auth
        auth = random.choice(list(constants.AuthEnum))
        user_auth = models.UserAuthModel.create(user.id, auth.value, quota=1000)

        models.session.delete(user_auth)
        models.session.delete(user)
        models.session.flush()
        return

    def test_check_log(self):
        phone = self.get_random_phone_number()
        ip = '1.1.1.1'
        action = random.choice([v.value for v in constants.ActionEnum])
        check_log = models.PhoneCheckLogModel(user_id=self.user.id, phone=phone, ip=ip, action=action)
        models.session.add(check_log)
        models.session.flush()
        new_check_log = models.session.query(models.PhoneCheckLogModel).filter_by(id=check_log.id).one()
        models.session.delete(new_check_log)
        models.session.flush()
        return

    def test_check_result(self):
        user_id = 1

        phone = self.get_random_phone_number()

        rating = 'green'

        result = models.PhoneCheckResultModel.create(user_id=user_id, phone=phone, rating=rating)
        self.assertTrue(result.rating == rating)
        
        rating = 'black'
        result = models.PhoneCheckResultModel.create(user_id=user_id, phone=phone, rating=rating)
        self.assertTrue(result.rating == rating)

        new = models.session.query(models.PhoneCheckResultModel).filter_by(phone=phone).one()
        self.assertTrue(new.rating == rating)
        
        return
    pass

class TestWeb(BaseTest):
    def test_web(self):
        phone = self.get_random_phone_number()
        # check

        timestamp = str(time.time())
        action = random.choice(list(constants.ActionEnum)).value
        user = self.user
        ip = '::1'
        url = urlparse.urljoin(self.server, '/phone/check')
        params = dict(token=user.token, timestamp=timestamp, phone=phone, action=action, ip=ip)
        params['sign'] = utils.md5(user.key+timestamp+phone)
        response = requests.get(url, params=params)

        r = response.json()

        self.assertTrue(r['code'] == 0, 'access url failure: url: %s, response: %s' % (url, response.text))
        # add white list
        url = urlparse.urljoin(self.server, '/phone/commit/white_list')
        params = dict(token=user.token, timestamp=timestamp, phone=phone)
        params['sign'] = utils.md5(user.key+timestamp+phone)

        response = requests.get(url, params=params)
        logging.info('response.text: %s', response.text)
        r = response.json()

        self.assertTrue(r['code'] == 0, 'access url failure: url: %s, response: %s' % (url, response.text))
        
        return

    pass





if __name__ == "__main__":
    unittest.main(failfast=True)
