import time

from mobile_portal_py3.view import user_bp
from service import user_service

from core.error import Error
from core.core import return_data, request_check, login_required
from core.common import get_request_params, get_json_header
from core.exceptions import BusinessException

from ..version import versions


@user_bp.route('/loginByMobile')
@request_check()
def Login_mobile():
    data = "hello world!!"
    time.sleep(10)
    return return_data(data=data, login_data={"user_id": "1234545"})


@user_bp.route('/getUserInfo.json', version=versions)
@request_check()
@login_required
def Login_mobile():
    params = get_request_params()
    result = user_service.get_userInfo(params)
    if result.get('code') != 200:
        raise BusinessException(func=Error.get_fail)
    data = result.get('data')
    return return_data(data=data, login_data={"user_id": "1234545"})


@user_bp.route('/getUserInfo.json', version=["3.0.0", "4.0.0"])
@request_check()
@login_required
def Login_mobile():
    params = get_request_params()
    result = user_service.post_userInfo(params)
    if result.get('code') != 200:
        raise BusinessException(func=Error.get_fail)
    data = result.get('data')
    return return_data(data=data, login_data={"user_id": "1234545"})
