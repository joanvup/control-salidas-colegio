from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.models.user import UserRole

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('Se requiere rol de administrador para acceder a esta página.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function