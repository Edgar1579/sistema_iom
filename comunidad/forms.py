from django import forms
from django.forms import ModelChoiceField, ModelForm, widgets
from comunidad.models import Usuario, RegistroHoras, SolicitudPermiso
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple
 

class UsuarioForm(ModelForm):
    rol= ModelChoiceField(
        queryset=Group.objects.all(),
        label="Rol",
    )
    class Meta:
        model= Usuario
        fields= "__all__"
        exclude=["estado","user"]
        widgets={
            'fecha_nacimiento':widgets.DateInput(attrs={'type':'date'},format='%Y-%m-%d')
        }

class UsuarioEditarForm(ModelForm):
    rol= ModelChoiceField(
        queryset=Group.objects.all(), 
        label="Rol",
    )
    class Meta:
        model= Usuario
        fields= "__all__"
        exclude=["estado","fecha_nacimiento", "documento","user"]


class GroupForm(ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=FilteredSelectMultiple('Permissions', False),
        required=False,
    )
    class Meta:
        model = Group
        fields = ['name','permissions'] 

from django import forms
from .models import RegistroHoras

class RegistroHorasForm(forms.ModelForm):
    class Meta:
        model = RegistroHoras
        fields = ['fecha', 'hora_entrada', 'hora_salida']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_entrada': forms.TimeInput(attrs={'type': 'time'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time'}),
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