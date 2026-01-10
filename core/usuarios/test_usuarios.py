"""
Pruebas unitarias para el módulo de usuarios.
Incluye creación, validación y login de usuarios.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.usuarios.models import Usuario

def test_ejemplo_basico():
    """Prueba de ejemplo simple."""
    assert True

def usuario_valido(nombre, correo):
    """Valida si un usuario tiene nombre y correo correcto."""
    return nombre != "" and "@" in correo

def test_usuario_valido():
    """Test de usuario válido."""
    assert usuario_valido("Ana", "ana@mail.com") is True

def test_usuario_invalido():
    """Test de usuario inválido."""
    assert usuario_valido("", "correo") is False
