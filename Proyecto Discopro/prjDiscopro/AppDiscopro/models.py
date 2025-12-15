from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission
from django.utils import timezone


# ============= GESTOR DE USUARIOS PERSONALIZADO =============

class UsuarioManager(BaseUserManager):
    """Gestor personalizado para el modelo Usuario"""
    
    def create_user(self, nombre_usuario, correo, password=None, **extra_fields):
        """Crea y guarda un usuario regular"""
        if not nombre_usuario:
            raise ValueError('El usuario debe tener un nombre de usuario')
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        
        correo = self.normalize_email(correo)
        user = self.model(
            nombre_usuario=nombre_usuario,
            correo=correo,
            **extra_fields
        )
        user.set_password(password)  # Hash automático
        user.save(using=self._db)
        return user
    
    def create_superuser(self, nombre_usuario, correo, password=None, **extra_fields):
        """Crea y guarda un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        # Asignar rol de Gerente por defecto a superusuarios
        if 'id_rol' not in extra_fields:
            rol_gerente, _ = Rol.objects.get_or_create(
                nombre_rol='GERENTE',
                defaults={'id_rol': 1}
            )
            extra_fields['id_rol'] = rol_gerente
        
        return self.create_user(nombre_usuario, correo, password, **extra_fields)


# ============= MODELOS BÁSICOS =============

class Rol(models.Model):
    """Roles del sistema: GERENTE, SUPERVISOR, OPERADORA"""
    ROLES_CHOICES = [
        ('GERENTE', 'Gerente'),
        ('SUPERVISOR', 'Supervisor'),
        ('OPERADORA', 'Operadora'),
    ]
    
    id_rol = models.AutoField(db_column='ID_ROL', primary_key=True)
    nombre_rol = models.CharField(
        db_column='NOMBRE_ROL', 
        unique=True, 
        max_length=20,
        choices=ROLES_CHOICES
    )
    descripcion = models.TextField(db_column='DESCRIPCION', blank=True, null=True)

    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.get_nombre_rol_display()


class UsuarioPersonalizado(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuario personalizado con roles"""
    
    id_usuario = models.AutoField(db_column='ID_USUARIO', primary_key=True)
    nombre_usuario = models.CharField(
        db_column='NOMBRE_USUARIO', 
        unique=True, 
        max_length=50
    )
    correo = models.EmailField(
        db_column='CORREO',
        unique=True,
        max_length=100
    )
    nombre_completo = models.CharField(
        db_column='NOMBRE_COMPLETO', 
        max_length=100
    )
    
    password = models.CharField(db_column='pswd', max_length=255, blank=True)
    id_rol = models.ForeignKey(
        Rol, 
        on_delete=models.PROTECT, 
        db_column='ID_ROL',
        related_name='usuarios'
    )
    
    # Campos adicionales
    telefono = models.CharField(
        db_column='TELEFONO',
        max_length=20,
        blank=True,
        null=True
    )
    fecha_creacion = models.DateTimeField(
        db_column='FECHA_CREACION',
        default=timezone.now
    )
    ultimo_acceso = models.DateTimeField(
        db_column='ULTIMO_ACCESO',
        blank=True,
        null=True
    )
    
    # Campos requeridos por Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Re-definimos explícitamente las relaciones ManyToMany para grupos y permisos
    # con related_name únicos para evitar colisiones con el modelo `auth.User`.
    groups = models.ManyToManyField(
        Group,
        related_name='appdiscopro_usuariopersonalizado_set',
        blank=True,
        help_text='Grupos a los que pertenece el usuario',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='appdiscopro_usuariopersonalizado_permissions_set',
        blank=True,
        help_text='Permisos específicos del usuario',
    )
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['correo', 'nombre_completo']
    
    class Meta:
        db_table = 'usuario_personalizado'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre_completo} ({self.nombre_usuario})"
    
    def get_rol_display(self):
        """Retorna el nombre del rol"""
        return self.id_rol.get_nombre_rol_display() if self.id_rol else 'Sin rol'
    
    def es_gerente(self):
        """Verifica si el usuario es gerente"""
        return self.id_rol.nombre_rol == 'GERENTE'
    
    def es_supervisor(self):
        """Verifica si el usuario es supervisor"""
        return self.id_rol.nombre_rol == 'SUPERVISOR'
    
    def es_operadora(self):
        """Verifica si el usuario es operadora"""
        return self.id_rol.nombre_rol == 'OPERADORA'
    
    def tiene_permiso_crear_despacho(self):
        """Verifica si puede crear despachos"""
        return self.id_rol.nombre_rol in ['GERENTE', 'OPERADORA']
    
    def tiene_permiso_ver_reportes(self):
        """Verifica si puede ver reportes completos"""
        return self.id_rol.nombre_rol in ['GERENTE', 'SUPERVISOR']
    
    def tiene_permiso_gestionar_usuarios(self):
        """Verifica si puede gestionar usuarios"""
        return self.id_rol.nombre_rol == 'GERENTE'


