"""Vistas del módulo de usuarios: CRUD, autenticación y registro."""
import base64
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from core.pedidos.models import Pedido
from core.usuarios.models import Usuario
from core.usuarios.facade.usuario_facade import UsuarioFacade
from .forms import UsuarioCreationForm, UsuarioChangeForm, ClienteRegistrationForm
from django.http import JsonResponse
import json
facade = UsuarioFacade()

@login_required
def listar_usuarios(request):
    """Listar todos los usuarios."""
    usuarios = facade.listar_usuarios()
    return render(request, "usuarios/listar.html", {"usuarios": usuarios})

@login_required
def crear_usuario(request):
    """Crear un nuevo usuario."""
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("usuarios:lista")
    else:
        form = UsuarioCreationForm()
    return render(request, "usuarios/crear.html", {'form': form})


@login_required
def ver_perfil(request):
    if request.method == "POST":
        # Recogemos el texto de la imagen recortada
        img_data = request.POST.get('foto_perfil_base64')

        if img_data:
            # Separamos el encabezado del contenido base64
            format, imgstr = img_data.split(';base64,')
            ext = format.split('/')[-1]  # obtenemos jpg o png

            # Creamos el archivo de imagen para guardar en el modelo
            nombre_archivo = f"user_{request.user.id}_avatar.{ext}"
            file_data = ContentFile(base64.b64decode(imgstr), name=nombre_archivo)

            request.user.foto_perfil = file_data
            request.user.save()
            messages.success(request, "¡Foto ajustada y guardada correctamente!")
            return redirect('usuarios:perfil')

    return render(request, "usuarios/perfil.html", {"user": request.user})

@login_required
def verificar_password_ajax(request):
    """Verifica la contraseña para permitir cambios sensibles."""
    if request.method == "POST":
        data = json.loads(request.body)
        password = data.get('password')

        # El método check_password de Django es seguro [cite: 39]
        if request.user.check_password(password):
            return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)

@login_required
def editar_usuario(request, pk):
    """Editar un usuario existente."""
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            datos = form.cleaned_data
            nueva_password = datos.pop('password', None)
            facade.actualizar_usuario(pk, **datos)
            if nueva_password:
                usuario.set_password(nueva_password)
                usuario.save()
            return redirect("usuarios:lista")
    else:
        form = UsuarioChangeForm(instance=usuario)
    return render(request, "usuarios/editar.html", {"form": form, "usuario": usuario})

@login_required
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    pedidos_activos = Pedido.objects.filter(
        cliente=usuario,
        estado__in=["pendiente", "enviado"]
    )

    if pedidos_activos.exists():
        if pedidos_activos.filter(estado="enviado").exists():
            messages.error(
                request,
                "No se puede eliminar este usuario porque tiene pedidos sin entregar."
            )
        else:
            messages.error(
                request,
                "No se puede eliminar este usuario porque tiene pedidos pendientes."
            )
        return redirect("usuarios:lista")

    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect("usuarios:lista")

    return render(
        request,
        "usuarios/confirmar_eliminar.html",
        {"usuario": usuario}
    )


def login_view(request):
    """Vista para login de usuarios."""
    if request.user.is_authenticated:
        return redirect('home:home')

    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('home:home')
        error_message = "Usuario o contraseña incorrectos."
    return render(request, 'registration/login.html', {'error_message': error_message})

@login_required
def logout_view(request):
    """Cerrar sesión del usuario."""
    logout(request)
    return redirect('login')

def register_client(request):
    """Registrar nuevos usuarios con rol 'cliente'."""
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = ClienteRegistrationForm()
    return render(request, 'usuarios/registro.html', {'form': form})
