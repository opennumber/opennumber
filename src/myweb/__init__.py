# -*- coding: utf-8 -*
'''
该模块仅仅简单的对webpy进行封装
'''
from _imports import *
import urlparse
import sys
reload(sys)
import functools
sys.setdefaultencoding('utf-8')
import datetime
import traceback
import logging
import web

import codecs
import ipaddress
from sqlalchemy.orm import scoped_session, sessionmaker

#
import err
import utils
import models
from models import UserModel, UserAuthModel, UserAuthQuotaRedis
import constants
import settings


logger = logging.getLogger(__name__)

class SeeOther(web.webapi.HTTPError):
    """A `303 See Other` redirect. web.py has bug"""
    def __init__(self, url, absolute=False):

        status = '303 See Other'
        newloc = url

        home = web.ctx.environ['HTTP_ORIGIN']
        newloc = urlparse.urljoin(home, url)
        logger.info('seeother: %s', newloc)
        headers = {
            'Content-Type': 'text/html',
            'Location': newloc
        }
        web.webapi.HTTPError.__init__(self, status, headers, "")
        pass
    pass

web.seeother = SeeOther


class Response(object):
    def __init__(self):
        """
        """
        self.code = err.Success.code
        self.message = err.Success.message
        self.result = None
        
        pass # end def __init__


    def json_dumps(self):
        return vars(self) # end def dumps


    @classmethod
    def internal_error(cls):
        response = cls()
        response.code = err.InternalError.code
        response.message = err.InternalError.message
        return response
    
    pass #end class Response

# 
class BaseHandler(object):
    """
    webpy的封装， 用来返回html内容
    """
    STATUS_SUCCESS = '200 SUCCESS'

    def __init__(self):
        web.header('Content-Type', 'text/html; charset=utf8')
        pass  #

    @property
    def client_ip(self):
        """
        """
        ip = web.ctx.env.get('HTTP_X_REAL_IP',web.ctx.ip)
        return  ip


    def get(self, *args):
        raise NotImplementedError("Not implemented!")

    
    def post(self, *args):
        raise NotImplementedError("Not implemented!")        

    
    def get_argument(self, argument, default=utils.none):
        """获取参数"""
        v = web.input().get(argument, '').strip()
        if v:
            return v

        if default is not utils.none:
            return default
        
        raise err.MissingParameter(argument)
    
    def get_argument_int(self, argument, default=utils.none):
        if default is not utils.none:
            assert isinstance(default, utils.IntegerTypes)
            
        v = self.get_argument(argument, None)
        if v:
            try:
                return int(v)
            except ValueError as e:
                raise err.IntegerParameterError(argument)

            
        if default is not utils.none:
            return default
        
        raise err.MissingParameter(argument)


    def get_argument_timestamp(self):
        timestamp = web.input().get('timestamp', '')
        if not timestamp:
            raise err.MissingTimestampError()
        return timestamp

    
    def get_argument_datetime(self, argument, default=utils.none):
        if default is not utils.none:
            assert isinstance(default, datetime.datetime)
            
        v = self.get_argument(argument, None)
        if v:
            try:
                pattern = '%Y-%m-%d %H:%M:%S'
                d = datetime.datetime.stfptime(v, pattern)
            except ValueError as e:
                raise err.DatetimeParameterError(argument)

        if default is not utils.none:
            return default

        raise err.MissingParameter(argument)
    
    def get_argument_phone(self, argument):
        v = self.get_argument(argument)

        if constants.phone_number_regex.match(v):
            return v
        
        raise err.InvalidPhoneNumber()
        
    
    def get_argument_action(self, argument):
        v = self.get_argument(argument)
        if v not in constants.ActionEnum.__members__:
            raise err.InvalidAction()
        return v
    
    
    def get_argument_ip(self, argument, default=utils.none):
        v = self.get_argument(argument, '')
        if v:
            try:
                ipaddress.ip_address(v)
                return v
            except ValueError as e:
                raise err.InvalidIp()
            

        if default is not utils.none:
            return default
        
        return ''


    def get_argument_rating(self, argument):
        v = self.get_argument(argument)

        if v not in constants.RatingEnum.__members__:
            raise err.InvalidRating()
        return v

    
    def POST(self, *args, **kwargs):
        return self.GET(*args, **kwargs)
        

    def log_request(self):
        logger.info('client:%s url: %s # %s', self.client_ip, web.ctx.environ['PATH_INFO'], web.input())

        
    def GET(self, *args, **kwargs):
        """
        """
        response = Response.internal_error()
        try:
            self.log_request()
            with models.Session() as orm:
                web.ctx.orm = orm
                response =  self.get(*args, **kwargs)
                return response
        except:
            logger.exception('BaseHandler failure:')
            status = '500 InternalError'
            headers = {'Content-Type': 'text/html'}
            raise web.HTTPError(status, headers, 'internal error')

    pass 


class JsonHandler(BaseHandler):
    def __init__(self):
        super(JsonHandler, self).__init__()
        web.header("Access-Control-Allow-Origin", '*')
        web.header('Cache-Control', 'no-cache, no-store, must-revalidate')
        web.header('Pragma', 'no-cache')
        web.header('Expires', '0')
        web.header('Content-Type', 'application/json; charset=utf8')
        
        pass

    def check(self, auth, sign_parameter_list=[]):
        """
        检测用户是否具有权限，同时对皮进行校验签名
        """
        assert auth in constants.AuthEnum, 'invalid auth "%s"' % (auth, )
        # get token
        token = self.get_argument('token')

        session = web.ctx.orm
        # get user
        user = session.query(UserModel).filter_by(token=token, status=constants.StatusEnum.valid.value).scalar()
        if not user:
            raise err.NotFoundToken()

        # check auth
        user_auth = session.query(UserAuthModel).filter_by(user_id=user.id, auth=auth.value).scalar()
        if not user_auth:
            raise err.AccessReject()

        # quota
        used = UserAuthQuotaRedis(user.id, user_auth.auth, user_auth.quota).access()

        web.ctx.user = user
        web.ctx.user_auth = user_auth


        # sign
        sign_text = u''
        lst = [user.key, self.get_argument_timestamp()]
        lst.extend(sign_parameter_list)
        for p in lst:
            sign_text += p
            pass


        sign = self.get_argument('sign')
        if sign != utils.md5(sign_text):
            raise err.InvaildSign()

        return

        
    def GET(self, *args, **kwargs):
        """
        """
        response = Response.internal_error()
        web.ctx.orm = None
        try:
            self.get_argument_timestamp()            
            self.get_argument('token')
            self.get_argument('sign')
            
            self.log_request()
            with models.Session() as session:
                web.ctx.orm = session
                result = self.get(*args, **kwargs)
                response.code = 0
                response.message = err.Success.message
                response.result = result
                pass
            
        except err.BaseError as e:
            logger.error("base error: %s", e.message)
            response.code = e.code
            response.message = e.message
        except:
            logger.exception('JsonHandler failure:')
            pass
        finally:
            del web.ctx.orm
            
        response_json_data =  utils.json_dumps(response)
        return response_json_data
    
    pass #end class JsonApi

