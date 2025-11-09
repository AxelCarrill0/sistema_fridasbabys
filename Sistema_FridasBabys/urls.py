from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('django.contrib.auth.urls')),

    path('', include('core.home.urls')),

    path('productos/', include('core.productos.urls', namespace='productos')),

    path('usuarios/', include('core.usuarios.urls', namespace='usuarios')),

    path('pedidos/', include('core.pedidos.urls', namespace='pedidos')),
]