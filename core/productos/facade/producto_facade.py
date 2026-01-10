from core.productos.models import Producto
from core.productos.factory.producto_factory import ProductoFactory
from core.productos.observer.producto_observador import subject_producto
from core.productos.observer.inventario_observer import InventarioObserver
from django.db.models import Q


class ProductoFacade:

    def __init__(self):
        if not subject_producto._observadores:
            subject_producto.adjuntar(InventarioObserver())

    def listar_productos(self, query=None):
        queryset = Producto.objects.all()

        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) |
                Q(categoria__icontains=query) |
                Q(precio_base__icontains=query)
            )

        return queryset.order_by('id')

    def crear_producto(self, creado_por=None, **datos):

        return ProductoFactory.crear_producto(creado_por=creado_por, **datos)

    def obtener_producto(self, id_producto):
        return Producto.objects.get(id=id_producto)

    def actualizar_producto(self, id_producto, **datos):
        producto = self.obtener_producto(id_producto)

        stock_anterior = producto.stock
        precio_anterior = producto.precio_base

        for key, value in datos.items():
            setattr(producto, key, value)

        producto.save()

        cambios = {}
        if 'stock' in datos and datos['stock'] != stock_anterior:
            cambios['stock'] = {'anterior': stock_anterior}

        if 'precio_base' in datos and datos['precio_base'] != precio_anterior:
            cambios['precio'] = {'anterior': precio_anterior}

        if cambios:
            subject_producto.notificar(producto, cambios)

        return producto

    def eliminar_producto(self, id_producto):
        producto = self.obtener_producto(id_producto)

        if producto.pedido_set.exists():
            raise Exception("No se puede eliminar el producto. Está relacionado con uno o más pedidos existentes.")

        producto.delete()
        return True