# ============= MODELOS GEOGRÁFICOS =============

class Region(models.Model):
    id_region = models.IntegerField(db_column='ID_REGION', primary_key=True)
    nombre_region = models.CharField(db_column='NOMBRE_REGION', max_length=50)

    class Meta:
        db_table = 'region'
        verbose_name = 'Región'
        verbose_name_plural = 'Regiones'
    
    def __str__(self):
        return self.nombre_region


class Comuna(models.Model):
    id_comuna = models.IntegerField(db_column='ID_COMUNA', primary_key=True)
    nombre_comuna = models.CharField(db_column='NOMBRE_COMUNA', max_length=50)
    id_region = models.ForeignKey('Region', models.DO_NOTHING, db_column='ID_REGION')

    class Meta:
        db_table = 'comuna'
        verbose_name = 'Comuna'
        verbose_name_plural = 'Comunas'
    
    def __str__(self):
        return f"{self.nombre_comuna} ({self.id_comuna})"


# ============= MODELOS DE NEGOCIO =============

class Farmacia(models.Model):
    codigo_farmacia = models.IntegerField(db_column='CODIGO_FARMACIA', primary_key=True)
    nombre_farmacia = models.CharField(db_column='NOMBRE_FARMACIA', max_length=50)
    direccion = models.CharField(db_column='DIRECCION', max_length=150)
    id_comuna = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='ID_COMUNA', blank=True, null=True)
    horario_apertura = models.TimeField(db_column='HORARIO_APERTURA', blank=True, null=True)
    horario_cierre = models.TimeField(db_column='HORARIO_CIERRE', blank=True, null=True)
    telefono = models.CharField(db_column='TELEFONO', unique=True, max_length=20)
    latitud = models.DecimalField(db_column='LATITUD', max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(db_column='LONGITUD', max_digits=9, decimal_places=6, blank=True, null=True)
    motoristas_asignados = models.ManyToManyField('Motorista', through='AsignacionMotoristaFarmacia', related_name='farmacias_asignadas')

    class Meta:
        db_table = 'farmacia'
        verbose_name = 'Farmacia'
        verbose_name_plural = 'Farmacias'

    def __str__(self):
        return self.nombre_farmacia


class Motorista(models.Model):
    codigo_motorista = models.IntegerField(db_column='CODIGO_MOTORISTA', primary_key=True)
    rut = models.CharField(db_column='RUT', unique=True, max_length=12)
    pasaporte = models.CharField(db_column='PASAPORTE', unique=True, max_length=12, blank=True, null=True)
    nombre = models.CharField(db_column='NOMBRE', max_length=30)
    apellido_paterno = models.CharField(db_column='APELLIDO_PATERNO', max_length=30)
    apellido_materno = models.CharField(db_column='APELLIDO_MATERNO', max_length=30)
    fecha_nacimiento = models.DateField(db_column='FECHA_NACIMIENTO')
    direccion = models.CharField(db_column='DIRECCION', max_length=100, blank=True, null=True)
    id_comuna = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='ID_COMUNA', blank=True, null=True)
    telefono = models.CharField(db_column='TELEFONO', max_length=20)
    correo = models.CharField(db_column='CORREO', unique=True, max_length=50)
    incluye_moto_personal = models.IntegerField(db_column='INCLUYE_MOTO_PERSONAL')

    class Meta:
        db_table = 'motorista'
        verbose_name = 'Motorista'
        verbose_name_plural = 'Motoristas'

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} ({self.rut})"


class Moto(models.Model):
    codigo_moto = models.IntegerField(db_column='CODIGO_MOTO', primary_key=True)
    patente = models.CharField(db_column='PATENTE', unique=True, max_length=10)
    marca = models.CharField(db_column='MARCA', max_length=50, blank=True, null=True)
    modelo = models.CharField(db_column='MODELO', max_length=50, blank=True, null=True)
    color = models.CharField(db_column='COLOR', max_length=20, blank=True, null=True)
    anio = models.TextField(db_column='ANIO', blank=True, null=True)
    numero_chasis = models.CharField(db_column='NUMERO_CHASIS', unique=True, max_length=17)
    motor = models.CharField(db_column='MOTOR', max_length=50, blank=True, null=True)
    propietario_moto = models.CharField(db_column='PROPIETARIO_MOTO', max_length=9)
    id_motorista_asignado = models.OneToOneField('Motorista', models.DO_NOTHING, db_column='ID_MOTORISTA_ASIGNADO', blank=True, null=True)

    class Meta:
        db_table = 'moto'
        verbose_name = 'Moto'
        verbose_name_plural = 'Motos'

    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo}"


