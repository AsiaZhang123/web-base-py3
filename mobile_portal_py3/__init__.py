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


@app.route('/index')
def abc():
    return "hello world!!!"


check_member = SubCheckParam(DEFAULT_METHODS)

# root = MFBlueprint('root', __name__, default_methods=DEFAULT_METHODS)
# manager = MFBlueprint('manager', __name__, default_methods=DEFAULT_METHODS)
# member = MFBlueprint('member', __name__, default_methods=DEFAULT_METHODS)


from mobile_portal_py3.view import *
from mobile_portal_py3.view.user import root, user_b
# from mobile_portal_py3.view.resume import resume_b

app.register_blueprint(root)
app.register_blueprint(user_b, url_prefix='/outer/user')
# app.register_blueprint(resume_b, url_prefix='/outer/resume')
# app.register_blueprint(member, url_prefix='/member')

check_param.register_check_param(check_member, url_prefix='/member')
