"""
Configuración del admin para la aplicación Usuarios.
Define la visualización y filtros de los usuarios en el panel de administración de Django.
"""

from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """
    Configuración de la clase Usuario en el admin.
    Define los campos visibles, filtros y campos de búsqueda.
    """
    list_display = ('username', 'nombre', 'email', 'telefono', 'rol')
    list_filter = ('rol',)
    search_fields = ('username', 'nombre', 'email')
