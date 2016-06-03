#! /usr/bin/env python
# -*- coding: utf-8 -*
'''
创建用户访问份额
'''

import subprocess
import os
import sys
import argparse

ROOT_SRC_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, ROOT_SRC_DIRECTORY)

var_runmode = 'opennumber_runmode'
if os.getenv(var_runmode):
    os.environ[var_runmode] = os.getenv(var_runmode)
else:
    runmode = len(sys.argv) == 2 and sys.argv[1] or 'debug'
    os.environ[var_runmode] = runmode


#
import context
import settings
import models
import constants

if __name__ == "__main__":
    parse = argparse.ArgumentParser(usage="create user auth")
    parse.add_argument('--phone', required=True, nargs='?', dest='phone')
    
    parse.add_argument('--auth', required=True, nargs="?", choices=[e.value for e in constants.AuthEnum])    
    parse.add_argument('--quota', required=True, nargs='?', type=int)


    args = parse.parse_args(sys.argv[1:])
    assert args.quota > 0
    user = models.session.query(models.UserModel).filter_by(phone=args.phone).one()
    
    models.UserAuthModel.create(user.id, auth=args.auth, quota=args.quota)
    
    

