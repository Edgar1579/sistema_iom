from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time
from django.contrib.auth import get_user_model
from django.utils import timezone

def get_image_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.documento}.{ext}"
    return f"comunidad/usuarios/{filename}"

class Usuario(models.Model):
    primer_nombre = models.CharField(max_length=45, verbose_name="Primer Nombre")
    segundo_nombre = models.CharField(max_length=45, verbose_name="Segundo Nombre", blank=True, null=True)
    primer_apellido = models.CharField(max_length=45, verbose_name="Primer Apellido")
    segundo_apellido = models.CharField(max_length=45, verbose_name="Segundo Apellido")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    imagen = models.ImageField(upload_to=get_image_filename, blank=True, null=True, default="comunidad/default-user.jpeg")
    correo = models.EmailField(max_length=50, verbose_name="Correo")

    class TipoDocumento(models.TextChoices):
        CEDULA = 'CC', _("Cédula")
        CEDULA_EXTRANJERIA = 'CE', _("Cédula de Extranjería")

    tipo_documento = models.CharField(max_length=2, choices=TipoDocumento.choices, verbose_name="Tipo de Documento")
    documento = models.PositiveIntegerField(verbose_name="Documento", unique=True)

    class RolChoices(models.TextChoices):
        ADMINISTRADOR = 'ADMIN', _("Administrador")
        EMPLEADO = 'EMP', _("Empleado")
        RECURSOS_HUMANOS = 'RH', _("Recursos Humanos")

    rol = models.CharField(max_length=5, choices=RolChoices.choices, default=RolChoices.EMPLEADO, verbose_name="Rol")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True, verbose_name="Estado Activo")

    departamento = models.CharField(max_length=100, verbose_name="Departamento", blank=True, null=True, help_text="Departamento al que pertenece el usuario")
    cargo = models.CharField(max_length=100, verbose_name="Cargo", blank=True, null=True, help_text="Cargo o posición del usuario")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono", blank=True, null=True)
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso", blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios_creados', verbose_name="Creado por")

    def clean(self):
        super().clean()
        # Normalizar nombres y apellidos
        self.primer_nombre = self.primer_nombre.strip().title() if self.primer_nombre else self.primer_nombre
        self.segundo_nombre = self.segundo_nombre.strip().title() if self.segundo_nombre else self.segundo_nombre
        self.primer_apellido = self.primer_apellido.strip().title() if self.primer_apellido else self.primer_apellido
        self.segundo_apellido = self.segundo_apellido.strip().title() if self.segundo_apellido else self.segundo_apellido

        # Validar documento según tipo
        if self.tipo_documento == self.TipoDocumento.CEDULA:
            if self.documento and (len(str(self.documento)) < 6 or len(str(self.documento)) > 10):
                raise ValidationError({'documento': 'La cédula debe tener entre 6 y 10 dígitos'})
        elif self.tipo_documento == self.TipoDocumento.CEDULA_EXTRANJERIA:
            if self.documento and (len(str(self.documento)) < 6 or len(str(self.documento)) > 12):
                raise ValidationError({'documento': 'La cédula de extranjería debe tener entre 6 y 12 dígitos'})

        # Validaciones específicas por rol
        if self.rol == self.RolChoices.RECURSOS_HUMANOS and not self.departamento:
            self.departamento = "Recursos Humanos"

    def save(self, *args, **kwargs):
        self.full_clean()
        # Configurar permisos del usuario Django según el rol
        if self.user:
            self.user.is_staff = self.rol in [self.RolChoices.ADMINISTRADOR, self.RolChoices.RECURSOS_HUMANOS]
            self.user.is_superuser = self.rol == self.RolChoices.ADMINISTRADOR
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

    @property
    def full_name(self):
        return f"{self.primer_nombre} {self.segundo_nombre or ''} {self.primer_apellido} {self.segundo_apellido or ''}".strip()

    @property
    def edad(self):
        today = datetime.today().date()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

    # Métodos de verificación de roles
    def es_administrador(self):
        return self.rol == self.RolChoices.ADMINISTRADOR

    def es_empleado(self):
        return self.rol == self.RolChoices.EMPLEADO

    def es_recursos_humanos(self):
        return self.rol == self.RolChoices.RECURSOS_HUMANOS

    def puede_gestionar_usuarios(self):
        return self.rol in [self.RolChoices.ADMINISTRADOR, self.RolChoices.RECURSOS_HUMANOS]

    def get_imagen_url(self):
        return self.imagen.url if self.imagen and hasattr(self.imagen, 'url') else '/media/comunidad/default-user.jpeg'

class RegistroHoras(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()
    horas_normales_diurnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_normales_nocturnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_extras_diurnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_extras_nocturnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recargo_nocturno = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recargo_dominical = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recargo_festivo = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def es_domingo(self):
        return self.fecha.weekday() == 6  # domingo es el día 6

    def es_festivo(self):
        festivos = [
            datetime(2023, 1, 1).date(),  # Año Nuevo
            datetime(2023, 5, 1).date(),  # Día del Trabajo
            # Añadir más festivos
        ]
        return self.fecha in festivos

    def calcular_horas(self):
        entrada = datetime.combine(self.fecha, self.hora_entrada)
        salida = datetime.combine(self.fecha, self.hora_salida)

        if salida <= entrada:
            raise ValidationError("La hora de salida debe ser posterior a la hora de entrada.")

        # Definir límites horarios
        inicio_diurno = time(6, 0)  # 6:00 AM
        fin_diurno = time(19, 0)    # 7:00 PM

        # Calcular horas trabajadas
        total_horas = (salida - entrada).total_seconds() / 3600

        if self.es_domingo() or self.es_festivo():
            self.calcular_horas_dominical_festivo(entrada, salida)
        else:
            self.calcular_horas_normales(entrada, salida)

    def calcular_pago_total(self):
        pago = 0
        # Horas normales
        pago += self.horas_normales_diurnas * 10000  # Ejemplo: $10,000 por hora normal
        pago += self.horas_normales_nocturnas * 10000 * 1.35  # 35% recargo nocturno

        # Horas extras
        if self.es_domingo() or self.es_festivo():
            recargo = 0.80 if self.es_domingo() else 0.80  # 80% recargo
            pago += self.horas_extras_diurnas * 10000 * (1 + recargo)
            pago += self.horas_extras_nocturnas * 10000 * (1 + recargo + 0.35)  # 35% recargo nocturno
        else:
            pago += self.horas_extras_diurnas * 10000 * 1.25  # 25% recargo extra diurno
            pago += self.horas_extras_nocturnas * 10000 * 1.75  # 75% recargo extra nocturno

        return pago

    def save(self, *args, **kwargs):
        if self.hora_salida <= self.hora_entrada:
            raise ValueError("La hora de salida debe ser posterior a la hora de entrada.")
        self.calcular_horas()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha}"

    def calcular_horas_normales(self, entrada, salida):
        fin_diurno = entrada.replace(hour=19, minute=0)  # 7:00 PM

        if salida <= fin_diurno:
            self.horas_normales_diurnas = (salida - entrada).total_seconds() / 3600
        else:
            self.horas_normales_diurnas = (fin_diurno - entrada).total_seconds() / 3600
            self.horas_normales_nocturnas = (salida - fin_diurno).total_seconds() / 3600

    def calcular_horas_dominical_festivo(self, entrada, salida):
        fin_diurno = entrada.replace(hour=19, minute=0)  # 7:00 PM
        horas_totales = (salida - entrada).total_seconds() / 3600

        if salida <= fin_diurno:
            self.horas_normales_diurnas = horas_totales
        else:
            self.horas_normales_diurnas = (fin_diurno - entrada).total_seconds() / 3600
            self.horas_normales_nocturnas = (salida - fin_diurno).total_seconds() / 3600

class SolicitudPermiso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permisos')
    fecha = models.DateField(default=timezone.now)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.TextField()
    documento_identidad = models.CharField(max_length=20, blank=True, verbose_name="Documento de identidad")
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - {self.get_estado_display()}"

class CalculoJornada:
    def __init__(self, fecha, hora_entrada, hora_salida):
        self.fecha = fecha
        self.hora_entrada = hora_entrada
        self.hora_salida = hora_salida
        self.horas_normales_diurnas = 0
        self.horas_normales_nocturnas = 0
        self.horas_extras_diurnas = 0
        self.horas_extras_nocturnas = 0
        self.recargo_dominical = 0
        self.recargo_festivo = 0
        self.recargo_nocturno = 0

    def es_festivo(self):
        festivos = [
            datetime(2023, 1, 1).date(),  # Año Nuevo
            datetime(2023, 12, 25).date(),  # Navidad
        ]
        return self.fecha in festivos

    def es_dominical(self):
        return self.fecha.weekday() == 6  # 6 es domingo

    def calcular_horas(self):
        entrada = datetime.combine(self.fecha, self.hora_entrada)
        salida = datetime.combine(self.fecha, self.hora_salida)

        if salida <= entrada:
            raise ValidationError("La hora de salida debe ser después de la hora de entrada.")

        # Definir límites horarios
        hora_limite_diurna = entrada.replace(hour=19, minute=0)  # 7 PM
        hora_limite_nocturna = entrada.replace(hour=6, minute=0) + timedelta(days=1)  # 6 AM del día siguiente

        # Calcular horas normales y extras
        if salida <= hora_limite_diurna:
            self.horas_normales_diurnas = (salida - entrada).total_seconds() / 3600
        else:
            self.horas_normales_diurnas = (hora_limite_diurna - entrada).total_seconds() / 3600
            if salida > hora_limite_diurna:
                self.horas_extras_diurnas = (min(salida, hora_limite_nocturna) - hora_limite_diurna).total_seconds() / 3600

        if salida > hora_limite_nocturna:
            self.horas_normales_nocturnas = (salida - max(hora_limite_nocturna, entrada)).total_seconds() / 3600

        # Aplicar recargos
        if self.es_festivo():
            self.recargo_festivo = (self.horas_normales_diurnas + self.horas_extras_diurnas) * 0.8  # 80%
            self.recargo_festivo += self.horas_extras_nocturnas * 1.5  # 150% para horas extras nocturnas
        elif self.es_dominical():
            self.recargo_dominical = (self.horas_normales_diurnas + self.horas_extras_diurnas) * 0.8  # 80%
            self.recargo_dominical += self.horas_extras_nocturnas * 1.5  # 150% para horas extras nocturnas
        else:
            self.recargo_nocturno = self.horas_normales_nocturnas * 0.35  # 35%

    def obtener_resultados(self):
        self.calcular_horas()
        return {
            'horas_normales_diurnas': self.horas_normales_diurnas,
            'horas_normales_nocturnas': self.horas_normales_nocturnas,
            'horas_extras_diurnas': self.horas_extras_diurnas,
            'horas_extras_nocturnas': self.horas_extras_nocturnas,
            'recargo_dominical': self.recargo_dominical,
            'recargo_festivo': self.recargo_festivo,
            'recargo_nocturno': self.recargo_nocturno,
        }