class AsignacionMotoristaFarmacia(models.Model):
    id_asignacion = models.AutoField(primary_key=True)
    id_farmacia = models.ForeignKey('Farmacia', on_delete=models.CASCADE, db_column='ID_FARMACIA')
    id_motorista = models.ForeignKey('Motorista', on_delete=models.CASCADE, db_column='ID_MOTORISTA')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    es_activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'asignacion_motorista_farmacia'
        unique_together = ('id_farmacia', 'id_motorista')
        verbose_name = 'Asignación Motorista-Farmacia'
        verbose_name_plural = 'Asignaciones Motorista-Farmacia'
    
    def __str__(self):
        return f"{self.id_motorista} -> {self.id_farmacia}"


class ContactoEmergencia(models.Model):
    id_contacto = models.AutoField(db_column='ID_CONTACTO', primary_key=True)
    id_motorista = models.ForeignKey('Motorista', models.DO_NOTHING, db_column='ID_MOTORISTA')
    nombre_completo = models.CharField(db_column='NOMBRE_COMPLETO', max_length=100)
    parentesco = models.CharField(db_column='PARENTESCO', max_length=50, blank=True, null=True)
    telefono = models.CharField(db_column='TELEFONO', max_length=20)

    class Meta:
        db_table = 'contacto_emergencia'
        verbose_name = 'Contacto de Emergencia'
        verbose_name_plural = 'Contactos de Emergencia'


