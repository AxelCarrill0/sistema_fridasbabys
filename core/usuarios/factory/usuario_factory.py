from core.usuarios.models import Usuario

class UsuarioFactory:
    """
    Crea usuarios según su rol usando el patrón Factory Method.
    """
    @staticmethod
    def crear_usuario(nombre, correo, telefono, direccion, rol="cliente"):
        # Crea el usuario directamente
        usuario = Usuario(
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            direccion=direccion,
            rol=rol
        )
        usuario.save()
        return usuario
