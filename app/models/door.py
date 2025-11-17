from app import db
import enum

class DoorStatus(enum.Enum):
    OPEN = 'Abierta'
    CLOSED = 'Cerrada'

class Door(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.Enum(DoorStatus), default=DoorStatus.CLOSED, nullable=False)

    def __repr__(self):
        return f'<Door {self.name}>'