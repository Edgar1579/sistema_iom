from django.contrib import admin
from comunidad.models import Usuario, RegistroHoras, SolicitudPermiso, ConfiguracionGeneral
from operaciones.models import Anuncio

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Anuncio)
admin.site.register(RegistroHoras)
admin.site.register(SolicitudPermiso)
@admin.register(ConfiguracionGeneral)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ('año', 'salario_minimo')