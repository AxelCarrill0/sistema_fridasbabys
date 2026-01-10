"""
Configuración de la aplicación Home.
"""

from django.apps import AppConfig


class HomeConfig(AppConfig):
    """
    Clase de configuración para la aplicación Home.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.home'
