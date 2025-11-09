from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home(request):
    if request.user.is_staff:
        # Staff/Admin
        return render(request, 'home/base.html')
    else:
        # Cliente
        return render(request, 'home/base_cliente.html')
