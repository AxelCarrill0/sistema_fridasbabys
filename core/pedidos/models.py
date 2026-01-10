"""
Modelos de la aplicación Pedidos.
"""

from django.db import models
from core.productos.models import Producto
from core.usuarios.models import Usuario
from core.pagos.models import Pago


class Pedido(models.Model):
    """
    Representa un pedido realizado por un cliente, con información
    del producto, cantidad, estado y pago asociado.
    """
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    )

    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name="Cliente"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        verbose_name="Producto"
    )
    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad"
    )
    fecha_pedido = models.DateField(
        auto_now_add=True
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente',
        verbose_name="Estado"
    )
    pago = models.ForeignKey(
        Pago,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos',
        verbose_name="Pago"
    )

    def __str__(self):
        return f"Pedido de {self.cliente} - {self.producto} ({self.estado})"

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido']
