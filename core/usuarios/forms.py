"""
Formularios para la gestión de usuarios.
Incluye creación, edición y registro de clientes.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario


class UsuarioCreationForm(UserCreationForm):
    """
    Formulario para crear un nuevo usuario con campos adicionales.
    """
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + (
            'nombre', 'email', 'telefono', 'direccion', 'rol'
        )
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }


class UsuarioChangeForm(UserChangeForm):
    """
    Formulario para actualizar un usuario existente.
    Permite cambiar la contraseña opcionalmente.
    """
    password = forms.CharField(
        label='Nueva Contraseña (Dejar vacío para no cambiar)',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = (
            'username', 'email', 'nombre', 'telefono', 'direccion', 'rol',
            'is_active', 'is_staff', 'is_superuser'
        )
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }


class ClienteRegistrationForm(UserCreationForm):
    """
    Formulario de registro para clientes.
    El rol se asigna automáticamente a 'cliente'.
    """
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'nombre', 'email', 'telefono', 'direccion')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        """
        Sobrescribe el método save para asignar rol 'cliente'.
        """
        user = super().save(commit=False)
        user.rol = 'cliente'
        if commit:
            user.save()
        return user
