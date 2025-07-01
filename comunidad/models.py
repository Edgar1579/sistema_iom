from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def get_image_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.documento}.{ext}"
    return f"comunidad/usuarios/{filename}"

# Create your models here.
class Usuario(models.Model):
    primer_nombre = models.CharField(max_length=45, verbose_name="Primer Nombre")
    segundo_nombre = models.CharField(max_length=45, verbose_name="Segundo Nombre", blank=True, null=True)
    primer_apellido = models.CharField(max_length=45, verbose_name="Primer Apellido")
    segundo_apellido = models.CharField(max_length=45, verbose_name="Segundo Apellido")
    
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    imagen = models.ImageField(
        upload_to=get_image_filename, 
        blank=True, 
        null=True, 
        default="comunidad/default-user.jpeg",
        verbose_name="Imagen de Perfil"
    )
    correo = models.EmailField(max_length=50, verbose_name="Correo", unique=True)
    
    class TipoDocumento(models.TextChoices):
        CEDULA = 'CC', _("Cédula")
        CEDULA_EXTRANJERIA = 'CE', _("Cédula de Extranjería")
    
    tipo_documento = models.CharField(
        max_length=2, 
        choices=TipoDocumento.choices, 
        verbose_name="Tipo de Documento"
    )
    documento = models.PositiveIntegerField(verbose_name="Documento", unique=True)
    
    # Sistema de roles
    class RolChoices(models.TextChoices):
        ADMINISTRADOR = 'ADMIN', _("Administrador")
        EMPLEADO = 'EMP', _("Empleado")
        RECURSOS_HUMANOS = 'RH', _("Recursos Humanos")
    
    rol = models.CharField(
        max_length=5,
        choices=RolChoices.choices,
        default=RolChoices.EMPLEADO,
        verbose_name="Rol"
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario Django")
    estado = models.BooleanField(default=True, verbose_name="Estado Activo")
    
    # Campos específicos por rol
    departamento = models.CharField(
        max_length=100, 
        verbose_name="Departamento", 
        blank=True, 
        null=True,
        help_text="Departamento al que pertenece el usuario"
    )
    cargo = models.CharField(
        max_length=100, 
        verbose_name="Cargo", 
        blank=True, 
        null=True,
        help_text="Cargo o posición del usuario"
    )
    telefono = models.CharField(
        max_length=15, 
        verbose_name="Teléfono", 
        blank=True, 
        null=True
    )
    fecha_ingreso = models.DateField(
        verbose_name="Fecha de Ingreso", 
        blank=True, 
        null=True
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='usuarios_creados',
        verbose_name="Creado por"
    )
    
    def clean(self):
        super().clean()
        # Normalizar nombres y apellidos
        if self.primer_nombre:
            self.primer_nombre = self.primer_nombre.strip().title()
        if self.segundo_nombre:
            self.segundo_nombre = self.segundo_nombre.strip().title()
        if self.primer_apellido:
            self.primer_apellido = self.primer_apellido.strip().title()
        if self.segundo_apellido:
            self.segundo_apellido = self.segundo_apellido.strip().title()
        
        # Validar documento según tipo
        if self.tipo_documento == self.TipoDocumento.CEDULA:
            if self.documento and (len(str(self.documento)) < 6 or len(str(self.documento)) > 10):
                raise ValidationError({
                    'documento': 'La cédula debe tener entre 6 y 10 dígitos'
                })
        elif self.tipo_documento == self.TipoDocumento.CEDULA_EXTRANJERIA:
            if self.documento and (len(str(self.documento)) < 6 or len(str(self.documento)) > 12):
                raise ValidationError({
                    'documento': 'La cédula de extranjería debe tener entre 6 y 12 dígitos'
                })
        
        # Validaciones específicas por rol
        if self.rol == self.RolChoices.RECURSOS_HUMANOS:
            if not self.departamento:
                self.departamento = "Recursos Humanos"
    
    def save(self, *args, **kwargs):
        self.full_clean()
        
        # Configurar permisos del usuario Django según el rol
        if self.user:
            if self.rol == self.RolChoices.ADMINISTRADOR:
                self.user.is_staff = True
                self.user.is_superuser = True
            elif self.rol == self.RolChoices.RECURSOS_HUMANOS:
                self.user.is_staff = True
                self.user.is_superuser = False
            else:  # EMPLEADO
                self.user.is_staff = False
                self.user.is_superuser = False
            
            self.user.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido} ({self.get_rol_display()})"
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['primer_apellido', 'primer_nombre']
        db_table = 'usuarios'
        permissions = [
            ("can_manage_all_users", "Puede gestionar todos los usuarios"),
            ("can_view_reports", "Puede ver reportes"),
            ("can_manage_empleados", "Puede gestionar empleados"),
        ]
    
    # Propiedades básicas
    @property
    def full_name(self):
        nombres = [self.primer_nombre]
        if self.segundo_nombre:
            nombres.append(self.segundo_nombre)
        apellidos = [self.primer_apellido, self.segundo_apellido]
        return f"{' '.join(nombres)} {' '.join(apellidos)}"
    
    @property
    def nombre_completo_corto(self):
        return f"{self.primer_nombre} {self.primer_apellido}"
    
    @property
    def iniciales(self):
        iniciales = self.primer_nombre[0] + self.primer_apellido[0]
        return iniciales.upper()
    
    @property
    def edad(self):
        """Calcula la edad del usuario"""
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    # Métodos de verificación de roles
    def es_administrador(self):
        """Verifica si el usuario es administrador"""
        return self.rol == self.RolChoices.ADMINISTRADOR
    
    def es_empleado(self):
        """Verifica si el usuario es empleado"""
        return self.rol == self.RolChoices.EMPLEADO
    
    def es_recursos_humanos(self):
        """Verifica si el usuario es de recursos humanos"""
        return self.rol == self.RolChoices.RECURSOS_HUMANOS
    
    def puede_gestionar_usuarios(self):
        """Verifica si puede gestionar otros usuarios"""
        return self.rol in [self.RolChoices.ADMINISTRADOR, self.RolChoices.RECURSOS_HUMANOS]
    
    def puede_ver_reportes(self):
        """Verifica si puede ver reportes"""
        return self.rol in [self.RolChoices.ADMINISTRADOR, self.RolChoices.RECURSOS_HUMANOS]
    
    # Métodos de estado
    def esta_activo(self):
        """Verifica si el usuario está activo"""
        return self.estado
    
    def activar(self):
        """Activa el usuario"""
        self.estado = True
        self.save()
    
    def desactivar(self):
        """Desactiva el usuario"""
        self.estado = False
        self.save()
    
    # Métodos de información
    def get_documento_completo(self):
        """Retorna el documento con su tipo"""
        return f"{self.get_tipo_documento_display()}: {self.documento}"
    
    def get_imagen_url(self):
        """Retorna la URL de la imagen o la imagen por defecto"""
        if self.imagen and hasattr(self.imagen, 'url'):
            return self.imagen.url
        return '/media/comunidad/default-user.jpeg'
    
    def get_info_completa(self):
        """Retorna información completa del usuario"""
        return {
            'nombre_completo': self.full_name,
            'documento': self.get_documento_completo(),
            'rol': self.get_rol_display(),
            'departamento': self.departamento,
            'cargo': self.cargo,
            'correo': self.correo,
            'telefono': self.telefono,
            'estado': 'Activo' if self.estado else 'Inactivo',
            'edad': self.edad
        }
    
    # Métodos de consulta estáticos
    @staticmethod
    def get_administradores():
        """Obtiene todos los administradores activos"""
        return Usuario.objects.filter(rol=Usuario.RolChoices.ADMINISTRADOR, estado=True)
    
    @staticmethod
    def get_empleados():
        """Obtiene todos los empleados activos"""
        return Usuario.objects.filter(rol=Usuario.RolChoices.EMPLEADO, estado=True)
    
    @staticmethod
    def get_recursos_humanos():
        """Obtiene todos los usuarios de recursos humanos activos"""
        return Usuario.objects.filter(rol=Usuario.RolChoices.RECURSOS_HUMANOS, estado=True)
    
    @staticmethod
    def get_usuarios_por_departamento(departamento):
        """Obtiene usuarios por departamento"""
        return Usuario.objects.filter(departamento=departamento, estado=True)