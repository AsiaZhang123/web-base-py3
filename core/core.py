import time
import json
import redis
import hashlib
import requests
import traceback
import urllib.parse

from functools import wraps
from flask import make_response, request
from py_eureka_client import eureka_client
from urllib.parse import urlencode

from configs.logging_config import zyz_logger as logger
from core.utils import get_randoms, AesCrypt, get_hashlib
from core.common import get_trace_id, is_none, get_version, get_json_header

from core.exceptions import BusinessException, BaseError
from core.check_param import build_check_rule, CheckParam
from core.global_settings import METHODS

from configs import flask_env, AES_KEY, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, AUTH_COOKIE_KEY, SSO_VERSION, \
    CALL_SYSTEM_ID, MOBILE_ORIGIN_URL, EUREKA_CLIENT_URI

check_param = CheckParam()


class Redis(object):
    def __init__(self, db=None):
        self.conn = None
        self.REDIS_POOL_CACHE = None

        self.db = db
        if not hasattr(Redis, 'REDIS_POOL_CACHE'):
            self.getRedisCoon()
        self.get_server()

    def getRedisCoon(self):
        REDIS_ = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
        REDIS_1 = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=1)
        REDIS_2 = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=2)
        REDIS_3 = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=3)
        REDIS_4 = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=4)

        self.REDIS_POOL_CACHE = {
            '0': REDIS_,
            '1': REDIS_1,
            '2': REDIS_2,
            '3': REDIS_3,
            '4': REDIS_4
        }

    def __get_pool(self):
        if self.db is None:
            self.db = '0'
        return self.REDIS_POOL_CACHE.get(self.db)

    def get_server(self):
        self.conn = redis.Redis(connection_pool=self.__get_pool())
        return self.conn

    def set_variable(self, name, value, ex=None, px=None, nx=False, xx=False):
        # 设置普通键值对
        # EX — seconds – 设置键key的过期时间，单位时秒  （datetime.timedelta 格式）
        # PX — milliseconds – 设置键key的过期时间，单位时毫秒  （datetime.timedelta 格式）
        # NX – 只有键key不存在的时候才会设置key的值 （布尔值）
        # XX – 只有键key存在的时候才会设置key的值  （布尔值）
        self.conn.set(name, value, ex, px, nx, xx)

    def get_variable(self, name):
        # 获取普通键值对的值
        return self.conn.get(name)

    def delete_variable(self, *names):
        # 删除指定的一个或多个键 根据`names`
        self.conn.delete(*names)

    def get_hget(self, name, key):
        return self.conn.hget(name, key)

    def get_hgetall(self, name):
        return self.conn.hgetall(name)

    def set_hset(self, name, key, value):
        self.conn.hset(name, key, value)

    def set_rpush(self, name, value):
        # 列表结尾中增加值
        self.conn.rpush(name, value)

    def get_lpop(self, name):
        # 弹出列表的第一个值（非阻塞）
        self.conn.lpop(name)

    def set_blpop(self, *name, timeout=0):
        # 弹出传入所有列表的第一个有值的（阻塞），可以设置阻塞超时时间
        self.conn.blpop(*name, timeout=timeout)

    def get_llen(self, name):
        # 返回列表的长度（列表不存在时返回0）
        self.conn.llen(name)

    def set_sadd(self, name, value):
        # 集合中增加元素
        self.conn.sadd(name, value)

    def delete_srem(self, name, *value):
        # 删除集合中的一个或多个元素
        self.conn.srem(name, *value)

    def spop(self, name):
        # 随机移除集合中的一个元素并返回
        return self.get_server().spop(name)

    def smembers(self, name):
        return self.conn.smembers(name)

    def sismember(self, name, value):
        # 判断value是否是集合name中的元素。是返回1 ，不是返回0
        return self.conn.sismember(name, value)

    def expire(self, name, timeout):
        # 设置key的过期时间
        self.conn.expire(name, timeout)


class LoginAndReturn(object):
    def __init__(self):
        pass


def login_required(f):
    @wraps(f)  # 不改变使用装饰器原有函数的结构(如__name__, __doc__)
    def decorated_function(*args, **kw):
        #### 所有注释都是进行单点登录操作的 !!!!!!!
        auth_token = request.cookies.get('auth_token')
        refresh_time = request.cookies.get('refresh_time')
        user_id = get_cookie_info().get('user_id')
        sso_code = get_cookie_info().get('sso_code')

        if is_none(auth_token) or is_none(refresh_time) or is_none(user_id):
            return BaseError.not_login()
        # 去redis中取 组装cookie时存的随机数
        _redis = Redis()
        _sso_code = _redis.get_hget("app_sso_code", user_id)

        # 校验cookie解析出来的随机数 和存在redis中的随机数是否一致
        if is_none(_sso_code) or is_none(sso_code) or sso_code != _sso_code:
            return BaseError.not_local_login(user_id)

        # 解密auth_token中的sign
        sign = aes_decrypt(auth_token)
        # 利用user_id + '#$%' + redis中随机数 + '#$%' + md5加密后的字符串 组装_sign
        _sign = hashlib.sha1(AUTH_COOKIE_KEY + user_id + refresh_time + sso_code).hexdigest()
        if sign == _sign:
            return f(*args, **kw)
        else:
            return BaseError.not_login()

    return decorated_function


# 制作response并返回的函数,包括制作response的请求头和请求体
#   login_data : 登录操作时必传参数，必须包括user_id，其余可以包括想带入cookie中的参数 格式{“user_id”:“12345”}
def return_data(data=None, code=200, msg=u'成功', login_data=None):
    data = {} if data is None else data
    data_json = json.dumps({'traceID': get_trace_id(),
                            'code': code,
                            'msg': msg,
                            'data': data})
    resp = make_response(data_json, 200)
    response = allow_cross_domain(resp)  # 允许跨域
    create_auth_cookie(response, login_data)  # 制作cookie
    return response


def create_auth_cookie(response, login_data):
    # 进场获取缓存cookie中的信息
    auth_token = request.cookies.get('auth_token')
    refresh_time = request.cookies.get('refresh_time')  # refresh_time = 1482222171524
    cookie_info = request.cookies.get('cookie_info')

    # 设置cookie过期时间点， time.time() + 60 表示一分钟后
    outdate = time.time() + 60 * 60 * 24 * 30  # 记录登录态三天
    _redis = Redis()
    # login 如果是登录操作，cookie中所有信息重新生成
    if not is_none(login_data) and not is_none(login_data.get('user_id')):
        user_id = login_data.get('user_id')

        sso_code = "vJjPtawUC8"  # 如果当前版本不设置单点登录，则使用固定随机码
        if get_version() in SSO_VERSION:
            # 如果版本设置单点登录,随机生成10位随机数，当做单机唯一登录码，存在redis中方便对比
            # 只要不清除登录态，单点登录则不会触发
            sso_code = get_randoms(10)
            _redis.set_hset("app_sso_code", user_id, sso_code)

        # 产生新的refresh_time 和新的auth_token
        refresh_time = str(int(round(time.time() * 1000)))
        sign = get_hashlib(AUTH_COOKIE_KEY + user_id + refresh_time + sso_code)
        auth_token = aes_encrypt(sign)
        login_data['sso_code'] = sso_code
        cookie_info = aes_encrypt(json.dumps(login_data))

    # not login 如果不是登录操作，并且cookie中auth_token和refresh_time存在
    if not is_none(auth_token) and not is_none(refresh_time):
        now_time = int(round(time.time() * 1000))
        differ_minuts = (now_time - int(refresh_time)) / (60 * 1000)

        if differ_minuts >= 30 and is_none(login_data):
            user_id = get_cookie_info().get('user_id')
            if not is_none(user_id):
                refresh_time = str(int(round(time.time() * 1000)))
                sso_code = _redis.get_hget("app_sso_code", user_id)  # 获取单点登录码
                sign = get_hashlib(AUTH_COOKIE_KEY + user_id + refresh_time + sso_code)
                auth_token = aes_encrypt(sign)
    if not is_none(auth_token) and not is_none(refresh_time) and not is_none(cookie_info):
        response.set_cookie('auth_token', value=auth_token, domain='.mofanghr.com', expires=outdate, secure=True,
                            httponly=True, samesite='Lax')
        response.set_cookie('refresh_time', value=str(refresh_time), domain='.mofanghr.com', expires=outdate)
        response.set_cookie('cookie_info', value=cookie_info, domain='.mofanghr.com', expires=outdate)
    return response


def allow_cross_domain(response):
    # response.headers['Content-Type'] = 'application/json'
    if request.headers.get('Origin') in MOBILE_ORIGIN_URL:
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin')
    else:
        response.headers['Access-Control-Allow-Origin'] = 'https://i.mofanghr.com'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = "Referer,Accept,Origin,User-Agent"
    return response


