from django.forms import ModelForm, widgets
from comunidad.models import Usuario

class UsuarioForm(ModelForm):
    class Meta:
        model= Usuario
        fields= "__all__"
        exclude=["estado","user"]
        widgets={
            'fecha_nacimiento':widgets.DateInput(attrs={'type':'date'},format='%Y-%m-%d')
        }