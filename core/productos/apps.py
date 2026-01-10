"""
Configuración de la aplicación Productos.
"""

from django.apps import AppConfig


class ProductosConfig(AppConfig):
    """
    Clase de configuración para la aplicación Productos.
    """
    name = 'core.productos'
    label = 'core_productos'
    verbose_name = 'Gestión de Productos'

    def ready(self):
        """
        Importa las señales del módulo productos.
        """
        # pylint: disable=import-outside-toplevel, unused-import
        import core.productos.signals
