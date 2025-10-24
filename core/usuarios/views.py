from django.shortcuts import render, redirect, get_object_or_404
from core.usuarios.facade.usuario_facade import UsuarioFacade
from core.usuarios.models import Usuario

facade = UsuarioFacade()

def listar_usuarios(request):
    usuarios = facade.listar_usuarios()
    return render(request, "usuarios/listar.html", {"usuarios": usuarios})

def crear_usuario(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        correo = request.POST["correo"]
        telefono = request.POST["telefono"]
        direccion = request.POST["direccion"]
        rol = request.POST.get("rol", "cliente")

        facade.crear_usuario(nombre, correo, telefono, direccion, rol)
        return redirect("usuarios:lista")

    return render(request, "usuarios/crear.html")

def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        usuario.nombre = request.POST.get("nombre")
        usuario.correo = request.POST.get("correo")
        usuario.telefono = request.POST.get("telefono")
        usuario.direccion = request.POST.get("direccion")
        usuario.rol = request.POST.get("rol")
        usuario.save()
        return redirect("usuarios:lista")

    return render(request, "usuarios/editar.html", {"usuario": usuario})

def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.delete()
    return redirect("usuarios:lista")
