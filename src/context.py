# -*- coding: utf-8 -*-
'''
该模块是对依赖环境的封装，包括redis等等
'''
from _imports import *

import redis
import platform

# import module
import settings


# redis
socket_keepalive_options = None
if platform.system().lower() == "linux":
    socket_keepalive_options = {socket.TCP_KEEPIDLE: 3,
                                socket.TCP_KEEPCNT: 2,
                                socket.TCP_KEEPINTVL:1}
    pass


redis_config = settings.redis_config
redis_connection_pool = redis.ConnectionPool(max_connections=64,
                                             host=redis_config['host'],
                                             port=redis_config['port'],
                                             db=redis_config['db'],
                                             password=redis_config['password'],
                                             socket_timeout=1,
                                             socket_connect_timeout=1,
                                             socket_keepalive=True, # enable keepalive
                                             socket_keepalive_options=socket_keepalive_options) #

redis_client = redis.StrictRedis(connection_pool=redis_connection_pool)
redis_client.ping()



