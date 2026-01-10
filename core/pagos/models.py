"""
Modelos de la aplicación Pagos.
"""

from django.db import models
from core.usuarios.models import Usuario


class Pago(models.Model):
    """
    Representa un pago realizado por un usuario, incluyendo
    método de pago, estado y fechas de creación y pago.
    """
    METODO_PAGO_CHOICES = (
        ('tarjeta', 'Tarjeta de crédito'),
        ('transferencia', 'Transferencia'),
    )

    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='pagos',
        verbose_name="Usuario"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total"
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        verbose_name="Método de pago"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    fecha_pago = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de pago"
    )
    foto_verificacion = models.ImageField(
        upload_to='verificaciones/',
        null=True,
        blank=True,
        verbose_name="Foto de Verificación"
    )

    def __str__(self):
        return f"Pago #{self.id} - {self.usuario} - {self.estado}"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_creacion']
