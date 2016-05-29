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

    @classmethod
    def get_ordered_list(cls):
        return ['white', 'green', 'yellow', 'red', 'black']
    
    @classmethod
    def next(cls, r):
        assert hasattr(cls, r)

        ordered_list = cls.get_ordered_list()
        index = ordered_list.index(r)
        return ordered_list[min(index+1, len(ordered_list)-1)]
        
    @classmethod
    def greater_than(cls, a, b):
        assert hasattr(cls, a)
        assert hasattr(cls, b)

        ordered_list = cls.get_ordered_list()
        a_index = ordered_list.index(a)
        b_index = ordered_list.index(b)

        return a_index > b_index
        
    pass

