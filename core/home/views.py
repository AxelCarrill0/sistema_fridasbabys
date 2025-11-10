from django.shortcuts import render

def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return render(request, 'home/base.html')
        else:
            return render(request, 'home/base_cliente.html')
    else:
        return render(request, 'home/home.html')
