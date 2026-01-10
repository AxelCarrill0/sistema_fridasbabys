# INTERFAZ DEL OBSERVADOR
class ProductoObserver:

    def actualizar(self, producto, cambio):

        raise NotImplementedError

class ProductoSubject:

    _observadores = []

    def adjuntar(self, observador: ProductoObserver):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def desadjuntar(self, observador: ProductoObserver):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, producto, cambio):
        for observador in self._observadores:
            observador.actualizar(producto, cambio)

subject_producto = ProductoSubject()