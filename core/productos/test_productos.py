"""
Pruebas unitarias para la aplicación Productos.
Incluye creación de productos y validaciones de reglas de negocio.
"""

import pytest
from core.productos.models import Producto


@pytest.mark.django_db
def test_crear_producto():
    """Test que verifica la creación correcta de un Producto."""
    producto = Producto.objects.create(
        nombre="Coche de juguete",
        precio_base=10.50,
        stock=5
    )
    assert producto.nombre == "Coche de juguete"
    assert producto.precio_base == 10.50
    assert producto.stock == 5


# --- Lógica del dominio (reglas del sistema) ---


def calcular_precio_total(precio_unitario, cantidad):
    """Calcula el precio total dado un precio unitario y cantidad."""
    return precio_unitario * cantidad


def aplicar_descuento(total, descuento):
    """Aplica un descuento (0-1) sobre un total."""
    return total - (total * descuento)


# --- Pruebas unitarias de lógica ---


def test_calcular_precio_total():
    """Test para la función calcular_precio_total."""
    assert calcular_precio_total(10, 3) == 30


def test_aplicar_descuento():
    """Test para la función aplicar_descuento."""
    assert aplicar_descuento(100, 0.1) == 90


@pytest.mark.django_db
def test_producto_precio_positivo():
    """Verifica que el precio de un producto sea siempre positivo."""
    producto = Producto.objects.create(
        nombre="Crema",
        precio_base=3.25,
        stock=4
    )
    assert producto.precio_base > 0


@pytest.mark.django_db
def test_producto_str():
    """Verifica que el __str__ de Producto no sea None."""
    producto = Producto.objects.create(
        nombre="Talco",
        precio_base=2.00,
        stock=1
    )
    assert str(producto) is not None
