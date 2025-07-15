# comunidad/urls.py
from django.urls import path
from comunidad.views import usuario_crear, usuario_eliminar, usuario_editar, registrar_horas, lista_horas


urlpatterns = [
    path("usuarios/", usuario_crear, name='usuarios'),
    path("usuarios/eliminar/<int:pk>/", usuario_eliminar, name="usuario-eliminar"),
    path("usuarios/editar/<int:pk>/", usuario_editar, name="usuario-editar"),
    path('registro/', registrar_horas, name='registrar-horas'),
    path('lista/', lista_horas, name='lista_horas'),
]