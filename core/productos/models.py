from django.db import models


class Producto(models.Model):
    # Opciones de categoría de producto
    CATEGORIAS = (
        ('ropa', 'Ropa de Bebé'),
        ('juguetes', 'Juguetes y Didácticos'),
        ('accesorios', 'Accesorios'),
        ('cuidado', 'Cuidado Personal'),
    )

    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")

    stock = models.IntegerField(default=0, verbose_name="Cantidad en Stock")

    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='accesorios', verbose_name="Categoría")

    activo = models.BooleanField(default=True, verbose_name="Activo")

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']