from configs import DEFAULT_METHODS
from core.mofang_flask import MFBlueprint

user_b = MFBlueprint('user', __name__, default_methods=DEFAULT_METHODS)
root = MFBlueprint('root', __name__, default_methods=DEFAULT_METHODS)
