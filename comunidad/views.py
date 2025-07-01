# views.py actualizado para tu aplicación de registro de horario
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Empleado, RegistroHoras, Permiso  # Asegúrate de que estos modelos existan en models.py

def home(request):
    return render(request, 'base/home.html')

@login_required
def registrar_horas(request):
    if request.method == 'POST':
        # Lógica para procesar el registro de horas
        pass
    return render(request, 'base/registro_horas.html')

@login_required
def solicitar_permiso(request):
    if request.method == 'POST':
        # Lógica para procesar solicitud de permiso
        pass
    return render(request, 'base/solicitud_permiso.html')

@login_required
def reportes(request):
    # Lógica para generar reportes
    return render(request, 'base/reportes.html')
