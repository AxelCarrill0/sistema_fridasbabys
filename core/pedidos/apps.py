"""
Configuración de la aplicación Pedidos.
"""

from django.apps import AppConfig


class PedidosConfig(AppConfig):
    """
    Clase de configuración para la aplicación Pedidos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.pedidos'
