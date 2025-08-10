from django import forms
from django.forms import ModelChoiceField, ModelForm, widgets
from comunidad.models import Usuario, RegistroHoras, SolicitudPermiso
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple
from decimal import Decimal
from django.core.exceptions import ValidationError
import holidays


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

class RegistroHorasForm(forms.ModelForm):
    numero_documento = forms.CharField(label="Número de Documento", required=False, disabled=True)

    class Meta:
        model = RegistroHoras
        fields = ['numero_documento', 'fecha', 'hora_entrada', 'hora_salida']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'hora_entrada': forms.TimeInput(attrs={'type': 'time'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        if usuario:
            # Obtén el objeto Usuario asociado al usuario logueado
            try:
                usuario_obj = Usuario.objects.get(user=usuario)
                # Asigna el número de documento del usuario al campo
                self.fields['numero_documento'].initial = usuario_obj.documento
            except Usuario.DoesNotExist:
                self.fields['numero_documento'].initial = ""  # Manejo de error si no se encuentra el usuario

    def clean(self):
     cleaned_data = super().clean()
     fecha = cleaned_data.get('fecha')

     if fecha:
        es_domingo = fecha.weekday() == 6
        es_festivo = fecha in holidays.Colombia(years=fecha.year)

        if es_domingo or es_festivo:
            msg = []
            if es_domingo:
                msg.append("DOMINGO")
            if es_festivo:
                msg.append("FESTIVO")

            # En lugar de marcar error:
            self.add_error('fecha', f"La fecha seleccionada es un {' y '.join(msg)}.")

        return cleaned_data



class SolicitudPermisoForm(forms.ModelForm):
    class Meta:
        model = SolicitudPermiso
        fields = ['fecha', 'hora_inicio', 'hora_fin', 'motivo', 'documento_identidad']

        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'motivo': forms.Textarea(attrs={'rows': 4}),
           
        }
        
