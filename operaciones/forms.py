# operaciones/forms.py
from django import forms
from operaciones.models import Anuncio

class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        fields= "__all__"
        exclude=["estado",]

class AnuncioEditarForm(forms.ModelForm):
    class Meta:
        model= Anuncio
        fields= "__all__"
        exclude=["estado",]