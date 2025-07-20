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

class UsuarioEditarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"
        exclude = ["estado", "user", "documento", "fecha_nacimiento"]
        # Widget personalizado para el campo de fecha (si lo necesitas)
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remueve completamente los campos excluidos del formulario
        for field_name in self.Meta.exclude:
            if field_name in self.fields:
                del self.fields[field_name]


class RegistroHorasForm(forms.ModelForm):
    class Meta:
        model = RegistroHoras
        fields = ['usuario', 'fecha', 'horas_trabajadas', 'horas_extras', 'permisos']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }


