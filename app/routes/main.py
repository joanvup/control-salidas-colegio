from flask import Blueprint, render_template, request, Response, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.models.student import Student
from app.models.exit_log import ExitLog, colombia_tz
from app.models.door import Door
from app.models.user import User, UserRole
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime, time, timedelta
import json
import csv
from io import StringIO
from app.pdf_generator import generate_report_pdf as create_report_pdf

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """Ruta del Dashboard principal con datos detallados para el modal."""
    
    now_co = datetime.now(colombia_tz)
    today_start = now_co.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now_co.replace(hour=23, minute=59, second=59, microsecond=999999)
    seven_days_ago_start = (now_co - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. Tarjetas de resumen
    total_students = db.session.query(func.count(Student.id)).scalar()
    total_exits_today = ExitLog.query.filter(ExitLog.timestamp.between(today_start, today_end)).count()
    
    # MODIFICACIÓN: Ahora seleccionamos también el ID de la puerta
    exits_by_door_today = db.session.query(Door.id, Door.name, func.count(ExitLog.id))\
        .join(ExitLog)\
        .filter(ExitLog.timestamp.between(today_start, today_end))\
        .group_by(Door.id, Door.name).all()

    # --- NUEVA CONSULTA: Obtener detalles de todas las salidas de hoy ---
    todays_exits_details_query = ExitLog.query.options(
        joinedload(ExitLog.student)
    ).filter(ExitLog.timestamp.between(today_start, today_end)).order_by(ExitLog.timestamp.desc()).all()
    
    # Convertimos los objetos a un formato simple para JavaScript
    todays_exits_list = [
        {
            "student_name": log.student.name,
            "student_course": log.student.course,
            "student_photo_url": f"/static/uploads/photos/{log.student.photo}" if log.student.photo else "/static/img/avatar.png",
            "door_id": log.door_id,
            "timestamp": log.local_timestamp.strftime('%I:%M %p')
        } for log in todays_exits_details_query
    ]

    # ... (El resto de la lógica para las gráficas no cambia) ...
    colombia_timezone_offset = '-05:00'
    date_in_colombia = func.date(func.convert_tz(ExitLog.timestamp, '+00:00', colombia_timezone_offset))
    exits_by_day_query = db.session.query(date_in_colombia, func.count(ExitLog.id)).filter(ExitLog.timestamp >= seven_days_ago_start).group_by(date_in_colombia).order_by(date_in_colombia).all()
    daily_exits_dict = {date_obj.strftime("%Y-%m-%d"): count for date_obj, count in exits_by_day_query}
    chart_labels_days = [(seven_days_ago_start.date() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    chart_data_days = [daily_exits_dict.get(day, 0) for day in chart_labels_days]
    exits_by_course_today_query = db.session.query(Student.course, func.count(ExitLog.id)).join(Student).filter(ExitLog.timestamp.between(today_start, today_end)).group_by(Student.course).all()
    chart_labels_courses = [course for course, count in exits_by_course_today_query]
    chart_data_courses = [count for course, count in exits_by_course_today_query]
    chart_labels_doors = [door_name for door_id, door_name, count in exits_by_door_today]
    chart_data_doors = [count for door_id, door_name, count in exits_by_door_today]

    return render_template(
        'index.html', 
        title='Dashboard',
        total_students=total_students,
        total_exits_today=total_exits_today,
        exits_by_door_today=exits_by_door_today,
        todays_exits_details=todays_exits_list, # Pasamos la nueva lista a la plantilla
        chart_data={
            'days': {'labels': chart_labels_days, 'data': chart_data_days},
            'courses': {'labels': chart_labels_courses, 'data': chart_data_courses},
            'doors': {'labels': chart_labels_doors, 'data': chart_data_doors}
        }
    )
# El resto del archivo no necesita cambios.
@bp.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    # --- Lógica de Ordenamiento ---
    # Obtenemos los parámetros de la URL (GET) o usamos valores por defecto.
    sort_by = request.args.get('sort_by', 'timestamp')
    direction = request.args.get('direction', 'desc')

    # Validamos que la dirección sea segura
    if direction not in ['asc', 'desc']:
        direction = 'desc'

    # --- Lógica de Fechas ---
    # Las fechas pueden venir de un POST (filtrado) o de un GET (ordenamiento)
    today_str = datetime.now(colombia_tz).strftime('%Y-%m-%d')
    if request.method == 'POST':
        start_date_str = request.form.get('start_date', today_str)
        end_date_str = request.form.get('end_date', today_str)
    else:
        start_date_str = request.args.get('start_date', today_str)
        end_date_str = request.args.get('end_date', today_str)
    
    try:
        start_date = colombia_tz.localize(datetime.strptime(start_date_str, '%Y-%m-%d')).replace(hour=0, minute=0, second=0)
        end_date = colombia_tz.localize(datetime.strptime(end_date_str, '%Y-%m-%d')).replace(hour=23, minute=59, second=59)
    except (ValueError, TypeError):
        flash("Formato de fecha inválido. Usando fechas de hoy.", "warning")
        start_date_str = end_date_str = today_str
        start_date = colombia_tz.localize(datetime.strptime(start_date_str, '%Y-%m-%d')).replace(hour=0, minute=0, second=0)
        end_date = colombia_tz.localize(datetime.strptime(end_date_str, '%Y-%m-%d')).replace(hour=23, minute=59, second=59)

    # --- Construcción de la Consulta ---
    # Mapeo de los nombres de columnas a los objetos de SQLAlchemy
    sortable_columns = {
        'timestamp': ExitLog.timestamp,
        'student': Student.name,
        'course': Student.course,
        'door': Door.name,
        'operator': User.username # Suponiendo que el modelo User está importado
    }
    
    # Seleccionamos la columna por la que ordenar, con un valor por defecto seguro
    sort_column = sortable_columns.get(sort_by, ExitLog.timestamp)

    # Construimos la consulta base con los joins necesarios para poder ordenar
    query = ExitLog.query.join(Student).join(Door).join(User)

    # Aplicamos el filtro de fecha
    query = query.filter(ExitLog.timestamp.between(start_date, end_date))

    # Aplicamos el ordenamiento
    if direction == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    logs = query.all()

    return render_template('reports.html', 
                           logs=logs, 
                           start_date=start_date_str, 
                           end_date=end_date_str, 
                           sort_by=sort_by,
                           direction=direction,
                           title="Reporte de Salidas")

@bp.route('/export/csv')
@login_required
def export_csv():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    start_date = colombia_tz.localize(datetime.strptime(start_date_str, '%Y-%m-%d'))
    end_date = colombia_tz.localize(datetime.strptime(end_date_str, '%Y-%m-%d')).replace(hour=23, minute=59, second=59)

    logs_query = ExitLog.query.options(
        joinedload(ExitLog.student),
        joinedload(ExitLog.door),
        joinedload(ExitLog.operator)
    )
    logs = logs_query.filter(ExitLog.timestamp.between(start_date, end_date)).all()

    def generate():
        data = StringIO()
        writer = csv.writer(data)
        writer.writerow(["Timestamp (Hora Colombia)", "ID Estudiante", "Nombre Estudiante", "Curso", "Puerta", "Operador"])
        for log in logs:
            writer.writerow([
                log.local_timestamp.strftime('%Y-%m-%d %I:%M %p'),
                log.student.id,
                log.student.name,
                log.student.course,
                log.door.name,
                log.operator.username
            ])
        yield data.getvalue()
    
    response = Response(generate(), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename=f"reporte_salidas_{start_date_str}_a_{end_date_str}.csv")
    return response

@bp.route('/export/pdf')
@login_required
def export_pdf():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    start_date = colombia_tz.localize(datetime.strptime(start_date_str, '%Y-%m-%d'))
    end_date = colombia_tz.localize(datetime.strptime(end_date_str, '%Y-%m-%d')).replace(hour=23, minute=59, second=59)
    
    logs_query = ExitLog.query.options(
        joinedload(ExitLog.student),
        joinedload(ExitLog.door),
        joinedload(ExitLog.operator)
    )
    logs = logs_query.filter(ExitLog.timestamp.between(start_date, end_date)).all()
    
    if not logs:
        flash("No hay datos para exportar en el rango de fechas seleccionado.", "warning")
        return redirect(url_for('main.reports'))

    pdf_buffer = create_report_pdf(logs, start_date_str, end_date_str)
    
    return Response(pdf_buffer, 
                    mimetype='application/pdf', 
                    headers={"Content-Disposition": f"attachment;filename=reporte_salidas_{start_date_str}_a_{end_date_str}.pdf"})