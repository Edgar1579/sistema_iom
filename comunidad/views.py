from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from comunidad.models import Usuario, RegistroHoras  # Asegúrate de que RegistroHoras esté importado
from comunidad.forms import UsuarioForm, UsuarioEditarForm, RegistroHorasForm





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
def usuario_eliminar(request,pk):
    usuario = Usuario.objects.filter(id=pk)
    usuario.update(estado=False)
    

    messages.success(request, "Usuario eliminado correctamente.")
    return redirect('usuarios')

def usuario_editar(request, pk):
    
    
    usuario = Usuario.objects.get(id=pk)
    usuarios = Usuario.objects.all()
    # Titulo dinámico con datos del usuario ya obtenido
    titulo = f"Usuario {usuario.id} {usuario.primer_nombre} {usuario.primer_apellido}"
    accion = "Actualizar"

    if request.method == "POST":
        form = UsuarioEditarForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            documento = request.POST['documento']
            correo = request.POST['correo']
            primer_nombre = request.POST['primer_nombre']
            primer_apellido = request.POST['primer_apellido']

            # Actualizar el usuario del modelo User
            user = usuario.user
            if user:
                user.username = documento
                user.email = correo
                user.first_name = primer_nombre
                user.last_name = primer_apellido
                user.save()
            else:
                user = User.objects.create_user(
                    username=documento,
                    email=correo,
                    password=make_password(
                        "@" + primer_nombre[0] + primer_apellido[0] + documento[-4:]
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

def registrar_horas(request):
    if request.method == 'POST':
        form = RegistroHorasForm(request.POST)
        if form.is_valid():
            form.save()
        else:
         form = RegistroHorasForm()
    return render(request, 'comunidad/horas/registro_horas.html')

def lista_horas(request):
    horas = RegistroHoras.objects.all()
    return render(request, 'comunidad/horas/lista_horas.html', {'horas': horas})
