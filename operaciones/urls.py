# operaciones/urls.py
from django.urls import path
from .views import anuncio_lista, anuncio_crear, anuncio_editar, anuncio_eliminar,index

urlpatterns = [
    path('', index, name='index'),  # Página de inicio
    path('anuncios/', anuncio_lista, name='anuncio_lista'),
    path('anuncios/nuevo/', anuncio_crear, name='anuncio_crear'),
    path('anuncios/editar/<int:id>/', anuncio_editar, name='anuncio_editar'),
    path('anuncios/eliminar/<int:id>/', anuncio_eliminar, name='anuncio_eliminar'),
]
