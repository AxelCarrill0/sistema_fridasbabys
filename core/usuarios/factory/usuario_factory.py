from core.usuarios.models import Usuario

class UsuarioFactory:

    @staticmethod
    def crear_usuario(**datos):

        if 'username' not in datos or 'password' not in datos:
            raise ValueError("Se requieren 'username' y 'password' para crear un usuario.")

        usuario = Usuario.objects.create_user(
            username=datos.pop('username'),
            password=datos.pop('password'),
            **datos  # Esta parte indica que los otros campos o atributos de la tabla se
                     # extraen del metodo de Django
        )

        return usuario
