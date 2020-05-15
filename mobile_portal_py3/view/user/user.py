# -*-coding: utf-8-*-
from core.core import return_data,request_check
from mobile_portal_py3 import root, inner
import time


@inner.route('/user/loginByMobile')
def Login_mobile():
    data = "hello world!!"
    time.sleep(10)
    return return_data(data=data, login_data={"user_id":"1234545"})


@inner.route('/user/loginByMobile', version=["2.0.0"])
def Login_mobile():
    data = "hello world!!2"
    return return_data(data=data, login_data={"user_id": "1234545"})
