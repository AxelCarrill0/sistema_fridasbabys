from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):

    list_display = ('username', 'nombre', 'email', 'telefono', 'rol')

    list_filter = ('rol',)

    search_fields = ('username', 'nombre', 'email')