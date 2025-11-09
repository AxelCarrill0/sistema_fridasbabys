from django.shortcuts import render, redirect, get_object_or_404
from core.usuarios.facade.usuario_facade import UsuarioFacade
from core.usuarios.models import Usuario
from django.contrib.auth.decorators import login_required
from .forms import UsuarioCreationForm, UsuarioChangeForm, ClienteRegistrationForm
from django.contrib.auth import authenticate, login, logout

facade = UsuarioFacade()


@login_required
def listar_usuarios(request):
    usuarios = facade.listar_usuarios()
    return render(request, "usuarios/listar.html", {"usuarios": usuarios})


@login_required
def crear_usuario(request):
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("usuarios:lista")
    else:
        form = UsuarioCreationForm()

    return render(request, "usuarios/crear.html", {'form': form})


@login_required
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            datos = form.cleaned_data

            nueva_password = datos.pop('password', None)

            # Actualizamos el resto de los campos mediante el Facade para mantener el patrón

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

    if request.method == "POST":
        facade.eliminar_usuario(pk)
        return redirect("usuarios:lista")

    return render(request, "usuarios/confirmar_eliminar.html", {"usuario": usuario})

# esta parte es referente al proceso de autenticacion
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home:home')
        else:
            error_message = "Usuario o contraseña incorrectos."
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

#con esta vista registramos  nuevos usuarios con rol 'cliente'.
def register_client(request):

    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Opcional: Autenticar e iniciar sesión al nuevo cliente automáticamente
            # login(request, user)
            return redirect('login')
    else:
        form = ClienteRegistrationForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        # Redirigir según rol
        if request.user.is_staff:
            return redirect('home:home')       # Admin o staff
        else:
            return redirect('home:cliente_home')  # Cliente

    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('home:home')
            else:
                return redirect('home:cliente_home')
        else:
            error_message = "Usuario o contraseña incorrectos."

    return render(request, 'usuarios/../../templates/registration/login.html', {'error_message': error_message})
