from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # Importa static
from base.views import principal, principal_admin, logout_user
#para la gestion de login y contraseña
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/',auth_views.LoginView.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('admin/', admin.site.urls),
    path('', principal, name='index'),
    path('base/', principal, name='base'),# Ruta para la página principal
    path('adm/', principal_admin, name='index-admin'),
    path('comunidad/', include('comunidad.urls')),  # Incluye las URLs de la aplicación comunidad
    path('operaciones/', include('operaciones.urls'))
    
   
]

# Solo para desarrollo: sirve archivos estáticos y media
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Esta línea faltaba