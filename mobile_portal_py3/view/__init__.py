from configs import DEFAULT_METHODS
from core.mofang_flask import MFBlueprint
from core.check_param import SubCheckParam

# 将所有蓝图初始化工作放在view中，1、方便管理 2、当有多个版本时，可以复用 3、避免循环调用 portal->user->view  portal->view(之前是 user->portal->view->user)
root = MFBlueprint('root', __name__, default_methods=DEFAULT_METHODS)
user_bp = MFBlueprint('user', __name__, default_methods=DEFAULT_METHODS, url_prefix='/member')
task_bp = MFBlueprint('task', __name__, default_methods=DEFAULT_METHODS, url_prefix='/member')
file_bp = MFBlueprint('file', __name__, default_methods=DEFAULT_METHODS, url_prefix='/member')

check_member = SubCheckParam(DEFAULT_METHODS)
