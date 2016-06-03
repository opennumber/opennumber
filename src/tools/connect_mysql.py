#! /usr/bin/env python
# -*- coding: utf-8 -*
'''
和当前的数据库进行交互
'''
import subprocess
import os
import sys

ROOT_SRC_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, ROOT_SRC_DIRECTORY)

var_runmode = 'opennumber_runmode'
if os.getenv(var_runmode):
    os.environ[var_runmode] = os.getenv(var_runmode)
else:
    runmode = len(sys.argv) == 2 and sys.argv[1] or 'debug'
    os.environ[var_runmode] = runmode

import settings


if __name__ == "__main__":
    commands = ['mysql', '--host', settings.mysql_config['host'],
                '--port', str(settings.mysql_config['port']),
                '--user', settings.mysql_config['user'],
                '--password=%s' % settings.mysql_config['password'],
                '--database', settings.mysql_config['database'],
                '--reconnect']


    subprocess.call(commands)


