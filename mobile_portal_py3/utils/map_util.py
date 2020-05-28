# -*- coding:utf-8 -*-

import requests

from configs import GAODEMAP_APIWEBKEY
# from mobile_portal_py3.constants.constant import ZHIXIA_CITY_NAME

ZHIXIA_CITY = ['8611','8631','8612','8650']
ZHIXIA_CITY_NAME = [u"北京市", u"上海市", u"天津市", u"重庆市"]

# 根据经纬度获取城市名称（高德API）
# 请求实例：https://restapi.amap.com/v3/geocode/regeo?location=116.310003,39.991957&key=6a7a913d49a68fc16c4218d481c5ce73
def location2city(location):
    url = "https://restapi.amap.com/v3/geocode/regeo?location=%s&key=%s" % (location,GAODEMAP_APIWEBKEY)
    resp = requests.get(url)
    ret_data = resp.json()
    if ret_data.get('status') == "1":
        data = ret_data.get("regeocode").get("addressComponent")
        city = data.get("province")
        if city not in ZHIXIA_CITY_NAME:
            city = data.get("city")
        return city
    else:
        return ''
# msg = {"FromUserName": "ogfZRtzpL7eJbdMOcAFidfT62pW4", "Precision": "30.000000", "ToUserName": "gh_b8e41ae8d1c5",
# "Longitude": "116.409866", "CreateTime": 1538209264, "MsgType": "event", "Latitude": "40.067104", "Event": "LOCATION"}

# if __name__ == "__main__":
#     # use_location_get_city("116.409866,40.067055")
#     from h5_portal.backend.app.controller.wechat.weixin_conductor import save_openID_location,get_user_city
#     save_openID_location(msg)
#     # get_user_city(msg)


# 根据地址获取经纬度（高德API）
# 请求实例：https://restapi.amap.com/v3/geocode/geo?address=北京市朝阳区阜通东大街6号&key=6a7a913d49a68fc16c4218d481c5ce73
def address2location(address):
    url = "https://restapi.amap.com/v3/geocode/geo?address=%s&key=%s" % (address, GAODEMAP_APIWEBKEY)
    resp = requests.get(url)
    ret_data = resp.json()
    if ret_data.get('status') == "1":
        data = ret_data.get("geocodes")[0]
        location = data.get("location")
        return location
    else:
        return ''


# 一次解析多个地址
# "https://restapi.amap.com/v3/geocode/geo?address=北京,我来了|丰宁，你好&key=8f16bc0933bbd84b462a7f9719fb6530&batch=true"
def address2code_list(address_list):
    code_list = list()
    address = "|".join(address_list)
    url = "https://restapi.amap.com/v3/geocode/geo?address=%s&key=%s" % (address, GAODEMAP_APIWEBKEY)
    if len(address_list) > 1:
        url = url + "&batch=true"
    resp = requests.get(url)
    ret_data = resp.json()
    if ret_data.get('status') == "1":
        data = ret_data.get("geocodes")
        for city in data:
            if city.get("adcode") and isinstance( city.get("adcode"), str):
                code_list.append("86" + city.get("adcode"))
            else:
                code_list.append("")
    return code_list
"""
{
    status: "1",
    info: "OK",
    infocode: "10000",
    count: "2",
    geocodes: [
        {
        formatted_address: "北京市",
        country: "中国",
        province: "北京市",
        citycode: "010",
        city: "北京市",
        district: [ ],
        township: [ ],
        neighborhood: {
            name: [ ],
            type: [ ],
        },
        building: {
            name: [ ],
            type: [ ],
        },
        adcode: "110000",
        street: [ ],
        number: [ ],
        location: "116.407526,39.904030",
        level: "省",
    },
    {
        formatted_address: "河北省承德市丰宁满族自治县",
        country: "中国",
        province: "河北省",
        citycode: "0314",
        city: "承德市",
        district: "丰宁满族自治县",
        township: [ ],
        neighborhood: {
            name: [ ],
            type: [ ],
        },
        building: {
            name: [ ],
            type: [ ],
        },
        adcode: "130826",
        street: [ ],
        number: [ ],
        location: "116.651207,41.209904",
        level: "区县",
    },
    ],
}"""
