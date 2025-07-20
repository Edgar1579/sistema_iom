# operaciones/urls.py
from django.urls import path
from .views import anuncio_lista, anuncio_crear, anuncio_editar, anuncio_eliminar

urlpatterns = [
    path('anuncios/', anuncio_lista, name='anuncio_lista'),
    path('anuncios/crear/', anuncio_crear, name='anuncio_crear'),
    path('anuncios/editar/<int:id>/', anuncio_editar, name='anuncio_editar'),
    path('anuncios/eliminar/<int:id>/', anuncio_eliminar, name='anuncio_eliminar'),
]
