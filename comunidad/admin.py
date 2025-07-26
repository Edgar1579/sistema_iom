from django.contrib import admin
from comunidad.models import Usuario, RegistroHorario, SolicitudPermiso
from operaciones.models import Anuncio

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Anuncio)
admin.site.register(RegistroHorario)
admin.site.register(SolicitudPermiso)