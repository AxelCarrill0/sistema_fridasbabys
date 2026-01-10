"""
Formularios de la aplicación Pedidos.
"""

from django import forms
from .models import Pedido


class PedidoEstadoForm(forms.ModelForm):
    """
    Formulario para actualizar el estado de un pedido.
    """
    class Meta:
        model = Pedido
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'})
        }
