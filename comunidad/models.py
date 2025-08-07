from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone
from decimal import Decimal
import holidays

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
        CEDULA_EXTRANJERIA = 'CE', _("Cédula de Extrangería")

    tipo_documento = models.CharField(max_length=2, choices=TipoDocumento.choices, verbose_name="Tipo de Documento")
    documento = models.PositiveIntegerField(verbose_name="Documento", unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)
    departamento = models.CharField(max_length=50, verbose_name="Departamento", blank=True, null=True)
    telefono = models.CharField(max_length=15, verbose_name="Teléfono", blank=True, null=True)
    cargo = models.CharField(max_length=50, verbose_name="Cargo", blank=True, null=True)

    def clean(self):
        self.primer_nombre = self.primer_nombre.title()

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"

    class Meta:
        verbose_name_plural = "Usuarios"

    @property
    def full_name(self):
        if self.segundo_nombre:
            return f"{self.primer_nombre} {self.segundo_nombre} {self.primer_apellido} {self.segundo_apellido}"
        else:
            return f"{self.primer_nombre} {self.primer_apellido} {self.segundo_apellido}"

class ConfiguracionGeneral(models.Model):
    año = models.PositiveIntegerField(unique=True)
    salario_minimo = models.DecimalField(max_digits=10, decimal_places=2)

    def valor_hora(self):
        return self.salario_minimo / Decimal('240')

    def __str__(self):
        return f"Configuración {self.año}"

class RegistroHoras(models.Model):
    # Constantes para el cálculo
    SALARIO_MINIMO = Decimal('1423500')  # Salario mínimo
    AUXILIO_TRANSPORTE = Decimal('200000')  # Auxilio de transporte
    HORAS_TRABAJADAS_MES = 220  # Horas trabajadas al mes

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
    pago_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    
    def __str__(self):
        return f"{self.usuario.username} - {self.fecha}"

    def es_domingo(self):
        return self.fecha.weekday() == 6

    def es_festivo(self):
        colombia_holidays = holidays.Colombia(years=self.fecha.year)
        return self.fecha in colombia_holidays

    def calcular_horas(self):
        entrada = datetime.combine(self.fecha, self.hora_entrada)
        salida = datetime.combine(self.fecha, self.hora_salida)

        if salida <= entrada:
            raise ValidationError("La hora de salida debe ser posterior a la hora de entrada.")

        if self.es_domingo() or self.es_festivo():
            self.calcular_horas_dominical_festivo(entrada, salida)
        else:
            self.calcular_horas_normales(entrada, salida)

def calcular_horas_normales(self, entrada, salida):
    # Definir las horas de inicio y fin para las horas normales
    inicio_horas_normales = time(6, 0)  # 6 AM
    fin_horas_normales = time(19, 0)    # 7 PM
    # Comprobar si la hora de entrada es antes de las horas normales
    if entrada.time() < inicio_horas_normales:
        entrada = entrada.replace(hour=6, minute=0)  # Ajustar la entrada a las 6 AM
    # Comprobar si la hora de salida es después de las horas normales
    if salida.time() > fin_horas_normales:
        salida = salida.replace(hour=19, minute=0)  # Ajustar la salida a las 7 PM
    # Calcular las horas normales diurnas
    if salida.time() <= fin_horas_normales:  # Cambiar <= a <= para evitar el error
        self.horas_normales_diurnas = Decimal((salida - entrada).total_seconds() / 3600)
    else:
        self.horas_normales_diurnas = Decimal((fin_horas_normales - entrada.time()).total_seconds() / 3600)
        self.horas_normales_nocturnas = Decimal((salida - fin_horas_normales).total_seconds() / 3600)

def calcular_horas_dominical_festivo(self, entrada, salida):
    fin_diurno = entrada.replace(hour=19, minute=0)
    if salida <= fin_diurno:
        self.recargo_dominical = Decimal((salida - entrada).total_seconds() / 3600)
    else:
        self.recargo_dominical = Decimal((fin_diurno - entrada).total_seconds() / 3600)
        self.recargo_nocturno = Decimal((salida - fin_diurno).total_seconds() / 3600)

def calcular_pago_total(self):
    # Calcular el valor de la hora ordinaria
    valor_hora = (self.SALARIO_MINIMO + self.AUXILIO_TRANSPORTE) / self.HORAS_TRABAJADAS_MES

    # Calcular el pago total
    pago_total = (
        self.horas_normales_diurnas * valor_hora +
        self.horas_normales_nocturnas * valor_hora * Decimal('1.35') +
        self.horas_extras_diurnas * valor_hora * Decimal('1.25') +
        self.horas_extras_nocturnas * valor_hora * Decimal('1.75') +
        self.recargo_nocturno * valor_hora * Decimal('0.35') +
        self.recargo_dominical * valor_hora * Decimal('0.75') +
        self.recargo_festivo * valor_hora * Decimal('0.75')
    )
    return pago_total.quantize(Decimal('1.00'))

@property
def pago_total(self):
    return self.calcular_pago_total()

def save(self, *args, **kwargs):
    self.calcular_horas()
    self.pago_total = self.calcular_pago_total()
    super().save(*args, **kwargs)

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
