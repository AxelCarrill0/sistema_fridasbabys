"""
Configuración del panel de administración para Productos.
"""

from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Configuración de la vista de administración de productos.
    """
    list_display = (
        'id', 'nombre', 'precio_base', 'ganancia', 'precio_final',
        'stock', 'categoria', 'activo'
    )
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria', 'activo')
