from django import forms
from django.forms import ModelChoiceField, ModelForm, widgets
from comunidad.models import Usuario, RegistroHoras, SolicitudPermiso
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple
from decimal import Decimal
from django.core.exceptions import ValidationError
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




# forms.py

from django import forms
from .models import RegistroHoras
import holidays

class RegistroHorasForm(forms.ModelForm):
    class Meta:
        model = RegistroHoras
        fields = ['fecha', 'hora_entrada', 'hora_salida']
        widgets={
            'fecha':widgets.DateInput(attrs={'type':'date'},format='%Y-%m-%d'),
            'hora_entrada': widgets.TimeInput(attrs={'type': 'time'}),
            'hora_salida': widgets.TimeInput(attrs={'type': 'time'})
           
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')

        if fecha:
            msg = []
            if fecha.weekday() == 6:
                msg.append("La fecha seleccionada es un DOMINGO.")
            
            colombia_holidays = holidays.Colombia(years=fecha.year)
            if fecha in colombia_holidays:
                msg.append("La fecha seleccionada es un FESTIVO en Colombia.")

            if msg:
                self.add_error('fecha', " ".join(msg))

        return cleaned_data


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
        
