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
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.paginator import Paginator



def usuario_crear(request):
    titulo = "Usuario"
    accion = "Agregar"
    usuarios = Usuario.objects.all()

    if request.method == "POST":
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            documento = request.POST['documento']
            correo = request.POST['correo']
            primer_nombre = request.POST['primer_nombre']
            primer_apellido = request.POST['primer_apellido']

            # Crear el usuario de Django si no existe
            user = User.objects.filter(username=documento).first()
            if not user:
                password = "@" + primer_nombre[0].lower() + primer_apellido[0].lower() + documento[-4:]
                user = User.objects.create_user(
                    username=documento,
                    email=correo,
                    password=password  # No es necesario usar make_password aquí
                )
                user.first_name = primer_nombre
                user.last_name = primer_apellido
                user.save()

            # Guardar el Usuario personalizado
            usuario = form.save(commit=False)
            usuario.user = user
            usuario.save()

            messages.success(request, "Usuario creado exitosamente.")
            return redirect('usuarios')
        else:
            messages.error(request, "Formulario inválido.")
    else:
        form = UsuarioForm()

    context = {
        "titulo": titulo,
        "accion": accion,
        "usuarios": usuarios,
        "form": form,
    }
    return render(request, "comunidad/usuarios/usuarios.html", context)



def usuario_eliminar(request, pk):
    usuario = Usuario.objects.filter(id=pk)
    usuario.update(estado=False)
    
    messages.success(request, "Usuario eliminado correctamente.")
    return redirect('usuarios')
def usuario_editar(request, pk):
    usuario = Usuario.objects.get(id=pk)
    usuarios = Usuario.objects.all()
    accion="Editar"
    nombre=f"{usuario.primer_nombre} {usuario.primer_apellido}"
    titulo=f"Usuario {nombre}"

    if request.method == "POST":
        form = UsuarioEditarForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            correo = request.POST['correo']
            primer_nombre = request.POST['primer_nombre']
            primer_apellido = request.POST['primer_apellido']

            # Actualizar el usuario del modelo User
            user = usuario.user
            if user:
                user.email = correo
                user.first_name = primer_nombre
                user.last_name = primer_apellido
                user.save()
            else:
                user = User.objects.create_user(
                    email=correo,
                    password=make_password(
                        "@" + primer_nombre[0] + primer_apellido[0] 
                    )
                )
                usuario.user = user

            usuario = form.save(commit=False)
            usuario.user = user
            usuario.save()

            messages.success(request, "Usuario actualizado exitosamente.")
            return redirect("usuarios")
        else:
            messages.error(request, "Error al actualizar el usuario.")
    else:
        form = UsuarioEditarForm(instance=usuario)

    context = {
        "titulo": titulo,
        "accion": accion,
        "form": form,
        "usuarios": usuarios,
    }
    return render(request, "comunidad/usuarios/usuarios.html", context)


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
            return redirect('edit_group',group_id)  # Cambia 'list_groups' por el nombre de la URL donde se listan los grupos
    else:
        form = GroupForm(instance=group)
    context={
    'groups':groups,
    'group': group,
    'form': form
    }
    return render(request, 'comunidad/usuarios/grupos.html', context)                        


@login_required
def registrar_horas(request):
    if request.method == 'POST':
        form = RegistroHorasForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            registro.save()
            return redirect('lista_registros')
    else:
        form = RegistroHorasForm()
    return render(request, 'comunidad/horas/registrar.html', {'form': form})


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
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            festivos = holidays.Colombia()
            es_festivo = fecha in festivos
            es_domingo = fecha.weekday() == 6
            return JsonResponse({
                'es_festivo': es_festivo,
                'es_domingo': es_domingo,
                'tipo': 'Festivo' if es_festivo else 'Domingo' if es_domingo else 'Normal'
            })
        except ValueError:
            pass
    return JsonResponse({'error': 'Fecha inválida'}, status=400)
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

""" @login_required
def actualizar_datos(request):
    if request.method == 'POST':
        form = ActualizarDatosForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos actualizados exitosamente.")
            return redirect('comunidad:dashboard_empleado')
    else:
        form = ActualizarDatosForm(instance=request.user)
    return render(request, 'comunidad/actualizar_datos.html', {'form': form}) """