def request_check():
    def decorator(func):
        @wraps(func)
        def handle_request_data(*args, **kw):
            # 校验参数
            try:
                check_rule = build_check_rule(str(request.url_rule), str(request.rule_version),
                                              list(request.url_rule.methods & set(METHODS)))
                check_func = check_param.get_check_rules().get(check_rule)
                if check_func:
                    check_func(*args, **kw)
            except BusinessException as e:
                return e.package_error()
            except Exception as e:
                if flask_env not in ['PROD', 'PROD-LEGACY']:
                    return BaseError.system_exception()
                return BaseError.system_exception(msg=e)
            # 监听抛出的异常
            try:
                if request.trace_id is not None and request.full_path is not None:
                    logger.info('trace_id is:' + request.trace_id + ' request path:' + request.full_path)

                return func(*args, **kw)
            except BusinessException as e:
                return e.package_error()
            except Exception as e:
                if flask_env not in ['PROD', 'PROD-LEGACY']:
                    return BaseError.system_exception()
                return BaseError.system_exception(msg=e)

        return handle_request_data

    return decorator


# 使用AES算法对字符串进行加密
def aes_encrypt(text):
    aes_crypt = AesCrypt(AES_KEY)  # 初始化密钥
    encrypt_text = aes_crypt.encrypt(text)  # 加密字符串
    return encrypt_text


# 使用AES算法对字符串进行解密
def aes_decrypt(text):
    aes_crypt = AesCrypt(AES_KEY)  # 初始化密钥
    decrypt_text = aes_crypt.decrypt(text)  # 解密成字符串
    return decrypt_text


# 获取并解析cookie_info
def get_cookie_info():
    req_cookie = request.cookies.get('cookie_info')
    if req_cookie is not None:
        try:
            aes_crypt_cookie = aes_decrypt(req_cookie)
            req_cookie = json.loads(aes_crypt_cookie)
            return req_cookie
        except Exception:
            return {}
    else:
        return {}


# 工厂模式，根据不同的后端项目域名生成不同的项目对象,传入request_api中组成接口
# 针对不同的后端服务项目，实例化后生成不同的service对象
#       有三个属性 service.url  后端项目的域名 || "http://user.service.mofanghr.com/"
#                service.params  项目通用普通参数，放在params中  || {“userID”:"12345"}
#                service.common_params  项目通用公共参数，拼在url问号？后面 || {“userID”:"12345"}
class Service_api(object):
    def __init__(self, base_url, server_params=None, common_params=None):
        self.base_url = base_url
        self.server_params = server_params
        self.common_params = common_params

    def __str__(self):
        return self.base_url


