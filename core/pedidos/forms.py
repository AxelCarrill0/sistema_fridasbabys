from django import forms
from .models import Pedido

class PedidoEstadoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'})
        }