from django.shortcuts import render, redirect
from django.contrib import messages
from configuracion.models import Slider
from operaciones.models import Anuncio
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from comunidad.models import Usuario

@login_required
def principal(request):
    titulo = "Bienvenido"
    sliders = Slider.objects.filter(estado=True)
    # Asegúrate de definir 'anuncios' aquí
    anuncios = Anuncio.objects.filter(estado=True)  # Ejemplo de cómo podrías obtener anuncios
    context = {
        "titulo": titulo,
        "sliders": sliders,
        "anuncios": anuncios
    }
    return render(request, "index.html", context)

@login_required
def principal_admin(request):
    titulo = "Bienvenido"
    
    # Obtener las cantidades correctas
    usuarios = Usuario.objects.all().count()
    usuarios_obj = Usuario.objects.all()
    context = {
        "titulo": titulo,
        "usuarios_cantidad": usuarios,
        "usuarios_obj": usuarios_obj,
        
    }

    return render(request, "index-admin.html", context)

def logout_user(request):
    logout(request)
    return redirect('base') # Asegúrate de que 'index' sea una URL válida
