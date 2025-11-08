# INTERFAZ DEL OBSERVADOR
class ProductoObserver:
    """
    Define la interfaz para los objetos observadores.
    Todos los observadores concretos deben implementar este método.
    """
    def actualizar(self, producto, cambio):

        raise NotImplementedError


# SUJETO OBSERVABLE
class ProductoSubject:
    """
    Mantiene una lista de observadores y tiene métodos para adjuntar,
    desadjuntar y notificar a los observadores.
    """
    _observadores = []

    def adjuntar(self, observador: ProductoObserver):
        """Adjunta un observador a la lista."""
        if observador not in self._observadores:
            self._observadores.append(observador)

    def desadjuntar(self, observador: ProductoObserver):
        """Desadjunta un observador de la lista."""
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, producto, cambio):
        """Notifica a todos los observadores sobre un cambio."""
        for observador in self._observadores:
            observador.actualizar(producto, cambio)

subject_producto = ProductoSubject()