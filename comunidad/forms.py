# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    """Formulario completo para crear/editar usuarios"""
    username = forms.CharField(
        max_length=150,
        label="Nombre de usuario",
        help_text="Requerido. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_ son permitidos.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese nombre de usuario'
        })
    )
    
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese contraseña'
        }),
        help_text="Su contraseña debe contener al menos 8 caracteres.",
    )
    
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme contraseña'
        }),
        strip=False,
        help_text="Ingrese la misma contraseña que antes, para verificación.",
    )

    class Meta:
        model = Usuario
        fields = [
            'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'fecha_nacimiento', 'imagen', 'correo', 'tipo_documento', 'documento',
            'rol', 'departamento', 'cargo', 'telefono', 'fecha_ingreso'
        ]
        
        widgets = {
            'primer_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer nombre'
            }),
            'segundo_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo nombre (opcional)'
            }),
            'primer_apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer apellido'
            }),
            'segundo_apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo apellido'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'documento': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento'
            }),
            'rol': forms.Select(attrs={
                'class': 'form-select'
            }),
            'departamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Departamento'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es edición, no requerir contraseñas
        if self.instance and self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            self.fields['password1'].help_text = "Deje en blanco si no desea cambiar la contraseña."

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Si es edición, excluir el usuario actual
            if self.instance and self.instance.pk and hasattr(self.instance, 'user'):
                if User.objects.filter(username=username).exclude(id=self.instance.user.id).exists():
                    raise ValidationError("Ya existe un usuario con este nombre.")
            else:
                if User.objects.filter(username=username).exists():
                    raise ValidationError("Ya existe un usuario con este nombre.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        # Si no es edición o se proporcionaron contraseñas
        if not (self.instance and self.instance.pk) or password1 or password2:
            if password1 and password2 and password1 != password2:
                raise ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        usuario = super().save(commit=False)
        
        # Crear o actualizar usuario Django
        if not usuario.pk:  # Nuevo usuario
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=usuario.correo,
                password=self.cleaned_data['password1'],
                first_name=usuario.primer_nombre,
                last_name=usuario.primer_apellido
            )
            usuario.user = user
        else:  # Actualizar usuario existente
            user = usuario.user
            user.username = self.cleaned_data['username']
            user.email = usuario.correo
            user.first_name = usuario.primer_nombre
            user.last_name = usuario.primer_apellido
            
            # Solo actualizar contraseña si se proporcionó
            if self.cleaned_data.get('password1'):
                user.set_password(self.cleaned_data['password1'])
            
            user.save()
        
        if commit:
            usuario.save()
        
        return usuario

class UsuarioRegistroForm(UserCreationForm):
    """Formulario simplificado para registro público"""
    primer_nombre = forms.CharField(
        max_length=45,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Primer nombre'
        })
    )
    primer_apellido = forms.CharField(
        max_length=45,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Primer apellido'
        })
    )
    segundo_apellido = forms.CharField(
        max_length=45,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Segundo apellido'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    tipo_documento = forms.ChoiceField(
        choices=Usuario.TipoDocumento.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    documento = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de documento'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if Usuario.objects.filter(documento=documento).exists():
            raise ValidationError("Ya existe un usuario con este documento.")
        return documento

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(correo=email).exists():
            raise ValidationError("Ya existe un usuario con este correo.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['primer_nombre']
        user.last_name = self.cleaned_data['primer_apellido']
        
        if commit:
            user.save()
            
            # Crear el perfil de Usuario
            usuario = Usuario.objects.create(
                user=user,
                primer_nombre=self.cleaned_data['primer_nombre'],
                primer_apellido=self.cleaned_data['primer_apellido'],
                segundo_apellido=self.cleaned_data['segundo_apellido'],
                fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
                correo=self.cleaned_data['email'],
                tipo_documento=self.cleaned_data['tipo_documento'],
                documento=self.cleaned_data['documento'],
                rol=Usuario.RolChoices.EMPLEADO  # Por defecto empleado
            )
        
        return user

class UsuarioEditForm(forms.ModelForm):
    """Formulario para que el usuario edite su propio perfil"""
    
    class Meta:
        model = Usuario
        fields = [
            'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'imagen', 'correo', 'telefono', 'departamento', 'cargo'
        ]
        
        widgets = {
            'primer_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer nombre'
            }),
            'segundo_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo nombre'
            }),
            'primer_apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer apellido'
            }),
            'segundo_apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo apellido'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
            'departamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Departamento'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo'
            }),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        
        # Actualizar también el usuario Django
        if usuario.user:
            usuario.user.email = usuario.correo
            usuario.user.first_name = usuario.primer_nombre
            usuario.user.last_name = usuario.primer_apellido
            usuario.user.save()
        
        if commit:
            usuario.save()
        
        return usuario

class BusquedaUsuarioForm(forms.Form):
    """Formulario para buscar usuarios"""
    busqueda = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, apellido, correo o documento...'
        })
    )
    
    rol = forms.ChoiceField(
        choices=[('', 'Todos los roles')] + list(Usuario.RolChoices.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    departamento = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Departamento'
        })
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos'), ('true', 'Activos'), ('false', 'Inactivos')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )