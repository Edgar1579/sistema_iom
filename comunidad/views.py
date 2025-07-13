from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from comunidad.models import Usuario
from comunidad.forms import UsuarioForm

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