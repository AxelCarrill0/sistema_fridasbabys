from django.shortcuts import render



def home(request):
    # 1. VERIFICAR si el usuario está autenticado
    if request.user.is_authenticated:
        # Si está autenticado, el usuario debe ver su DASHBOARD (Panel de Control)

        # Ojo: Si 'base.html' y 'base_cliente.html' solo son plantillas base
        # y no contienen el HTML completo de los dashboards, deberás crear
        # y renderizar plantillas como 'home/dashboard_admin.html' o
        # 'home/dashboard_cliente.html'.

        if request.user.is_staff:
            # Usuario Staff/Admin: Lo redirigimos a su panel
            return render(request, 'home/base.html')
        else:
            # Usuario Cliente: Lo redirigimos a su panel
            return render(request, 'home/base_cliente.html')

    # 2. Si NO está autenticado, mostramos la PÁGINA DE INICIO PÚBLICA
    else:
        return render(request, 'home/home.html')