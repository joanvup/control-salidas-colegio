import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Clase de configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    TEMP_FOLDER = os.path.join(basedir, 'temp')
     # Tiempo mínimo en minutos entre registros de salida para el mismo estudiante
    EXIT_LOG_COOLDOWN_MINUTES = 60
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024