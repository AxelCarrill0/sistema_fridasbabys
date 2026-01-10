"""
Rutas (URLs) de la aplicación Pagos.
"""

from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path(
        'seleccionar/<int:pago_id>/',
        views.seleccionar_metodo,
        name='seleccionar_metodo'
    ),
    path(
        'procesar/<int:pago_id>/',
        views.procesar_pago,
        name='procesar_pago'
    ),
    path(
        'detalle/<int:pago_id>/',
        views.detalle_pago,
        name='detalle_pago'
    ),
    path(
        'comprobante/<int:pago_id>/',
        views.descargar_comprobante,
        name='descargar_comprobante'
    ),
]
