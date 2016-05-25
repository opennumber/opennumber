#! /usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all(subprocess=True, sys=True, Event=True)
import gevent
from _imports import *
import web
import errno
import argparse
# change working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


from gevent.pywsgi import WSGIServer, WSGIHandler



# internal module
import settings
import myweb
import models

# 用于监控该网站
class Ping(myweb.BaseHandler):
    def get(self):
        data = web.ctx.orm.query(models.TestModel).first()
        return data.name
    pass


class _wsgi_handler(WSGIHandler):
    """
    当访问量非常巨大的时候，如果客户端首先退出，则屏蔽该错误信息。
    """
    def process_result(self):
        try:
            super(_wsgi_handler, self).process_result()
        except socket.error as err:
            if err.errno in (errno.EPIPE,):
                pass
            else:
                raise
        except:
            raise
        return  # 
    pass #end class _wsgi_handler


# 
def handler_signal_ctrl_c():
    pid = os.getpid()
    os.killpg(os.getpgid(pid), signal.SIGKILL)
    os.kill(pid, signal.SIGKILL)
    return  # 


def handler_notfound():
    return web.notfound("page not found")


def handler_internalerror():
    return web.internalerror("server internal error")


urls = [
    # phone
    '/phone/check/?', 'handler_phone.CheckHandler', # 检测手机号码
    '/phone/commit/while_list', 'handler_phone.CommitWhileListHandler', # 提交白名单
    '/phone/commit/check_result', 'handler_phone.CommitCheckResultHandler', # 直接提交检查结果,例如黑名单。

    
    '/ping/?', 'Ping']

if __name__ == "__main__":
    # disable debug
    web.config.debug= False

    # handler ctrl-c
    gevent.signal(signal.SIGINT, handler_signal_ctrl_c)


    # parse option
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--host', dest="host", default="127.0.0.1", nargs="?", help="host", metavar="127.0.0.1")
    parser.add_argument('--port', dest="port", type=int, required=True, nargs="?", help="listen port")

    args = parser.parse_args(sys.argv[1:])
    

    # start webapp
    app = web.application(urls, globals())
    application = app.wsgifunc()

    app.notfound = handler_notfound
    app.internalerror = handler_internalerror

    logging.warn("listen: %s:%s" %(args.host, args.port))
    server = WSGIServer((args.host, args.port),
                        application,
                        backlog=64,
                        log=None,
                        handler_class=_wsgi_handler)
    server.serve_forever()
    pass
