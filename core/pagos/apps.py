"""
Configuración de la aplicación Pagos.
"""

from django.apps import AppConfig


class PagosConfig(AppConfig):
    """
    Clase de configuración para la aplicación Pagos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.pagos'
