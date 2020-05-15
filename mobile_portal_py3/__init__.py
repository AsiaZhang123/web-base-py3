from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


import configs
from core.check_param import SubCheckParam
from core.mofang_flask import MFFlask, MFBlueprint
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


root = MFBlueprint('root', __name__, default_methods=DEFAULT_METHODS)
inner = MFBlueprint('inner', __name__, default_methods=DEFAULT_METHODS)
outer = MFBlueprint('outer', __name__, default_methods=DEFAULT_METHODS)
manager = MFBlueprint('manager', __name__, default_methods=DEFAULT_METHODS)
owner = MFBlueprint('owner', __name__, default_methods=DEFAULT_METHODS)
member = MFBlueprint('member', __name__, default_methods=DEFAULT_METHODS)
third = MFBlueprint('third', __name__, default_methods=DEFAULT_METHODS)
offline = MFBlueprint('offline', __name__, default_methods=DEFAULT_METHODS)


from mobile_portal_py3.view import *

app.register_blueprint(root)
app.register_blueprint(inner, url_prefix='/inner')
app.register_blueprint(outer, url_prefix='/outer')
app.register_blueprint(manager, url_prefix='/manager')
app.register_blueprint(owner, url_prefix='/owner')
app.register_blueprint(member, url_prefix='/member')
app.register_blueprint(third, url_prefix='/third')
app.register_blueprint(offline, url_prefix='/offline')

check_param.register_check_param(check_member, url_prefix='/member')
