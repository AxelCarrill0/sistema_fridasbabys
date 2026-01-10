"""
Configuración de la aplicación Usuarios.
Define la configuración principal de la app para Django.
"""

from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    """
    Configuración de la clase AppConfig para Usuarios.
    Define el nombre y el tipo de campo por defecto para la base de datos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.usuarios'
