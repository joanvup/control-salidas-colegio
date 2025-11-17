from app import create_app, db

def test_login_page():
    """
    Prueba que la página de inicio de sesión se cargue correctamente.
    """
    flask_app = create_app()
    with flask_app.test_client() as test_client:
        response = test_client.get('/auth/login')
        assert response.status_code == 200
        assert b"Iniciar Sesi\xc3\xb3n" in response.data # "Iniciar Sesión" en bytes

def test_unauthenticated_access():
    """
    Prueba que un usuario no autenticado sea redirigido al intentar acceder al dashboard.
    """
    flask_app = create_app()
    with flask_app.test_client() as test_client:
        response = test_client.get('/', follow_redirects=True)
        assert response.status_code == 200
        assert b"Por favor, inicie sesi\xc3\xb3n" in response.data # "Por favor, inicie sesión"