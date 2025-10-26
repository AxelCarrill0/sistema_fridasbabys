from django import forms
from .models import Usuario
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class UsuarioCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('nombre', 'email', 'telefono', 'direccion', 'rol')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rol': forms.Select(attrs={'class': 'form-control'})
        }


class UsuarioChangeForm(UserChangeForm):
    password = forms.CharField(
        label='Nueva Contraseña (Dejar vacío para no cambiar)',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'nombre', 'telefono', 'direccion', 'rol', 'is_active', 'is_staff',
                  'is_superuser')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rol': forms.Select(attrs={'class': 'form-control'})
        }