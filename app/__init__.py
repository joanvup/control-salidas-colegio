from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Por favor, inicie sesión para acceder a esta página.'
login.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Asegurarse de que las carpetas de trabajo existan
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'))
    if not os.path.exists(app.config['TEMP_FOLDER']):
        os.makedirs(app.config['TEMP_FOLDER'])

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Registrar Blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.management import bp as management_bp
    app.register_blueprint(management_bp, url_prefix='/manage') # Rutas de gestión bajo /manage

    from app.routes.scanner import bp as scanner_bp
    app.register_blueprint(scanner_bp)

    from app import commands
    commands.register_commands(app)

    # --- REGISTRAR NUEVO BLUEPRINT DE ARCHIVOS ESTÁTICOS ---
    from app.routes.static_files import bp as static_files_bp
    app.register_blueprint(static_files_bp)

    return app

from app.models import user, student, door, exit_log