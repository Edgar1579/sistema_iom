from django.db import models
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

from comunidad.models import Usuario, RegistroHorario, SolicitudPermiso, CalculoJornada
from comunidad.forms import UsuarioForm, UsuarioEditarForm, RegistroHorarioForm, SolicitudPermisoForm, ActualizarDatosForm
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
                user = User.objects.create_user(
                    username=documento,
                    email=correo,
                    password=make_password(
                        "@" + primer_nombre[0] + primer_apellido[0] + documento[-4:]
                    )
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
    titulo = f"Usuario {usuario.id} {usuario.primer_nombre} {usuario.primer_apellido}"
    accion = "Actualizar"

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

@login_required
def lista_registro_horario(request):
    registros = RegistroHorario.objects.filter(usuario=request.user)
    return render(request, 'comunidad/horas/registro_horario_list.html', {'registros': registros})

@login_required
def crear_registro_horario(request):
    if request.method == 'POST':
        form = RegistroHorarioForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            
            # Validar que la hora de salida sea posterior a la hora de entrada
            if registro.hora_salida <= registro.hora_entrada:
                messages.error(request, "La hora de salida debe ser posterior a la hora de entrada.")
                return render(request, 'comunidad/horas/registro_horario_form.html', {'form': form})

            try:
                # Usar la clase CalculoJornada para calcular horas y recargos
                calculo = CalculoJornada(registro.fecha, registro.hora_entrada, registro.hora_salida)
                resultados = calculo.obtener_resultados()

                # Asignar los resultados al registro
                registro.horas_normales_diurnas = resultados['horas_normales_diurnas']
                registro.horas_normales_nocturnas = resultados['horas_normales_nocturnas']
                registro.horas_extras_diurnas = resultados['horas_extras_diurnas']
                registro.horas_extras_nocturnas = resultados['horas_extras_nocturnas']
                registro.recargo_dominical = resultados['recargo_dominical']
                registro.recargo_festivo = resultados['recargo_festivo']
                registro.recargo_nocturno = resultados['recargo_nocturno']

                # Guardar el registro
                registro.save()
                messages.success(request, "Registro de horario creado exitosamente.")
                return redirect('registro_horario_list')
            except Exception as e:
                messages.error(request, f"Error al calcular los resultados: {str(e)}")
        else:
            messages.error(request, "Error al crear el registro de horario. Por favor, verifica los datos.")
    else:
        form = RegistroHorarioForm()
    
    return render(request, 'comunidad/horas/registro_horario_form.html', {'form': form})

@login_required
def detalle_pago(request, registro_id):
    registro = get_object_or_404(RegistroHorario, id=registro_id, usuario=request.user)
    pago_total = registro.calcular_pago_total()
    
    return render(request, 'detalle_pago.html', {
        'registro': registro,
        'pago_total': pago_total
    })

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

@login_required
def actualizar_datos(request):
    if request.method == 'POST':
        form = ActualizarDatosForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos actualizados exitosamente.")
            return redirect('comunidad:dashboard_empleado')
    else:
        form = ActualizarDatosForm(instance=request.user)
    return render(request, 'comunidad/actualizar_datos.html', {'form': form})

@login_required
def registro_horas(request):
    return render(request, 'comunidad/registro_horas.html')
