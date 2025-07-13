# comunidad/urls.py
from django.urls import path
from comunidad.views import usuario_crear, usuario_eliminar

urlpatterns = [
    path("usuarios/", usuario_crear, name='usuarios'),
    path("usuarios/eliminar/<int:pk>/", usuario_eliminar, name="usuario-eliminar")
]