from flask import Blueprint, send_from_directory, current_app

bp = Blueprint('static_files', __name__)

@bp.route('/sw.js')
def service_worker():
    """
    Ruta para servir el service worker con el MIME type correcto.
    """
    response = send_from_directory(current_app.static_folder, 'sw.js')
    # ¡Esta es la línea clave que soluciona el problema!
    response.headers['Content-Type'] = 'application/javascript'
    return response

@bp.route('/favicon.ico')
def favicon():
    """
    Ruta para servir el favicon.
    """
    return send_from_directory(current_app.static_folder, 'img/logo.png')