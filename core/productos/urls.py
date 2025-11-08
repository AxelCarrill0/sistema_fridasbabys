from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.listar_productos, name='lista'),
    path('crear/', views.crear_producto, name='crear'),

    path('<int:pk>/', views.detalle_producto, name='detalle'),

    path('editar/<int:pk>/', views.editar_producto, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar'),
]