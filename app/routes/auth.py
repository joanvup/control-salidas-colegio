from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse  # <-- IMPORT CORREGIDO
from app import db
from app.forms import LoginForm, RegistrationForm
from app.models.user import User, UserRole

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Usuario o contraseña inválidos', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # LÍNEA CORREGIDA: se usa urlparse en lugar de url_parse
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Opcional: solo permitir que administradores registren nuevos usuarios
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        flash('No tiene permiso para registrar nuevos usuarios.', 'warning')
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            email=form.email.data, 
            role=UserRole[form.role.data]
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('¡Usuario registrado correctamente!', 'success')
        return redirect(url_for('main.index')) # Redirigir al dashboard o a una lista de usuarios
        
    return render_template('auth/register.html', title='Registrar Usuario', form=form)