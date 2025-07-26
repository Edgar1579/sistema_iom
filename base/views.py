from django.shortcuts import render, redirect
from django.contrib import messages
from configuracion.models import Slider
from comunidad.models import Usuario
from operaciones.models import Anuncio
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

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
    
    # Obtener todos los usuarios
    usuarios = Usuario.objects.all().count()
    # Obtener todos los anuncios
    anuncios = Anuncio.objects.all().count()
    
    # Procesar formulario si es POST
    if request.method == 'POST':
        try:
            # Crear usuario Django
            user = User.objects.create_user(
                username=request.POST['documento'],
                email=request.POST['correo'],
                password=request.POST['password']
            )
            
            # Crear usuario personalizado
            usuario = Usuario.objects.create(
                primer_nombre=request.POST['primer_nombre'],
                segundo_nombre=request.POST.get('segundo_nombre', ''),
                primer_apellido=request.POST['primer_apellido'],
                segundo_apellido=request.POST['segundo_apellido'],
                fecha_nacimiento=request.POST['fecha_nacimiento'],
                correo=request.POST['correo'],
                documento=request.POST['documento'],
                tipo_documento=request.POST['tipo_documento'],
                rol=request.POST['rol'],
                departamento=request.POST.get('departamento', ''),
                cargo=request.POST.get('cargo', ''),
                telefono=request.POST.get('telefono', ''),
                user=user,
                creado_por=request.user if request.user.is_authenticated else None
            )
            
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('index-admin')
            
        except User.DoesNotExist:
            messages.error(request, 'Error: El usuario no pudo ser creado.')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    context = {
        "titulo": titulo,
        "usuarios": usuarios,

    }
    return render(request, "index-admin.html", context)

def logout_user(request):
    logout(request)
    return redirect('index') # Asegúrate de que 'index' sea una URL válida
