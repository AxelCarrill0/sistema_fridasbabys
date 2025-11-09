from django.urls import path
from . import views

app_name = 'pedidos'  # 🔹 Importante para usar el namespace pedidos:

urlpatterns = [
    path('mis-pedidos/', views.lista_pedidos, name='lista_pedidos'),
]
