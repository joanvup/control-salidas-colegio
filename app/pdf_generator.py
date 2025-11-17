import os
from io import BytesIO
from flask import current_app
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from app.models.exit_log import colombia_tz 

# --- Dimensiones Verticales del Carnet ---
CARD_WIDTH = 5.4 * cm
CARD_HEIGHT = 8.5 * cm

# --- Colores y Fuentes ---
PRIMARY_COLOR = HexColor("#0A2240") # Azul oscuro para el texto
SECONDARY_COLOR = HexColor("#4A4A4A") # Gris para subtítulos

def draw_vertical_card(c, student):
    """
    Dibuja los datos del estudiante sobre la imagen de fondo del carnet.
    """
    # --- Rutas a los archivos de imagen ---
    background_path = os.path.join(current_app.root_path, 'static/img/carnet_background.png')
    
    if student.photo:
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos', student.photo)
    else:
        photo_path = os.path.join(current_app.root_path, 'static/img/avatar.png')

    # --- 1. Dibujar el Fondo ---
    # Esto es lo más importante. La imagen de fondo contiene todo el diseño.
    try:
        c.drawImage(background_path, 0, 0, width=CARD_WIDTH, height=CARD_HEIGHT)
    except Exception:
        # Si el fondo no existe, dibuja un borde para que no quede vacío.
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        c.drawCentredString(CARD_WIDTH / 2, CARD_HEIGHT / 2, "Fondo no encontrado")

    # --- 2. Colocar la Foto del Estudiante (en el recuadro superior) ---
    PHOTO_SIZE = 3 * cm # Tamaño del área para la foto
    photo_x = (CARD_WIDTH - PHOTO_SIZE) / 2 # Centrado horizontal
    photo_y = 3.5 * cm # Posición vertical estimada desde abajo
    
    if os.path.exists(photo_path):
        c.drawImage(photo_path, photo_x, photo_y, 
                    width=PHOTO_SIZE, height=PHOTO_SIZE, 
                    preserveAspectRatio=True, anchor='c', mask='auto')

    # --- 3. Colocar Nombre e ID (entre los dos recuadros) ---
    center_x = CARD_WIDTH / 2
    
    # Nombre
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(PRIMARY_COLOR)
    # Truncamos el nombre si es muy largo para evitar que se salga del carnet
    student_name = (student.name[:24] + '..') if len(student.name) > 24 else student.name
    c.drawCentredString(center_x, 3 * cm, student_name.upper())

    # ID
    c.setFont("Helvetica", 9)
    c.setFillColor(SECONDARY_COLOR)
    c.drawCentredString(center_x, 2.65 * cm, f"{student.id}")

    # --- 4. Colocar el Código QR (en el recuadro inferior) ---
    QR_SIZE = 2.4 * cm # Tamaño del área para el QR
    qr_x = (CARD_WIDTH - QR_SIZE) / 2 # Centrado horizontal
    qr_y = 0.2 * cm # Posición vertical estimada desde abajo

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=1)
    qr.add_data(student.qr_code_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    qr_reportlab_img = ImageReader(qr_buffer)
    c.drawImage(qr_reportlab_img, qr_x, qr_y, width=QR_SIZE, height=QR_SIZE, preserveAspectRatio=True)


def generate_single_card_pdf(student):
    """Genera un PDF para un solo estudiante con el nuevo diseño vertical."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    draw_vertical_card(c, student)
    c.save()
    buffer.seek(0)
    return buffer


def generate_bulk_cards_pdf(students):
    """
    Genera un PDF con todos los carnets, donde CADA PÁGINA es un carnet.
    """
    buffer = BytesIO()
    # 1. El canvas se crea con el tamaño de un solo carnet.
    c = canvas.Canvas(buffer, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    
    for student in students:
        # 2. Dibuja el carnet en la página actual.
        draw_vertical_card(c, student)
        # 3. Finaliza la página actual y crea una nueva para el siguiente carnet.
        c.showPage()
                
    c.save()
    buffer.seek(0)
    return buffer

def generate_report_pdf(logs, start_date, end_date):
    """Genera un PDF tabular con el reporte de logs."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=cm, leftMargin=cm, topMargin=cm, bottomMargin=cm)
    
    elements = []
    styles = getSampleStyleSheet()

    # Título
    title = f"Reporte de Salidas Peatonales"
    p_title = Paragraph(title, styles['h1'])
    elements.append(p_title)
    
    subtitle = f"Desde: {start_date}   Hasta: {end_date}"
    p_subtitle = Paragraph(subtitle, styles['h2'])
    elements.append(p_subtitle)
    elements.append(Spacer(1, 0.5*cm))

    # Datos de la tabla
    data = [["Fecha y Hora", "Estudiante", "Curso", "Puerta", "Operador"]]
    for log in logs:
        data.append([
            Paragraph(log.timestamp.astimezone(colombia_tz).strftime('%Y-%m-%d %I:%M %p'), styles['Normal']),
            Paragraph(log.student.name, styles['Normal']),
            Paragraph(log.student.course, styles['Normal']),
            Paragraph(log.door.name, styles['Normal']),
            Paragraph(log.operator.username, styles['Normal'])
        ])
        
    # Crear la tabla
    table = Table(data, colWidths=[4*cm, 5*cm, 2.5*cm, 3*cm, 3*cm])
    
    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0A2240")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])
    table.setStyle(style)
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer