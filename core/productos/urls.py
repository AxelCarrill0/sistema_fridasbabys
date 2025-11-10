from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('gestionar/', views.listar_productos, name='lista'),
    path('crear/', views.crear_producto, name='crear'),
    path('editar/<int:pk>/', views.editar_producto, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar'),

    path('catalogo/', views.catalogo_productos, name='catalogo'),
    path('detalle/<int:pk>/', views.detalle_producto, name='detalle'),
    path('subir-imagen/<int:pk>/', views.subir_imagen, name='subir_imagen'),

]