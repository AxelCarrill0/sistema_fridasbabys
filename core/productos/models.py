"""
Modelos de la aplicación Productos.
"""

from decimal import Decimal
from django.db import models
from core.usuarios.models import Usuario


class Producto(models.Model):
    """
    Modelo que representa un producto disponible en la tienda.
    """
    CATEGORIAS = (
        ('ropa', 'Ropa de Bebé'),
        ('juguetes', 'Juguetes y Didácticos'),
        ('accesorios', 'Accesorios'),
        ('cuidado', 'Cuidado Personal'),
        ('Zapatos y Zapatillas', 'calzado'),
    )

    nombre = models.CharField(
        max_length=150, unique=True, verbose_name="Nombre del Producto"
    )
    descripcion = models.TextField(
        blank=True, null=True, verbose_name="Descripción"
    )
    precio_base = models.DecimalField(
        max_digits=10, decimal_places=2, default=1, verbose_name="Precio compra"
    )
    ganancia = models.DecimalField(
        max_digits=5, decimal_places=2, default=20, verbose_name="Ganancia %"
    )
    precio_final = models.DecimalField(
        max_digits=10, decimal_places=2, default=1, verbose_name="Precio venta"
    )
    imagen = models.ImageField(
        upload_to='productos/', null=True, blank=True, verbose_name="Imagen del Producto"
    )
    stock = models.IntegerField(
        default=0, verbose_name="Cantidad en Stock"
    )
    categoria = models.CharField(
        max_length=20, choices=CATEGORIAS, default='accesorios', verbose_name="Categoría"
    )
    activo = models.BooleanField(
        default=True, verbose_name="Activo"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Creado por"
    )

    def __str__(self):
        return (
            f"{self.nombre} | Precio final: ${self.precio_final} | Stock: {self.stock}"
        )

    def calcular_precio_final(self):
        """
        Calcula el precio final del producto usando el precio base y porcentaje de ganancia.
        """
        return (
            self.precio_base * (1 + (self.ganancia / 100))
        ).quantize(Decimal("0.01"))

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