# 工厂模式，根据传如的不同项目加上不同的后端接口生成不同的接口函数,请求接口并处理返回值
# base_prj 针对不同的后端服务项目，实例化后的service对象，
#       有三个属性 base_prj.url  后端项目的域名 || "http://user.service.mofanghr.com/"
#                base_prj.params  项目通用普通参数，放在params中  || {“userID”:"12345"}
#                base_prj.common_params  项目通用公共参数，拼在url问号？后面 || {“userID”:"12345"}
#
# fixUrl 接口的后缀url，拼在项目域名后，形成完整的访问接口
# baseParams 如果同一个接口需要增加相同的参数，可以放在baseParams中，增加拓展性 || {‘reqSource’:‘Mf1.0’}
class Requests_api(object):
    def __init__(self, base_prj, fixUrl, baseParams=None):
        self.base_prj = base_prj
        self.url = base_prj.base_url + fixUrl
        self.baseParams = baseParams

    # 执行请求后端的函数,get请求
    # fixUrl 同一个项目下的不同接口后缀 || inner/careerObjective/get.json
    # params 访问携带参数  || {“userID”:"12345"}
    def implement_get(self, params, **kwargs):
        url = self.url_add_common_param()
        url = self.url_add_business_param(params, url)
        logger.info(url)
        resp = requests.get(url, **kwargs)
        return self.process_response(resp, params, url)

    # 执行请求后端的函数,post请求
    # headers 请求头，如果有特殊的请求头要求，可以使用||{'Content-Type': 'application/json;charset=utf-8'}
    def implement_post(self, data=None, headers=None, **kwargs):
        url = self.url_add_common_param()
        logger.info(url)
        if "json" in kwargs:
            resp = requests.post(url, headers=headers, **kwargs)
        else:
            data = {'params': json.dumps(data)}
            resp = requests.post(url, data=data, headers=headers, **kwargs)
        return self.process_response(resp, data, url)

    # 处理服务返回状态
    @staticmethod
    def process_response(resp, params, url):
        if resp.status_code == 200:
            ret_data = resp.json()
        else:
            raise BusinessException(code=resp.status_code, msg=resp.text, url=resp.url)

        if 'code' not in ret_data or ret_data.get('code') != 200:
            logger.error('api_return_error, result: %s, url: %s, params: %s' % (str(ret_data), url, params))

        return ret_data

    # 格式化params，并组装URL的函数，将参数值转化为url编码拼接到self.url后面
    # self.url http://user.service.mofanghr.com/inner/crm/getSessionAndJobList.json?params={"jobStandardCardID":"123"}
    def url_add_business_param(self, params, url):
        # 如果存在需要整个项目传的参数，则增加进params中,例如 整个user服务需要加个参数 || {"source":"python"}
        if not is_none(self.base_prj.server_params):
            for _service_key, _service_value in self.base_prj.server_params.items():
                params[_service_key] = _service_value

        # 如果存在需要整个接口传的参数，则增加进params中
        if not is_none(self.baseParams):
            for _key, _value in self.baseParams.items():
                params[_key] = _value
        url = url + '&params=' + urllib.parse.quote_plus(json.dumps(params))
        return url

    # 给URL增加公共参数，所有接口都会有的参数
    # self.base_prj.common_params 个性化公共参数，个别接口可以根据需求自行添加 || {“platform”:“1207”}
    def url_add_common_param(self):
        url = self.url + '?traceID=' + get_trace_id() + '&callSystemID=' + str(CALL_SYSTEM_ID)

        if not is_none(self.base_prj.common_params):
            for key, value in self.base_prj.common_params.items():
                url = url + "&" + str(key) + "=" + str(value)
        return url

    def __str__(self):
        return self.url


# 例子
# SEARCH_API_URL = Service_api("http://search.service.mofanghr.com/", common_params={"callSystemID":str(CALL_SYSTEM_ID)}) # 每个service实例化一个
# job_search = Requests_api(SEARCH_API_URL,"inner/all/job/search.json") # 每个接口实例化一个
#
# result = job_search.implement_get({"userID":"12345"}) # 前端函数中使用


# 注册中心
class EurekaClient(object):
    def __init__(self):
        # 注册中心
        self.ek_cli = None

    # eureka_client.init_discovery_client("http://dev:dev@register.cloud.mofanghr.com/eureka/")
    def discovery_client(self):
        self.ek_cli = eureka_client.init_discovery_client(EUREKA_CLIENT_URI)

    # eureka_client.do_service(app_name="python_test", service="/member/getUserInfo.json", method="POST")
    def do_service(self, app_name="", service="", return_type="json", prefer_ip=False, prefer_https=False,
                   method="POST", headers=None, data=None, timeout=10,
                   cafile=None, capath=None, cadefault=False, context=None):

        headers = get_json_header() if headers is None else headers
        if headers.get("Content-Type").startswith("application/json"):
            data = bytes(json.dumps(data), encoding='utf8')
        elif headers.get("Content-Type").startswith("application/x-www-form-urlencoded"):
            data = bytes(urlencode(data), encoding='utf8')

        # try:
        resp = self.ek_cli.do_service(app_name, service, return_type, prefer_ip, prefer_https, method, headers,
                                      data, timeout, cafile, capath, cadefault, context)

        if 'code' not in resp or resp.get('code') != 200:
            logger.error('api_return_error, result: %s, url: %s, params: %s' % (str(resp), app_name + service, data))

        return resp
        # except URLError:
        #     raise BusinessException(func=BaseError.server_api_error)

    def registry_client(self, app_name, port):
        # eureka_client.init_registry_client(
        #   "http://dev:dev@register.cloud.mofanghr.com/eureka/",
        #   "python_test",
        #   instance_port=3200
        #   )
        pass

    def delete_override(self):
        # eureka_client.delete_status_override(
        #   "http://dev:dev@register.cloud.mofanghr.com/eureka/",
        #   "python_test",
        #   "192.168.127.140:python_test:3200",
        #   "2020-06-29 18:13:50")
        pass


# 注册中心
# eureka_client.init_discovery_client(EUREKA_CLIENT_URI)
# ek_cli = EurekaClient()
# ek_cli.discovery_client()
