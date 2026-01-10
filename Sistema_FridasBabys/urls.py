from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('django.contrib.auth.urls')),

    path('', include('core.home.urls')),

    path('productos/', include('core.productos.urls', namespace='productos')),

    path('usuarios/', include('core.usuarios.urls', namespace='usuarios')),

    path('pedidos/', include('core.pedidos.urls', namespace='pedidos')),
    path('compras/', include('core.compras.urls', namespace='compras')),

    path('pagos/', include('core.pagos.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)