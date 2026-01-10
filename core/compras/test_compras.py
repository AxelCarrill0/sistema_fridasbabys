"""
Pruebas unitarias para la aplicación Compras.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.usuarios.models import Usuario

User = get_user_model()


@pytest.mark.django_db
def test_acceso_compras_admin(client):
    """
    Verifica que un usuario admin pueda acceder a la lista de compras.
    """
    admin = User.objects.create_user(
        username="admin_test",
        password="12345",
        rol="admin",
        is_staff=True
    )
    client.login(username="admin_test", password="12345")
    url = reverse("compras:lista")
    response = client.get(url)
    assert response.status_code == 200


def test_ejemplo_basico():
    """
    Prueba de ejemplo básica.
    """
    assert True


@pytest.mark.django_db
def test_compras_no_logueado_redirige(client):
    """
    Verifica que un usuario no autenticado sea redirigido.
    """
    url = reverse("compras:lista")
    response = client.get(url)
    assert response.status_code in [301, 302]


@pytest.mark.django_db
def test_compras_usuario_sin_permiso(client):
    """
    Verifica que un usuario sin permisos sea redirigido.
    """
    cliente = Usuario.objects.create_user(
        username="cliente_test",
        password="123",
        rol="cliente"
    )
    client.login(username="cliente_test", password="123")
    url = reverse("compras:lista")
    response = client.get(url)
    assert response.status_code == 302
