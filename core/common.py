# 这个文件中的函数只依赖与第三方包，和静态参数，防止重复调用

import re
import uuid
import json
import urllib.parse

from flask import request
from configs import flask_env


def get_trace_id():
    try:
        if request.trace_id is None:
            return uuid.uuid1()
        else:
            return request.trace_id
    except Exception:
        return str(uuid.uuid1())


def is_none(arg):
    return not arg or str(arg) in ['null', 'none', 'false']


def get_version():
    try:
        return request.version
    except AttributeError:
        pass
    return request.args.get('version')


def get_ip_address():
    try:
        if request.headers.get('x-forwarded-for') is not None:
            ip_address = str(request.headers.get('x-forwarded-for'))
            if "," in ip_address:
                return ip_address.split(",")[-1]
            return ip_address
    except:
        pass
    return '127.0.0.1'


# 获取get请求时，传的参数params并解url
def get_request_params():
    try:
        request_params = json.loads(urllib.parse.unquote_plus(request.args.get('params')))
        params = get_common_params(request_params)
    except Exception:
        params = {}
    return params


# 获取post请求时，传的参数params并解json
def post_request_params():
    try:
        request_params = json.loads(request.data)
        params = get_common_params(request_params)
    except Exception:
        params = {}

    return params


# 获取form_data中的参数并转换为字典格式
def form_data_to_dict():
    try:
        request_params = {key: dict(request.form)[key][0] for key in dict(request.form)}
        params = get_common_params(request_params)
    except Exception:
        params = {}
    return params


# 获取公共参数并加到params中
def get_common_params(params):
    try:
        if request.args.get('platform') is not None:
            params['platform'] = request.args.get('platform')
    except Exception:
        pass
    return params


def check_params(params):
    sql_res = re.findall(
        r"select|update | and|and | or|or |create |delete |drop |insert |rename |set |join |union |from | from|where"
        r"|current_database"
        r"|truncate |alert |confirm |script |prompt |expression |onclick |iframe |content-length|>|<|;|\*|\(|\)",
        str(params).lower())
    if len(sql_res) > 0:
        if flask_env not in ['PROD', 'PROD-LEGACY']:
            raise Exception("params error," + str(sql_res))
        raise Exception("Parameter has SQL injection risk, please redefine the parameter.")
    if "avatar" in params and params != "":
        avatar = params.get("avatar")
        ava_res = re.match(r"^https://public.mofanghr.com[a-zA-Z0-9/]+\.(jpg|png)$", avatar)
        if ava_res is None:
            raise Exception("Illegal avatar link,Please use the MF link.")


def get_sform_header():
    return {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    }


def get_json_header():
    return {
        'Content-Type': 'application/json;charset=utf-8'
    }


def partial_update(all_data, update_data):
    if not isinstance(all_data, dict) or not isinstance(update_data, dict):
        raise Exception('all_data or update_data is not a dict')

    for (key, value) in update_data.items():
        if value is not None and value != [] and value != '':
            all_data[key] = value
        elif all_data.get(key):
            all_data.pop(key)
    return all_data


def filter_model_data(model, *args):
    return_dict = dict()
    for arg in args:
        if model.get(str(arg)) is not None and model.get(str(arg)) != '' and model.get(str(arg)) != []:
            return_dict[str(arg)] = model.get(str(arg))
    return return_dict