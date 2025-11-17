import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask.cli import with_appcontext
from getpass import getpass # Usaremos getpass para una mejor compatibilidad
from app import db
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.door import Door

# Creamos un grupo de comandos para organizarnos mejor
@click.group()
def admin():
    """Comandos de administración."""
    pass

@admin.command("create")
@with_appcontext
def create_admin():
    """Crea el usuario administrador inicial de forma interactiva."""
    # 1. Verificar si el admin ya existe
    if User.query.filter_by(role=UserRole.ADMIN).first():
        click.secho("Ya existe al menos un usuario administrador.", fg="yellow")
        return

    click.echo("Creando cuenta de administrador inicial...")
    
    # 2. Solicitar datos de forma interactiva
    username = click.prompt(
        click.style("Nombre de usuario", fg="cyan"), 
        default="admin", 
        show_default=True
    )
    email = click.prompt(click.style("Email", fg="cyan"))
    
    # 3. Solicitar contraseña de forma segura
    password = click.prompt(
        click.style("Contraseña", fg="cyan"), 
        hide_input=True, 
        confirmation_prompt=click.style("Repetir contraseña", fg="cyan")
    )

    # 4. Validar que los campos no estén vacíos
    if not all([username, email, password]):
        click.secho("El nombre de usuario, email y contraseña no pueden estar vacíos.", fg="red")
        return

    # 5. Crear el usuario
    admin_user = User(
        username=username,
        email=email,
        role=UserRole.ADMIN
    )
    admin_user.set_password(password)

    db.session.add(admin_user)
    db.session.commit()

    click.secho(f"¡Usuario administrador '{username}' creado exitosamente!", fg="green")

@admin.command("migrate-sqlite-to-mysql")
@with_appcontext
def migrate_data():
    """Migra datos de usuarios, puertas y estudiantes desde SQLite a la BD actual."""
    click.echo("Iniciando migración de datos desde SQLite...")

    # 1. Conexión a la antigua base de datos SQLite
    sqlite_engine = create_engine('sqlite:///school_exit_control.db')
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SQLiteSession()

    # 2. Leer todos los datos de SQLite
    click.echo("Leyendo datos desde SQLite...")
    users = sqlite_session.query(User).all()
    doors = sqlite_session.query(Door).all()
    students = sqlite_session.query(Student).all()

    # 3. Insertar en la nueva base de datos (MySQL)
    try:
        # Usuarios
        for user in users:
            new_user = User(id=user.id, username=user.username, email=user.email, password_hash=user.password_hash, role=user.role)
            db.session.merge(new_user)
        click.echo(f"Procesados {len(users)} usuarios.")
        
        # Puertas
        for door in doors:
            new_door = Door(id=door.id, name=door.name, status=door.status)
            db.session.merge(new_door)
        click.echo(f"Procesados {len(doors)} puertas.")

        # Estudiantes
        for student in students:
            new_student = Student(id=student.id, name=student.name, course=student.course, 
                                  authorized_to_leave=student.authorized_to_leave, photo=student.photo, 
                                  qr_code_data=student.qr_code_data)
            db.session.merge(new_student)
        click.echo(f"Procesados {len(students)} estudiantes.")

        # 4. Confirmar la transacción
        db.session.commit()
        click.secho("¡Migración de datos completada exitosamente!", fg="green")

    except Exception as e:
        db.session.rollback()
        click.secho(f"Error durante la migración: {e}", fg="red")
    finally:
        sqlite_session.close()

# Esta función la usaremos para registrar el grupo de comandos
def register_commands(app):
    app.cli.add_command(admin)