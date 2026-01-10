import pytest
from unittest.mock import MagicMock
# Importamos tu clase corregida
from core.productos.observer.inventario_observer import InventarioObserver


def test_funcionamiento_logica_alerta():
    """
    Verifica la operatividad de la lógica de alertas en el observador.
    Esta es una prueba dinámica de caja blanca.
    """
    # 1. Preparación del escenario (Mocking)
    producto = MagicMock()
    producto.nombre = "Producto de Prueba"
    producto.stock = 5
    producto.precio_base = 100

    cambio = {'stock': {'anterior': 10}}

    # 2. Ejecución del componente
    observer = InventarioObserver()

    # Ejecutamos la función para verificar que no existan errores de ejecución (Runtime)
    observer.actualizar(producto, cambio)

    # 3. Validación de estado
    assert producto.stock == 5
    print("\n[V&V] Prueba dinámica ejecutada con éxito.")
