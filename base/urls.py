from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static  # Importa static
from base.views import principal

# Vista para la página de inicio
def home_view(request):
    return render(request, 'partials/home.html')

# Vista para registrar horas
def registrar_horas_view(request):
    return HttpResponse("Registrar Horas")  # Cambia esto por tu lógica

# Vista para solicitar permiso
def solicitar_permiso_view(request):
    return HttpResponse("Solicitar Permiso")  # Cambia esto por tu lógica

# Vista para reportes
def reportes_view(request):
    return HttpResponse("Reportes")  # Cambia esto por tu lógica

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', principal, name='index'),  # Ruta para la página principal
    path('registrar_horas/', registrar_horas_view, name='registrar_horas'),  # Ruta para registrar horas
    path('solicitar_permiso/', solicitar_permiso_view, name='solicitar_permiso'),  # Ruta para solicitar permiso
    path('reportes/', reportes_view, name='reportes'),  # Ruta para reportes
]

# Solo para desarrollo: sirve archivos estáticos y media
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Esta línea faltaba