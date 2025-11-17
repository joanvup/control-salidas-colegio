import uuid
from app import db

class Student(db.Model):
    id = db.Column(db.String(10), primary_key=True) # ID del estudiante (ej. carnet)
    name = db.Column(db.String(128), nullable=False)
    course = db.Column(db.String(64), nullable=False)
    authorized_to_leave = db.Column(db.Boolean, default=False, nullable=False)
    photo = db.Column(db.String(128), nullable=True) # Ruta a la foto
    qr_code_data = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    def __repr__(self):
        return f'<Student {self.name}>'