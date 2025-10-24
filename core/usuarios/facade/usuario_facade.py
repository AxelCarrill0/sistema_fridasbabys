from core.usuarios.models import Usuario
from core.usuarios.factory.usuario_factory import UsuarioFactory

class UsuarioFacade:
    """
    Patrón Facade.
    Centraliza las operaciones CRUD de usuarios.
    """
    def crear_usuario(self, nombre, correo, telefono, direccion, rol="cliente"):
        return UsuarioFactory.crear_usuario(nombre, correo, telefono, direccion, rol)

    def listar_usuarios(self):
        return Usuario.objects.all()

    def obtener_usuario(self, id_usuario):
        return Usuario.objects.get(id=id_usuario)

    def actualizar_usuario(self, id_usuario, **datos):
        usuario = Usuario.objects.get(id=id_usuario)
        for campo, valor in datos.items():
            setattr(usuario, campo, valor)
        usuario.save()
        return usuario

    def eliminar_usuario(self, id_usuario):
        usuario = Usuario.objects.get(id=id_usuario)
        usuario.delete()