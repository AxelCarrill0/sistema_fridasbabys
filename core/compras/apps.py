"""
Configuración de la aplicación Compras.
"""

from django.apps import AppConfig


class ComprasConfig(AppConfig):
    """
    Clase de configuración para la aplicación Compras.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.compras'
