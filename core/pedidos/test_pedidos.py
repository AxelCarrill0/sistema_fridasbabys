"""
Tests de la aplicación Pedidos.
Verifica la creación y los estados de los pedidos.
"""

import pytest
from django.contrib.auth import get_user_model
from core.productos.models import Producto
from core.pedidos.models import Pedido
from core.usuarios.models import Usuario

User = get_user_model()


@pytest.mark.django_db
def test_crear_pedido_pendiente():
    """Verifica que un pedido nuevo se cree con estado 'pendiente'."""
    cliente = User.objects.create_user(
        username="cliente_pedido",
        password="12345",
        rol="cliente"
    )
    producto = Producto.objects.create(
        nombre="Muñeca",
        precio_base=15,
        stock=10
    )
    pedido = Pedido.objects.create(
        cliente=cliente,
        producto=producto,
        cantidad=2
    )
    assert pedido.estado == "pendiente"


def test_ejemplo_basico():
    """Test de ejemplo simple."""
    assert True


def pedido_activo(estado):
    """Función auxiliar que verifica si un pedido está activo."""
    return estado == "activo"


def test_pedido_activo():
    """Verifica que un pedido activo sea detectado correctamente."""
    assert pedido_activo("activo") is True


def test_pedido_inactivo():
    """Verifica que un pedido no activo sea detectado correctamente."""
    assert pedido_activo("cancelado") is False


@pytest.mark.django_db
def test_pedido_estado_enviado():
    """Verifica que un pedido pueda tener estado 'enviado'."""
    cliente = Usuario.objects.create_user(
        username="cliente_envio",
        password="123",
        rol="cliente"
    )
    producto = Producto.objects.create(
        nombre="Leche",
        precio_base=1.50,
        stock=10
    )
    pedido = Pedido.objects.create(
        cliente=cliente,
        producto=producto,
        cantidad=1,
        estado="enviado"
    )
    assert pedido.estado == "enviado"


@pytest.mark.django_db
def test_pedido_tiene_cliente():
    """Verifica que un pedido tenga un cliente asociado."""
    cliente = Usuario.objects.create_user(
        username="cliente_test2",
        password="123",
        rol="cliente"
    )
    producto = Producto.objects.create(
        nombre="Juguete",
        precio_base=6,
        stock=3
    )
    pedido = Pedido.objects.create(
        cliente=cliente,
        producto=producto,
        cantidad=1,
        estado="pendiente"
    )
    assert pedido.cliente is not None