class LicenciaMotorista(models.Model):
    id_licencia = models.AutoField(db_column='ID_LICENCIA', primary_key=True)
    id_motorista = models.OneToOneField('Motorista', models.DO_NOTHING, db_column='ID_MOTORISTA')
    tipo_licencia = models.CharField(db_column='TIPO_LICENCIA', max_length=10, blank=True, null=True)
    fecha_control = models.DateField(db_column='FECHA_CONTROL', blank=True, null=True)
    fecha_vencimiento = models.DateField(db_column='FECHA_VENCIMIENTO')
    ruta_adjunto_archivo = models.CharField(db_column='RUTA_ADJUNTO_ARCHIVO', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'licencia_motorista'
        verbose_name = 'Licencia de Motorista'
        verbose_name_plural = 'Licencias de Motoristas'


class DocumentacionMoto(models.Model):
    id_documento = models.AutoField(db_column='ID_DOCUMENTO', primary_key=True)
    id_moto = models.ForeignKey('Moto', models.DO_NOTHING, db_column='ID_MOTO')
    anio = models.IntegerField(db_column='ANIO')
    tipo_documento = models.CharField(db_column='TIPO_DOCUMENTO', max_length=19)
    ruta_adjunto_archivo = models.CharField(db_column='RUTA_ADJUNTO_ARCHIVO', max_length=255, blank=True, null=True)
    fecha_vencimiento = models.DateField(db_column='FECHA_VENCIMIENTO', blank=True, null=True)

    class Meta:
        db_table = 'documentacion_moto'
        unique_together = (('id_moto', 'anio', 'tipo_documento'),)
        verbose_name = 'Documentación de Moto'
        verbose_name_plural = 'Documentación de Motos'


# ============= MODELOS DE DESPACHO =============

class TipoDespacho(models.Model):
    id_tipo_despacho = models.AutoField(db_column='ID_TIPO_DESPACHO', primary_key=True)
    nombre_tipo = models.CharField(db_column='NOMBRE_TIPO', unique=True, max_length=50)
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tipo_despacho'
        verbose_name = 'Tipo de Despacho'
        verbose_name_plural = 'Tipos de Despacho'
    
    def __str__(self):
        return self.nombre_tipo


class Despacho(models.Model):
    ESTADO_CHOICES = [
        ('CREADO', 'Creado'),
        ('ASIGNADO', 'Asignado'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
        ('FALLIDO', 'Fallido'),
    ]
    
    id_despacho = models.AutoField(db_column='ID_DESPACHO', primary_key=True)
    fecha_creacion = models.DateTimeField(db_column='FECHA_CREACION', auto_now_add=True)
    id_tipo_despacho = models.ForeignKey('TipoDespacho', models.DO_NOTHING, db_column='ID_TIPO_DESPACHO')
    id_farmacia_origen = models.ForeignKey('Farmacia', models.DO_NOTHING, db_column='ID_FARMACIA_ORIGEN', related_name='despachos_origen')
    id_farmacia_origen_secundaria = models.ForeignKey('Farmacia', models.DO_NOTHING, db_column='ID_FARMACIA_ORIGEN_SECUNDARIA', related_name='despachos_secundarios', blank=True, null=True)
    id_motorista = models.ForeignKey('Motorista', models.DO_NOTHING, db_column='ID_MOTORISTA')
    id_moto = models.ForeignKey('Moto', models.DO_NOTHING, db_column='ID_MOTO')
    direccion_entrega = models.CharField(db_column='DIRECCION_ENTREGA', max_length=200)
    estado = models.CharField(db_column='ESTADO', max_length=10, choices=ESTADO_CHOICES, default='CREADO')
    codigo_orden_farmacia = models.CharField(db_column='CODIGO_ORDEN_FARMACIA', max_length=50, blank=True, null=True)
    id_despacho_original = models.ForeignKey('self', models.SET_NULL, db_column='ID_DESPACHO_ORIGINAL', blank=True, null=True, related_name='reenvios')
    fecha_finalizacion = models.DateTimeField(db_column='FECHA_FINALIZACION', blank=True, null=True)
    observaciones = models.TextField(db_column='OBSERVACIONES', blank=True, null=True)
    creado_por = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despachos_creados',
        db_column='CREADO_POR'
    )

    class Meta:
        db_table = 'despacho'
        ordering = ['-fecha_creacion']
        verbose_name = 'Despacho'
        verbose_name_plural = 'Despachos'
    
    def __str__(self):
        return f"Despacho #{self.id_despacho} - {self.get_estado_display()}"


class RecetaDespacho(models.Model):
    id_receta = models.AutoField(db_column='ID_RECETA', primary_key=True)
    id_despacho = models.OneToOneField('Despacho', models.CASCADE, db_column='ID_DESPACHO', related_name='receta')
    numero_receta = models.CharField(db_column='NUMERO_RECETA', max_length=50, blank=True, null=True)
    nombre_medico = models.CharField(db_column='NOMBRE_MEDICO', max_length=100, blank=True, null=True)
    fecha_emision = models.DateField(db_column='FECHA_EMISION', blank=True, null=True)
    ruta_archivo = models.CharField(db_column='RUTA_ARCHIVO', max_length=255, blank=True, null=True)
    observaciones = models.TextField(db_column='OBSERVACIONES', blank=True, null=True)
    
    class Meta:
        db_table = 'receta_despacho'
        verbose_name = 'Receta de Despacho'
        verbose_name_plural = 'Recetas de Despacho'
    
    def __str__(self):
        return f"Receta - Despacho #{self.id_despacho.id_despacho}"


class Incidencia(models.Model):
    TIPO_INCIDENCIA_CHOICES = [
        ('CLIENTE_AUSENTE', 'Cliente Ausente'),
        ('DIRECCION_INCORRECTA', 'Dirección Incorrecta'),
        ('CLIENTE_RECHAZA', 'Cliente Rechaza Pedido'),
        ('ACCIDENTE', 'Accidente'),
        ('FALLA_MOTO', 'Falla Mecánica de Moto'),
        ('PRODUCTO_INCORRECTO', 'Producto Incorrecto'),
        ('DEMORA_TRAFICO', 'Demora por Tráfico'),
        ('OTRO', 'Otro'),
    ]
    
    id_incidencia = models.AutoField(db_column='ID_INCIDENCIA', primary_key=True)
    id_despacho = models.ForeignKey('Despacho', models.CASCADE, db_column='ID_DESPACHO', related_name='incidencias')
    tipo_incidencia = models.CharField(db_column='TIPO_INCIDENCIA', max_length=30, choices=TIPO_INCIDENCIA_CHOICES)
    descripcion = models.TextField(db_column='DESCRIPCION')
    fecha_incidencia = models.DateTimeField(db_column='FECHA_INCIDENCIA', auto_now_add=True)
    resuelto = models.BooleanField(db_column='RESUELTO', default=False)
    
    class Meta:
        db_table = 'incidencia'
        ordering = ['-fecha_incidencia']
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'
    
    def __str__(self):
        return f"Incidencia #{self.id_incidencia} - {self.get_tipo_incidencia_display()}"


# ============= MODELO ANTIGUO (MANTENER PARA COMPATIBILIDAD) =============

class Usuario(models.Model):
    """Modelo antiguo - mantener solo para compatibilidad con datos existentes"""
    id_usuario = models.IntegerField(db_column='ID_USUARIO', primary_key=True)
    nombre_usuario = models.CharField(db_column='NOMBRE_USUARIO', unique=True, max_length=50)
    clave_hash = models.CharField(db_column='CLAVE_HASH', max_length=255)
    nombre_completo = models.CharField(db_column='NOMBRE_COMPLETO', max_length=100)
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='ID_ROL')

    class Meta:
        db_table = 'usuario'
        managed = False  # No gestionar con migraciones