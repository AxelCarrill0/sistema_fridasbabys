import decimal
from ..models import Producto


class ProductoComponente:
    """Define la interfaz para los objetos que pueden tener funcionalidad añadida."""

    def get_precio_base(self):
        raise NotImplementedError

    def get_precio_final(self):
        raise NotImplementedError


class ProductoComponent(ProductoComponente):

    def __init__(self, producto: Producto):
        self._producto = producto

    def get_precio_base(self):
        return self._producto.precio

    def get_precio_final(self):
        return self._producto.precio


class ProductoDecorator(ProductoComponente):

    def __init__(self, componente: ProductoComponente):
        self._componente = componente

    def get_precio_base(self):
        return self._componente.get_precio_base()


class DescuentoPorcentajeDecorator(ProductoDecorator):

    def __init__(self, componente: ProductoComponente, porcentaje_descuento: decimal.Decimal):
        super().__init__(componente)
        self._porcentaje_descuento = porcentaje_descuento

    def get_precio_final(self):
        precio_base = decimal.Decimal(str(self.get_precio_base()))  # Convierte float a Decimal si es necesario
        factor_descuento = (decimal.Decimal('100') - self._porcentaje_descuento) / decimal.Decimal('100')
        precio_con_descuento = precio_base * factor_descuento

        return precio_con_descuento.quantize(decimal.Decimal('0.01'))