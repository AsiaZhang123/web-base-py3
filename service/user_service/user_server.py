# -*-coding: utf-8-*-
import requests
from configs import HRO_API_URL, PLATFORM
from core.core import Service_api, Requests_api
from core.common import get_json_header


SEARCH_API_URL = Service_api(HRO_API_URL, common_params={"platform": PLATFORM})


def get_userInfo(params):
    req = Requests_api(SEARCH_API_URL, "inner/roster/getUserInfo.json")   # 获取个人信息
    return req.implement_get(params)


def post_userInfo(params):
    req = Requests_api(SEARCH_API_URL, "inner/roster/getUserInfo.json")   # 获取个人信息
    return req.implement_post(params, headers=get_json_header())
