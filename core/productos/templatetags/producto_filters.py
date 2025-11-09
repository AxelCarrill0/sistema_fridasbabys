from django import template
from core.productos.decorator.producto_decorator import ProductoComponent, DescuentoPorcentajeDecorator
from decimal import Decimal

register = template.Library()

@register.filter
def producto_component(producto):
    componente = ProductoComponent(producto)
    porcentaje_descuento = getattr(producto, 'descuento', 0)
    if porcentaje_descuento > 0:
        componente = DescuentoPorcentajeDecorator(componente, Decimal(porcentaje_descuento))
    return componente

@register.filter
def get_precio_final(componente):
    return componente.get_precio_final()
