import json
from flask import make_response

from .common import get_trace_id
from .global_settings import LOGIN_FAIL, OTHER_LOGIN_FAIL, REQUEST_FAIL, SERVER_FAIL, PARAMS_FAIL


class BusinessException(Exception):
    def __init__(self, code=None, msg=None, func=None, url=None):
        self.code = code
        self.msg = msg
        self.func = func
        self.url = url


class BaseError(object):
    def __init__(self):
        pass

    @staticmethod
    def http_error(code, msg):
        data = json.dumps({
            'traceID': get_trace_id(),
            'code': code,
            'msg': msg
        })
        response = make_response(data, code)
        return response

    @staticmethod
    def not_login():
        return BaseError.http_error(code=LOGIN_FAIL, msg='用户未登录')

    @staticmethod
    def not_local_login():
        return BaseError.http_error(code=OTHER_LOGIN_FAIL, msg='您的帐号已在其他设备上登录\n请重新登录')

    @staticmethod
    def system_exception():
        raise BusinessException(code=REQUEST_FAIL, msg='后台系统异常')

    @staticmethod
    def request_params_incorrect():
        raise BusinessException(code=REQUEST_FAIL, msg='请求参数不正确')

    @staticmethod
    def server_api_error():
        raise BusinessException(code=SERVER_FAIL, msg='服务器接口异常')

    @staticmethod
    def common_field_null(field):
        raise BusinessException(code=PARAMS_FAIL, msg=field + '不能为空')

    @staticmethod
    def common_field_wrong(field):
        raise BusinessException(code=PARAMS_FAIL, msg=field + '错误')


class PermissionDenied(Exception):
    """The user did not have permission to do that"""
    pass


class ViewDoesNotExist(Exception):
    """The requested view does not exist"""
    pass


class MiddlewareNotUsed(Exception):
    """This middleware is not used in this server configuration"""
    pass


class ImproperlyConfigured(Exception):
    """Django is somehow improperly configured"""
    pass


class FieldError(Exception):
    """Some kind of problem with a model field."""
    pass