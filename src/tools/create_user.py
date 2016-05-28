#! /usr/bin/env python
# -*- coding: utf-8 -*
'''
创建授权访问用户
'''

import subprocess
import os
import sys
import argparse

ROOT_SRC_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, ROOT_SRC_DIRECTORY)

#
import context
import settings
import models


if __name__ == "__main__":
    parse = argparse.ArgumentParser(usage="create user")
    parse.add_argument('--phone', required=True, nargs='?', dest='phone')
    parse.add_argument('--name', required=True, nargs="?")    
    parse.add_argument('--email', required=True, nargs='?', dest='email')

    parse.add_argument('--company_name', required=True, nargs="?")
    parse.add_argument('--company_url', required=True, nargs='?')
    parse.add_argument('--status', nargs="?", choices=['0', '1'], default='1')
    
    args = parse.parse_args(sys.argv[1:])

    models.UserModel.create(name=args.name, phone=args.phone, email=args.email,
                            company_name=args.company_name, company_url=args.company_url)
    
    

