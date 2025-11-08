from core.productos.models import Producto
from core.productos.factory.producto_factory import ProductoFactory
from core.productos.observer.producto_observador import subject_producto
from core.productos.observer.inventario_observer import InventarioObserver
from django.db.models import Q


class ProductoFacade:

    def __init__(self):
        subject_producto.adjuntar(InventarioObserver())

    def listar_productos(self, query=None):
        queryset = Producto.objects.all()

        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) |
                Q(categoria__icontains=query) |
                Q(precio__icontains=query)
            )

        return queryset.order_by('id')

    def crear_producto(self, **datos):
        return ProductoFactory.crear_producto(**datos)

    def obtener_producto(self, id_producto):
        return Producto.objects.get(id=id_producto)

    def actualizar_producto(self, id_producto, **datos):
        producto = self.obtener_producto(id_producto)
        for key, value in datos.items():
            setattr(producto, key, value)
        producto.save()
        return producto

    def eliminar_producto(self, id_producto):
        producto = self.obtener_producto(id_producto)
        producto.delete()