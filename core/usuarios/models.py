"""
Modelo de usuario extendido para el sistema.
Incluye campos adicionales como nombre, teléfono, dirección y rol.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    """
    Extensión del modelo AbstractUser para agregar información
    adicional y rol de usuario en el sistema.
    """
    ROLES = (
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    )
    nombre = models.CharField(max_length=100)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')

    def __str__(self):
        return f"{self.username} ({self.rol})"