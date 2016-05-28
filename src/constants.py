# -*- coding: utf-8 -*
import enum
import re
phone_number_regex = re.compile(r'(13|14|15|17|18|19)\d{9}$')

class StatusEnum(enum.Enum):
    invalid = '0'
    valid = '1'
    pass


class AuthEnum(enum.Enum):
    phone_check = 'phone_check'
    phone_commit_white_list = 'phone_commit_white_list'
    phone_commit_check_result = 'phone_commit_check_result'
    pass


class ActionEnum(enum.Enum):
    login = 'login'
    register = 'register'
    logout = 'logout'
    post = 'post'
    pass


class RatingEnum(enum.Enum):
    white = 'white'
    green = 'green'
    yellow = 'yellow'
    red = 'red'
    black = 'black'
    pass

