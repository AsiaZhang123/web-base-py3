import json
import traceback
from flask import make_response, request

from core.common import get_trace_id, is_none
from configs.logging_config import zyz_logger as logger
from core.global_settings import LOGIN_FAIL, OTHER_LOGIN_FAIL, SERVER_FAIL, PARAMS_FAIL, REQUEST_FAIL, \
    SYSTEM_CODE_404, SYSTEM_CODE_503, SYSTEM_ERROR


class BusinessException(Exception):
    def __init__(self, code=None, msg=None, func=None, url=None):
        self.code = code
        self.msg = msg
        self.func = func
        self.url = url

    def package_error(self):
        if self.func is not None:
            return self.func()
        elif self.code is not None and self.msg is not None:
            self.business_exception_log()
            if self.code == SYSTEM_CODE_404 or self.code == SYSTEM_CODE_503:
                return BaseError.self_error(code=self.code, msg=SYSTEM_ERROR)
            else:
                return BaseError.self_error(code=self.code, msg=self.msg)
        else:
            return BaseError.system_exception()

    def business_exception_log(self):
        if request.trace_id is not None and request.full_path is not None:
            logger.error('BusinessException, code: %s, msg: %s trace_id: %s request path: %s' % (self.code, self.msg, request.trace_id, request.full_path))
        else:
            logger.error('BusinessException, code: %s, msg: %s' % (self.code, self.msg))


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
    def self_error(code, msg):
        data = json.dumps({
            'traceID': get_trace_id(),
            'code': code,
            'msg': msg
        })
        response = make_response(data, 200)
        return response

    @staticmethod
    def not_login():
        return BaseError.http_error(code=LOGIN_FAIL, msg='用户未登录')

    @staticmethod
    def not_local_login(user_id):
        logger.info("账号在其他设备登陆了%s" % user_id)
        return BaseError.http_error(code=OTHER_LOGIN_FAIL, msg='您的帐号已在其他设备上登录\n请重新登录')

    @staticmethod
    def system_exception(msg='后台系统异常'):
        if not is_none(request.trace_id):
            logger.error('request fail trace id is:' + str(request.trace_id))
        logger.error(traceback.format_exc())
        return BaseError.self_error(code=REQUEST_FAIL, msg=msg)

    @staticmethod
    def request_params_incorrect():
        logger.error('request params fail is:' + str(request.path) + str(request.values))
        return BaseError.self_error(code=REQUEST_FAIL, msg='请求参数不正确')

    @staticmethod
    def server_api_error():
        return BaseError.self_error(code=SERVER_FAIL, msg='服务器接口异常')

    @staticmethod
    def common_field_null(field):
        return BaseError.self_error(code=PARAMS_FAIL, msg=field + '不能为空')

    @staticmethod
    def common_field_wrong(field):
        return BaseError.self_error(code=PARAMS_FAIL, msg=field + '错误')


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
