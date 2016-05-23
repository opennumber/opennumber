# -*- coding: utf-8 -*
'''
该模块仅仅简单的对webpy进行封装
'''
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


#
import err
import utils
import models


log = logging.getLogger(__name__)

class SeeOther(web.webapi.HTTPError):
    """A `303 See Other` redirect. web.py has bug"""
    def __init__(self, url, absolute=False):

        status = '303 See Other'
        newloc = url

        home = web.ctx.environ['HTTP_ORIGIN']
        newloc = urlparse.urljoin(home, url)
        log.info('seeother: %s', newloc)
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
        v = web.input().get(argument, None)
        if v:
            return v.strip()

        if default is not utils.none:
            return default
        
        raise err.MissingParameter(argument)
    
    def get_argument_int(self, argument, default=utils.none):
        v = self.get_argument(argument, None)
        if v:
            try:
                return int(v)
            except ValueError as e:
                raise err.IntegerParameterError(argument)

            
        if default is not utils.none:
            if isinstance(default, (int, long)):
                return default
            else:
                raise TypeError("parameter '%s' default value should be integer." % (argument))

        raise err.MissingParameter(argument)


    def get_argument_timestamp(self):
        timestamp = web.input().get('timestamp', '')
        if not timestamp:
            raise err.MissingTimestampError()
        return

    
    def get_argument_datetime(self, argument, default=utils.none):
        v = self.get_argument(argument, None)
        if v:
            try:
                pattern = '%Y-%m-%d %H:%M:%S'
                d = datetime.datetime.stfptime(v, pattern)
            except ValueError as e:
                raise err.DatetimeParameterError(argument)

        if default is not utils.none:
            if isinstance(default, datetime.datetime):
                return default
            else:
                raise TypeError("parameter '%s' default value should be datetime." % (argument))

        raise err.MissingParameter(argument)

    
    def POST(self, *args, **kwargs):
        return self.GET(*args, **kwargs)
        

    def log_request(self):
        log.info('client:%s url: %s # %s', self.client_ip, web.ctx.environ['PATH_INFO'], web.input())

        
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
            log.exception('BaseHandler failure:')
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

    
    def GET(self, *args, **kwargs):
        """
        """
        response = Response.internal_error()
        try:
            self.log_request()
            with models.Session() as orm:
                web.ctx.orm = orm
                response = self.get(*args, **kwargs)
                return utils.json_dumps(response)
        except err.BaseError as e:
            log.error("base error: %s", e.message)
            response.code = e.code
            response.message = e.message
        except:
            log.exception('JsonHandler failure:')
            pass

        response_json_data =  utils.json_dumps(response)
        return response_json_data
    
    pass #end class JsonApi

