"""
Rutas (URLs) de la aplicación Compras.
"""

from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('', views.listar_compras, name='lista'),
    path('confirmar/<int:pk>/', views.confirmar_compra_staff, name='confirmar'),
]
