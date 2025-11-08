from django.contrib import admin


from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'activo', 'fecha_actualizacion')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre', 'descripcion')