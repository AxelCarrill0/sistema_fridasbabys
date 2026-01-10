"""
Vistas de la aplicación Home.
"""

from django.shortcuts import render


def home(request):
    """
    Renderiza la página principal según el tipo de usuario:
    - Admin: dashboard_admin.html
    - Cliente autenticado: dashboard_cliente.html
    - No autenticado: home.html
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return render(request, 'home/dashboard_admin.html')
        return render(request, 'home/dashboard_cliente.html')

    return render(request, 'home/home.html')
