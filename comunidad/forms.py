from dataclasses import field
from django import forms
from django.forms import ModelForm, widgets
from comunidad.models import Usuario, RegistroHoras, SolicitudPermiso

class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"
        exclude = ["estado", "user"]
        widgets = {
            'fecha_nacimiento': widgets.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'fecha_ingreso': widgets.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }

class UsuarioEditarForm(ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"
        exclude = ["estado", "user", "documento", "fecha_nacimiento"]
        # Widget personalizado para el campo de fecha (si lo necesitas)
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remueve completamente los campos excluidos del formulario
        for field_name in self.Meta.exclude:
            if field_name in self.fields:
                del self.fields[field_name]

field


class RegistroHorasForm(ModelForm):
    class Meta:
        model = RegistroHoras
        fields = ['usuario', 'fecha', 'hora_entrada', 'hora_salida']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'hora_entrada': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'hora_salida': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
        }

class SolicitudPermisoForm(ModelForm):
    class Meta:
        model = SolicitudPermiso
        fields = ['fecha', 'hora_inicio', 'hora_fin', 'motivo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'motivo': forms.Textarea(attrs={'rows': 4}),
           
        }
        
class ActualizarDatosForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'correo', 'telefono', 'departamento', 'cargo']
        widgets = {
            'primer_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'segundo_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'primer_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'segundo_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
        }