# operaciones/forms.py
from django import forms
from .models import Anuncio

class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        fields = ['titulo', 'imagen', 'contenido', 'accion']  # Asegúrate de incluir 'accion'
