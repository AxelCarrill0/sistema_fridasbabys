"""
Módulo de observador para la gestión de inventario en FridasBabys.
Provee la lógica para monitorear cambios en stock y precios de productos.
"""
import logging
from .producto_observador import ProductoObserver

# Constantes de configuración para el logger y alertas
LOGGER = logging.getLogger(__name__)
UMBRAL_STOCK_CRITICO = 5

class InventarioObserver(ProductoObserver):
    """
    Clase observadora que reacciona a variaciones en el inventario.
    """

    def actualizar(self, producto, cambio):
        """
        Procesa las actualizaciones de stock y precio de un producto.
        """
        # Verificación de cambios en el inventario
        if 'stock' in cambio:
            self._verificar_existencias(producto, cambio['stock']['anterior'])

        # Verificación de cambios en el precio
        if 'precio' in cambio:
            self._verificar_costos(producto, cambio['precio']['anterior'])

    def _verificar_existencias(self, producto, stock_previo):
        """
        Evalúa si el stock ha bajado de los niveles permitidos.
        """
        stock_actual = producto.stock
        if stock_actual <= UMBRAL_STOCK_CRITICO and stock_previo > UMBRAL_STOCK_CRITICO:
            LOGGER.warning(
                "[ALERTA] Producto '%s' en nivel crítico: %d unidades.",
                producto.nombre, stock_actual
            )
        elif stock_actual > stock_previo:
            LOGGER.info(
                "[INVENTARIO] '%s' aumentó de %d a %d unidades.",
                producto.nombre, stock_previo, stock_actual
            )

    def _verificar_costos(self, producto, precio_previo):
        """
        Con esta funcion registramos los cambios de precio para historial de auditoría.
        """
        precio_actual = producto.precio_base
        LOGGER.info(
            "[AUDITORÍA] '%s' cambió precio: de $%s a $%s.",
            producto.nombre, precio_previo, precio_actual
        )