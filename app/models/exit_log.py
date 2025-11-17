from app import db
from datetime import datetime
import pytz

# Zona horaria de Colombia
colombia_tz = pytz.timezone('America/Bogota')

class ExitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(colombia_tz))
    
    student_id = db.Column(db.String(10), db.ForeignKey('student.id'), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    door_id = db.Column(db.Integer, db.ForeignKey('door.id'), nullable=False)
    
    # Relaciones para acceder a los objetos completos
    student = db.relationship('Student', backref=db.backref('exit_logs', lazy=True))
    operator = db.relationship('User', backref=db.backref('exit_logs', lazy=True))
    door = db.relationship('Door', backref=db.backref('exit_logs', lazy=True))

    # --- NUEVA PROPIEDAD ---
    @property
    def local_timestamp(self):
        """Devuelve el timestamp en la zona horaria de Colombia."""
        return self.timestamp.astimezone(colombia_tz)

    def __repr__(self):
        return f'<ExitLog {self.student.name} at {self.timestamp}>'