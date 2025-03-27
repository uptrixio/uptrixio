from functools import wraps

from flask import redirect, url_for, flash
from flask_login import current_user, login_required

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):

        return f(*args, **kwargs)
    return decorated_function