# operaciones/views.py
from django.shortcuts import render, redirect, get_object_or_404
from operaciones.models import Anuncio
from operaciones.forms import AnuncioForm

def anuncio_lista(request):
    anuncios = Anuncio.objects.all()
    return render(request, 'operaciones/anuncios/anuncio_lista.html', {'anuncios': anuncios})

def anuncio_crear(request):
    if request.method == 'POST':
        form = AnuncioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('anuncio_lista')  # Redirige a la lista de anuncios después de crear
    else:
        form = AnuncioForm()
    
    return render(request, 'operaciones/anuncios/anuncio_form.html', {'form': form, 'accion': 'Crear'})

def anuncio_editar(request, id):
    anuncio = get_object_or_404(Anuncio, id=id)
    if request.method == 'POST':
        form = AnuncioForm(request.POST, request.FILES, instance=anuncio)
        if form.is_valid():
            form.save()
            return redirect('anuncio_lista')  # Redirige a la lista de anuncios después de editar
    else:
        form = AnuncioForm(instance=anuncio)
    
    return render(request, 'operaciones/anuncios/anuncio_form.html', {'form': form, 'accion': 'Editar'})

def anuncio_eliminar(request, id):
    anuncio = get_object_or_404(Anuncio, id=id)
    if request.method == 'POST':
        anuncio.delete()
        return redirect('anuncio_lista')  # Redirige a la lista de anuncios después de eliminar
    return render(request, 'operaciones/anuncios/anuncio_confirmar_eliminar.html', {'anuncio': anuncio})
