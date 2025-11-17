from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional
from app.models.user import User, UserRole
from app.models.door import DoorStatus
from app.models.student import Student

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(message="El usuario es requerido.")])
    password = PasswordField('Contraseña', validators=[DataRequired(message="La contraseña es requerida.")])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(message="El usuario es requerido.")])
    email = StringField('Email', validators=[DataRequired(message="El email es requerido."), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(message="La contraseña es requerida.")])
    password2 = PasswordField(
        'Repetir Contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas no coinciden.')])
    role = SelectField('Rol', choices=[(role.name, role.value) for role in UserRole], validators=[DataRequired()])
    submit = SubmitField('Registrar Usuario')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Este nombre de usuario ya está en uso.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Este email ya está registrado.')
        
class StudentForm(FlaskForm):
    id = StringField('ID Estudiante (Carnet)', validators=[DataRequired()])
    name = StringField('Nombre Completo', validators=[DataRequired()])
    course = StringField('Curso', validators=[DataRequired()])
    authorized_to_leave = BooleanField('Autorizado para Salir Solo')
    photo = FileField('Foto del Estudiante', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], '¡Solo imágenes!')
    ])
    submit = SubmitField('Guardar Estudiante')
    
    def __init__(self, original_id=None, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.original_id = original_id

    def validate_id(self, id):
        if id.data != self.original_id:
            student = Student.query.filter_by(id=id.data).first()
            if student:
                raise ValidationError('Este ID de estudiante ya existe. Por favor, use otro.')


class DoorForm(FlaskForm):
    name = StringField('Nombre de la Puerta', validators=[DataRequired()])
    status = SelectField('Estado', choices=[(status.name, status.value) for status in DoorStatus], validators=[DataRequired()])
    submit = SubmitField('Guardar Puerta')

class ImportStudentsForm(FlaskForm):
    excel_file = FileField(
        'Archivo Excel (.xlsx)',
        validators=[
            FileRequired(message="Por favor, selecciona un archivo."),
            FileAllowed(['xlsx'], '¡Solo se permiten archivos .xlsx!')
        ]
    )
    submit = SubmitField('Importar Estudiantes')

class UploadPhotosForm(FlaskForm):
    zip_file = FileField(
        'Archivo ZIP (.zip)',
        validators=[
            FileRequired(message="Por favor, selecciona un archivo."),
            FileAllowed(['zip'], '¡Solo se permiten archivos .zip!')
        ]
    )
    submit = SubmitField('Cargar Fotos')