
from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('mis-pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('agregar/', views.agregar_a_pedido, name='agregar_a_pedido'),
    path('editar/<int:pedido_id>/', views.editar_pedido, name='editar_pedido'),
    path('cancelar/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),

    path('confirmar-compra/', views.confirmar_compra, name='confirmar_compra'),

]