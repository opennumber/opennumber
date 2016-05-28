# -*- coding: utf-8 -*-
"""
该模块用于表示错误.
code_map = dict(code=XError class)
"""

import types
import constants


class BaseError(Exception):
    code = -1
    message = 'base_error'
    
    def __init__(self, message=''):
        if message and isinstance(message, types.UnicodeType):
            message = message.encode('utf-8')
            pass

        if not message:
            message = self.message
            pass
        
        self.args = (self.code, message)
        self.message = message
        pass

    def __str__(self):
        code, message = self.args
        return '%s: code: %s, message: %s' %(self.__class__, code, message)

    def __repr__(self):
        return self.__str__  #

    
    pass #end class BaseError


class Success(BaseError):
    """
    """
    code = 0
    message = 'success'
    pass #end class Success


class InternalError(BaseError):
    """
    internal error
    """
    code = 1
    message = 'internal error'
    pass #end class InternalError


class MissingParameter(BaseError):
    code = 2
    message = "missing parameter '%s'"

    def __init__(self, parameter_name):
        super(MissingParameter, self).__init__(self.message % parameter_name)
        return
    pass


class ParameterTypeError(BaseError):
    code = 3
    message = 'parameter type error'
    pass


class IntegerParameterError(ParameterTypeError):
    code = 4
    def __init__(self, pname):
        message = "'%s' type error. except integer" % (pname)
        super(IntegerParameterError, self).__init__(message)
        return
    pass

class DatetimeParameterError(ParameterTypeError):
    code = 5
    def __init__(self, pname):
        message = "'%s' type error. except datetime. e.g: '2016-01-01 20:00:00'" % (pname)
        super(DatetimeParameterError, self).__init__(self, message)
        return
    pass


class DateParameterError(ParameterTypeError):
    code = 6
    def __init__(self, pname):
        message = "'%s' type error. except date. e.g: '2016-01-01'" % (pname)
        super(DateParameterError, self).__init__(message)
        return
    pass


class MissingTimestampError(BaseError):
    code = 7
    message = 'missing parameter "timestamp". timestamp is used for debug. e.g: timestamp=time()'
    pass


class InvalidPhoneNumber(BaseError):
    code = 8
    message = 'invalid phone number. regex: "%s"' % (constants.phone_number_regex.pattern)

class InvalidAction(BaseError):
    code = 9
    message = 'invalid action. valid action %s' % ([x.value for x in constants.ActionEnum])

    pass

class NotFoundToken(BaseError):
    code = 10
    message = 'not found token'
    pass

class AccessReject(BaseError):
    code = 11
    message = 'access reject'
    pass

class QuotaOverFlow(BaseError):
    code = 12
    message = 'daily quota overflow. get help to increment quota by contact administrator'
    pass
    
class InvalidIp(BaseError):
    code = 13
    message = 'invalid ip value. except ipv4 & ipv6'
    pass

class InvalidRating(BaseError):
    code = 14
    message = 'invalid rating. valid rating %s' % ([e.value for e in constants.RatingEnum])
    pass

# 下面的代码对所有的错误的代码进行校验，保证error.code不会重复
_locals_keys = locals().keys()
code_map = {}

for key in _locals_keys:
    obj = locals()[key]
    if not issubclass(type(obj), type):
        continue
    
    if issubclass(obj, BaseError):
        if obj.code in code_map:
            raise RuntimeError('duplicate code: code: %s' %(obj.code))
        code_map[obj.code] = obj
        pass
    pass


