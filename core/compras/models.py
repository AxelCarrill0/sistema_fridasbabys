from django.db import models
from core.productos.models import Producto
from core.usuarios.models import Usuario

class Compra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    fecha_compra = models.DateField(auto_now_add=True)
    realizado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Staff que realizó la compra")

    def __str__(self):
        return f"Compra de {self.cantidad} {self.producto} por {self.realizado_por}"

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-fecha_compra']
