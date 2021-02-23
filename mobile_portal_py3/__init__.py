import os
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

import configs
from core.check_param import SubCheckParam
from core.mofang_flask import MFFlask
from configs import DEFAULT_METHODS
from core.core import check_param


app = MFFlask(__name__)
app.config.from_object(configs)
CORS(app)
db = SQLAlchemy(app)


@app.route('/zyz')
def abc():
    return "hello zyz!!!"


from .view import root, member, user_bp, resume_bp
from .view import check_member

# 将所有调用蓝图的包全部导入一遍，以便蓝图上注册的url生效
for pwd, dirs, files in os.walk("./mobile_portal_py3/view", topdown=False):
    for file in files:
        if file.endswith('.py') and file != '__init__.py':
            exec("import " + pwd[2:].replace('/', '.') + "." + file[:-3])

# app注册蓝图必须在 所有应用蓝图的包导入之后，这样蓝图上的url和函数映射才能生效
app.register_blueprint(root)
app.register_blueprint(member)
app.register_blueprint(user_bp)
app.register_blueprint(resume_bp)
# app.register_blueprint(file_bp)

check_param.register_check_param(check_member, url_prefix='/member')
