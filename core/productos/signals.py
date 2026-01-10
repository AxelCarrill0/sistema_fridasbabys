"""
Signals para la aplicación Productos.
Actualiza automáticamente el precio final cuando cambian precio_base o ganancia.
"""

from decimal import Decimal  # estándar
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Producto


@receiver(pre_save, sender=Producto)
def detectar_cambios_producto(sender, instance, **kwargs):
    """
    Detecta cambios en precio_base o ganancia de un Producto y actualiza precio_final.
    """
    if instance.pk:
        producto_anterior = Producto.objects.filter(pk=instance.pk).first()
        if producto_anterior:
            cambio_precio_base = producto_anterior.precio_base != instance.precio_base
            cambio_ganancia = producto_anterior.ganancia != instance.ganancia

            if cambio_precio_base or cambio_ganancia:
                instance.precio_final = (
                    instance.precio_base * (Decimal(1) + (instance.ganancia / 100))
                ).quantize(Decimal('0.01'))
                return

    # Si no hay producto anterior o no hubo cambio, recalcular siempre
    instance.precio_final = (
        instance.precio_base * (Decimal(1) + (instance.ganancia / 100))
    ).quantize(Decimal('0.01'))
