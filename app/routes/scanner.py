from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.student import Student
from app.models.door import Door, DoorStatus
from app.models.exit_log import ExitLog, colombia_tz
from datetime import datetime, timedelta
from pytz import utc

bp = Blueprint('scanner', __name__)

@bp.route('/scan')
@login_required
def scan_page():
    """Muestra la página principal de escaneo."""
    # Solo las puertas abiertas están disponibles para seleccionar
    open_doors = Door.query.filter_by(status=DoorStatus.OPEN).all()
    return render_template('scanner/scanner.html', title="Escanear Salida", doors=open_doors)

@bp.route('/scan/verify', methods=['POST'])
@login_required
def verify_qr():
    """API endpoint para verificar un código QR."""
    data = request.get_json()
    qr_code_data = data.get('qr_data')
    
    if not qr_code_data:
        return jsonify({'success': False, 'error': 'No se recibió el código QR.'}), 400

    student = Student.query.filter_by(qr_code_data=qr_code_data).first()

    if not student:
        return jsonify({'success': False, 'error': 'Código QR no válido. Estudiante no encontrado.'}), 404

    return jsonify({
        'success': True,
        'student': {
            'id': student.id,
            'name': student.name,
            'course': student.course,
            'photo_url': f"/static/uploads/photos/{student.photo}" if student.photo else "/static/img/avatar.png",
            'authorized': student.authorized_to_leave
        }
    })

@bp.route('/scan/log', methods=['POST'])
@login_required
def log_exit():
    """API endpoint para registrar una salida confirmada con validación de cooldown."""
    data = request.get_json()
    student_id = data.get('student_id')
    door_id = data.get('door_id')

    student = Student.query.get(student_id)
    door = Door.query.get(door_id)

    if not student or not door:
        return jsonify({'success': False, 'error': 'Estudiante o puerta no válidos.'}), 400
    
    if door.status != DoorStatus.OPEN:
        return jsonify({'success': False, 'error': 'La puerta seleccionada está cerrada.'}), 400

    cooldown_minutes = current_app.config.get('EXIT_LOG_COOLDOWN_MINUTES', 5)
    last_log = ExitLog.query.filter_by(student_id=student_id).order_by(ExitLog.timestamp.desc()).first()

    if last_log:
        # --- CORRECCIÓN CLAVE ---
        # El timestamp de la BD es naive, pero representa la hora de Colombia.
        # Usamos .localize() para hacerlo "aware" de la zona horaria correcta.
        last_log_timestamp_aware = colombia_tz.localize(last_log.timestamp)
        
        # Ahora sí, restamos dos datetimes que están en la misma zona horaria.
        time_since_last_log = datetime.now(colombia_tz) - last_log_timestamp_aware
        
        if time_since_last_log.total_seconds() < (cooldown_minutes * 60):
            error_message = f"Salida ya registrada para {student.name} hace menos de {cooldown_minutes} minutos."
            return jsonify({'success': False, 'error': error_message}), 409
    
    new_log = ExitLog(
        student_id=student_id,
        door_id=door_id,
        operator_id=current_user.id
    )
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Salida de {student.name} registrada.'})