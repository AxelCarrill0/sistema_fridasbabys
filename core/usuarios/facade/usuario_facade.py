from core.usuarios.models import Usuario
from core.usuarios.factory.usuario_factory import UsuarioFactory
class UsuarioFacade:

    """
    Patrón Facade.
    Centraliza las operaciones CRUD de usuarios.
    """

    def crear_usuario(self, **datos):
        return UsuarioFactory.crear_usuario(**datos)

    def listar_usuarios(self):
        return Usuario.objects.all()

    def obtener_usuario(self, id_usuario):
        return Usuario.objects.get(id=id_usuario)

    def actualizar_usuario(self, id_usuario, **datos):
        usuario = Usuario.objects.get(id=id_usuario)

        if 'password' in datos and datos['password']:
            usuario.set_password(datos.pop('password'))
        for campo, valor in datos.items():
            setattr(usuario, campo, valor)

        usuario.save()
        return usuario

    def eliminar_usuario(self, id_usuario):
        usuario = Usuario.objects.get(id=id_usuario)
        usuario.delete()