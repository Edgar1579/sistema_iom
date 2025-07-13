from django.shortcuts import render, redirect
from django.contrib import messages
from configuracion.models import Slider
from comunidad.models import Usuario
from django.contrib.auth.models import User

def principal(request):
    titulo = "Bienvenido"
    sliders = Slider.objects.filter(estado=True)
    context = {
        "titulo": titulo,
        "sliders": sliders
    }
    return render(request, "index.html", context)

def principal_admin(request):
    titulo = "Administración"
    
    # Obtener todos los usuarios
    usuarios = Usuario.objects.all()
    
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
            
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    context = {
        "titulo": titulo,
        "usuarios": usuarios,
        "roles": Usuario.RolChoices.choices,
        "tipos_documento": Usuario.TipoDocumento.choices,
    }
    return render(request, "index-admin.html", context)