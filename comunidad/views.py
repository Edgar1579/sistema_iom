from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
import holidays
from comunidad.forms import UsuarioForm, UsuarioEditarForm, RegistroHorasForm, SolicitudPermisoForm, GroupForm
from comunidad.models import Usuario, RegistroHoras, SolicitudPermiso
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from PIL import Image
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from datetime import datetime

# Create your views here.

#@permission_required('comunidad.add_usuario', raise_exception=True)
def usuario_crear(request):
    titulo="Usuario"
    accion="Agregar"
    usuarios= Usuario.objects.all()
    if request.method=="POST":
        form= UsuarioForm(request.POST,request.FILES)
        if form.is_valid():
            if not User.objects.filter(username=request.POST['documento']):
                user = User.objects.create_user('nombre','email@email','pass')
                user.username= request.POST['documento']
                user.first_name= request.POST['primer_nombre']
                user.last_name= request.POST['primer_apellido']
                user.email= request.POST['correo']
                user.password=make_password("@" + request.POST['primer_nombre'][0] + request.POST['primer_apellido'][0] + request.POST['documento'][-4:])
                user.save()
            else:
                user=User.objects.get(username=request.POST['documento'])
            rol_id = request.POST.get('rol')  # Obtén el ID del grupo seleccionado en el formulario
            if rol_id:
                rol = Group.objects.get(id=rol_id)
                user.groups.add(rol)  # Asocia el usuario al grupo
            usuario = Usuario.objects.create(
                primer_nombre=request.POST['primer_nombre'],
                segundo_nombre=request.POST['segundo_nombre'],
                primer_apellido=request.POST['primer_apellido'],
                segundo_apellido=request.POST['segundo_apellido'],
                fecha_nacimiento=request.POST['fecha_nacimiento'],
                imagen=request.FILES.get('imagen'),  # Asume que tu formulario maneja archivos
                correo=request.POST['correo'],
                tipo_documento=request.POST['tipo_documento'],
                documento=request.POST['documento'],
                user=user,
                
            )
            messages.success(request, f'¡El Usuario se agregó de forma exitosa!')
            if usuario.imagen:
                 img = Image.open(usuario.imagen.path)
                 img= img.resize((500,500))
                 img.save(usuario.imagen.path)
            usuario.save()
            return redirect('usuarios')

        else:
            messages.success(request, f'¡Error al agregar al Usuario!')
            form = UsuarioForm(request.POST,request.FILES)
    else:
        form=UsuarioForm()
    context={
        "titulo":titulo,
        "usuarios":usuarios,
        "form":form,
        "accion":accion
    }
    return render(request,"comunidad/usuarios/usuarios.html", context)
def usuario_editar(request,pk):
    usuario= Usuario.objects.get(id=pk)
    usuarios= Usuario.objects.all()
    accion="Editar"
    nombre=f"{usuario.primer_nombre} {usuario.primer_apellido}"
    titulo=f"Usuario {nombre}"

    if request.method=="POST":
        form= UsuarioEditarForm(request.POST,request.FILES, instance=usuario)
        if form.is_valid():
            usuario= form.save()
            # Actualizar el grupo del usuario
            rol_id = request.POST.get('rol')
            if rol_id:
                rol = Group.objects.get(id=rol_id)
                usuario.user.groups.set([rol])
            if usuario.imagen:
                img = Image.open(usuario.imagen.path)
                img= img.resize((500,500))
                img.save(usuario.imagen.path)
            usuario.save()
            messages.success(request, f'¡{nombre} se editó de forma exitosa!')
            return redirect("usuarios")
        else:
            messages.error(request, f'¡Error al editar a {nombre}!')

    else:
        form=UsuarioEditarForm(instance=usuario)
    context={
        "titulo":titulo,
        "usuarios":usuarios,
        "form":form,
        "accion":accion
    }
    return render(request,"comunidad/usuarios/usuarios.html", context)
def usuario_eliminar(request,pk):
    usuario=Usuario.objects.filter(id=pk)
    usuario.update(estado=False)
    
    ## Agregar mensjae de exito
    return redirect('usuarios')

def edit_group(request, group_id=None):
    groups = Group.objects.all()
    
    if group_id:
        group = get_object_or_404(Group, id=group_id)
    else:
        group = None
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_edit', group_id=group.id) if group else redirect('group_create')
    else:
        form = GroupForm(instance=group)
    context = {
        'groups': groups,
        'group': group,
        'form': form
    }
    return render(request, 'comunidad/usuarios/grupos.html', context)

@login_required
def registrar_horas(request):
    # Obtén el objeto Usuario asociado al usuario logueado
    try:
        usuario = Usuario.objects.get(user=request.user)  # Esto es correcto
    except Usuario.DoesNotExist:
        messages.error(request, "No se encontró el usuario asociado.")
        return redirect('lista_registros')
    if request.method == 'POST':
        form = RegistroHorasForm(request.POST, usuario=request.user)
        if form.is_valid():
            registro = form.save(commit=False)  # No guardes aún, primero asigna el usuario
            registro.usuario = request.user  # Asigna el objeto User al registro
            registro.save()  # Ahora guarda el registro
            return redirect('lista_registros')
    else:
        form = RegistroHorasForm(usuario=request.user)
    return render(request, 'comunidad/horas/registrar.html', {
        'form': form,
        'numero_documento': usuario.documento  # Pasa el número de documento al template
    })




@login_required
def panel_inicio(request):
    return render(request, 'comunidad/horas/panel_inicio.html', {'titulo': 'Panel de Inicio'})

@login_required
def lista_registros(request):
    registros = RegistroHoras.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'comunidad/horas/lista.html', {'registros': registros})

@login_required
def detalle_registro(request, pk):
    registro = get_object_or_404(RegistroHoras, pk=pk, usuario=request.user)
    return render(request, 'comunidad/horas/detalle.html', {'registro': registro})

def verificar_tipo_dia(request):
    fecha_str = request.GET.get('fecha')
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        if fecha.weekday() == 6:
            return JsonResponse({'tipo': 'domingo'})
        elif fecha in holidays.Colombia(years=fecha.year):
            return JsonResponse({'tipo': 'festivo'})
        else:
            return JsonResponse({'tipo': 'día laboral'})
    except ValueError:
        return JsonResponse({'error': 'Fecha inválida'})

@login_required
def lista_solicitud_permiso(request):
    solicitudes = SolicitudPermiso.objects.filter(usuario=request.user)
    return render(request, 'comunidad/horas/solicitud_permiso_list.html', {'solicitudes': solicitudes})

@login_required
def crear_solicitud_permiso(request):
    if request.method == 'POST':
        form = SolicitudPermisoForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.save()
            messages.success(request, "Solicitud de permiso creada exitosamente.")
            return redirect('solicitud_permiso_list')
    else:
        form = SolicitudPermisoForm()
    return render(request, 'comunidad/horas/solicitud_permiso_form.html', {'form': form})

@login_required
def dashboard_empleado(request):
    return render(request, 'comunidad/dashboard_empleado.html')

@login_required
def dashboard_administrador(request):
    return render(request, 'comunidad/dashboard_administrador.html')

@login_required
def registrar_permiso(request):
    if request.method == 'POST':
        form = SolicitudPermisoForm(request.POST)
        if form.is_valid():
            permiso = form.save(commit=False)
            permiso.usuario = request.user
            permiso.save()
            messages.success(request, "Permiso registrado exitosamente.")
            return redirect('comunidad:dashboard_empleado')
    else:
        form = SolicitudPermisoForm()
    return render(request, 'comunidad/registrar_permiso.html', {'form': form})
