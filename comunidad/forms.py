from django import forms
from django.forms import ModelForm, widgets
from comunidad.models import Usuario, RegistroHoras

class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"
        exclude = ["estado", "user"]
        widgets = {
            'fecha_nacimiento': widgets.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }

class UsuarioEditarForm(ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"
        exclude = ["estado", "user"]


class RegistroHorasForm(forms.ModelForm):
    class Meta:
        model = RegistroHoras
        fields = ['usuario', 'fecha', 'horas_trabajadas', 'horas_extras', 'permisos']
        widgets = {
            'fecha': widgets.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }
    
