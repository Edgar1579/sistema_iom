from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # Importa static
from base.views import principal, principal_admin



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', principal, name='index'),  # Ruta para la página principal
    path('adm/', principal_admin, name='index-admin'),
    path('comunidad/', include('comunidad.urls'))  # Incluye las URLs de la aplicación comunidad
    
]

# Solo para desarrollo: sirve archivos estáticos y media
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Esta línea faltaba