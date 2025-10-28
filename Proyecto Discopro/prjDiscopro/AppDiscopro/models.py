from django.db import models


class Comuna(models.Model):
    id_comuna = models.IntegerField(db_column='ID_COMUNA', primary_key=True)  # Field name made lowercase.
    nombre_comuna = models.CharField(db_column='NOMBRE_COMUNA', max_length=50)  # Field name made lowercase.
    id_region = models.ForeignKey('Region', models.DO_NOTHING, db_column='ID_REGION')  # Field name made lowercase.

    class Meta:
        db_table = 'comuna'
    
    def __str__(self):
        return f"{self.nombre_comuna} ({self.id_comuna})"


class ContactoEmergencia(models.Model):
    id_contacto = models.AutoField(db_column='ID_CONTACTO', primary_key=True)  # Field name made lowercase.
    id_motorista = models.ForeignKey('Motorista', models.DO_NOTHING, db_column='ID_MOTORISTA')  # Field name made lowercase.
    nombre_completo = models.CharField(db_column='NOMBRE_COMPLETO', max_length=100)  # Field name made lowercase.
    parentesco = models.CharField(db_column='PARENTESCO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=20)  # Field name made lowercase.

    class Meta:
        db_table = 'contacto_emergencia'


class Despacho(models.Model):
    id_despacho = models.IntegerField(db_column='ID_DESPACHO', primary_key=True)  # Field name made lowercase.
    fecha_creacion = models.DateTimeField(db_column='FECHA_CREACION')  # Field name made lowercase.
    id_tipo_despacho = models.ForeignKey('TipoDespacho', models.DO_NOTHING, db_column='ID_TIPO_DESPACHO')  # Field name made lowercase.
    id_farmacia_origen = models.ForeignKey('Farmacia', models.DO_NOTHING, db_column='ID_FARMACIA_ORIGEN')  # Field name made lowercase.
    id_farmacia_origen_secundaria = models.ForeignKey('Farmacia', models.DO_NOTHING, db_column='ID_FARMACIA_ORIGEN_SECUNDARIA', related_name='despacho_id_farmacia_origen_secundaria_set', blank=True, null=True)  # Field name made lowercase.
    id_motorista = models.ForeignKey('Motorista', models.DO_NOTHING, db_column='ID_MOTORISTA')  # Field name made lowercase.
    id_moto = models.ForeignKey('Moto', models.DO_NOTHING, db_column='ID_MOTO')  # Field name made lowercase.
    direccion_entrega = models.CharField(db_column='DIRECCION_ENTREGA', max_length=200)  # Field name made lowercase.
    estado = models.CharField(db_column='ESTADO', max_length=10)  # Field name made lowercase.
    codigo_orden_farmacia = models.CharField(db_column='CODIGO_ORDEN_FARMACIA', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'despacho'


class DocumentacionMoto(models.Model):
    id_documento = models.AutoField(db_column='ID_DOCUMENTO', primary_key=True)  # Field name made lowercase.
    id_moto = models.ForeignKey('Moto', models.DO_NOTHING, db_column='ID_MOTO')  # Field name made lowercase.
    anio = models.IntegerField(db_column='ANIO')  # Field name made lowercase.
    tipo_documento = models.CharField(db_column='TIPO_DOCUMENTO', max_length=19)  # Field name made lowercase.
    ruta_adjunto_archivo = models.CharField(db_column='RUTA_ADJUNTO_ARCHIVO', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_vencimiento = models.DateField(db_column='FECHA_VENCIMIENTO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'documentacion_moto'
        unique_together = (('id_moto', 'anio', 'tipo_documento'),)


class Farmacia(models.Model):
    codigo_farmacia = models.IntegerField(db_column='CODIGO_FARMACIA', primary_key=True)  # Field name made lowercase.
    nombre_farmacia = models.CharField(db_column='NOMBRE_FARMACIA', max_length=50)  # Field name made lowercase.
    direccion = models.CharField(db_column='DIRECCION', max_length=150)  # Field name made lowercase.
    id_comuna = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='ID_COMUNA', blank=True, null=True)  # Field name made lowercase.
    horario_apertura = models.TimeField(db_column='HORARIO_APERTURA', blank=True, null=True)  # Field name made lowercase.
    horario_cierre = models.TimeField(db_column='HORARIO_CIERRE', blank=True, null=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', unique=True, max_length=20)  # Field name made lowercase.
    latitud = models.DecimalField(db_column='LATITUD', max_digits=9, decimal_places=6, blank=True, null=True)  # Field name made lowercase.
    longitud = models.DecimalField(db_column='LONGITUD', max_digits=9, decimal_places=6, blank=True, null=True)  # Field name made lowercase.
    motoristas_asignados = models.ManyToManyField('Motorista', through='AsignacionMotoristaFarmacia', related_name='farmacias_asignadas')

    class Meta:
        db_table = 'farmacia'

    def __str__(self):
        return self.nombre_farmacia


class AsignacionMotoristaFarmacia(models.Model):
    id_asignacion = models.AutoField(primary_key=True)
    id_farmacia = models.ForeignKey('Farmacia', on_delete=models.CASCADE, db_column='ID_FARMACIA')
    id_motorista = models.ForeignKey('Motorista', on_delete=models.CASCADE, db_column='ID_MOTORISTA')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    es_activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'asignacion_motorista_farmacia'
        unique_together = ('id_farmacia', 'id_motorista')
    
    def __str__(self):
        return f"{self.id_motorista} -> {self.id_farmacia}"


class LicenciaMotorista(models.Model):
    id_licencia = models.AutoField(db_column='ID_LICENCIA', primary_key=True)  # Field name made lowercase.
    id_motorista = models.OneToOneField('Motorista', models.DO_NOTHING, db_column='ID_MOTORISTA')  # Field name made lowercase.
    tipo_licencia = models.CharField(db_column='TIPO_LICENCIA', max_length=10, blank=True, null=True)  # Field name made lowercase.
    fecha_control = models.DateField(db_column='FECHA_CONTROL', blank=True, null=True)  # Field name made lowercase.
    fecha_vencimiento = models.DateField(db_column='FECHA_VENCIMIENTO')  # Field name made lowercase.
    ruta_adjunto_archivo = models.CharField(db_column='RUTA_ADJUNTO_ARCHIVO', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'licencia_motorista'


class Moto(models.Model):
    codigo_moto = models.IntegerField(db_column='CODIGO_MOTO', primary_key=True)  # Field name made lowercase.
    patente = models.CharField(db_column='PATENTE', unique=True, max_length=10)  # Field name made lowercase.
    marca = models.CharField(db_column='MARCA', max_length=50, blank=True, null=True)  # Field name made lowercase.
    modelo = models.CharField(db_column='MODELO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    color = models.CharField(db_column='COLOR', max_length=20, blank=True, null=True)  # Field name made lowercase.
    anio = models.TextField(db_column='ANIO', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    numero_chasis = models.CharField(db_column='NUMERO_CHASIS', unique=True, max_length=17)  # Field name made lowercase.
    motor = models.CharField(db_column='MOTOR', max_length=50, blank=True, null=True)  # Field name made lowercase.
    propietario_moto = models.CharField(db_column='PROPIETARIO_MOTO', max_length=9)  # Field name made lowercase.
    id_motorista_asignado = models.OneToOneField('Motorista', models.DO_NOTHING, db_column='ID_MOTORISTA_ASIGNADO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'moto'

    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo}"


class Motorista(models.Model):
    codigo_motorista = models.IntegerField(db_column='CODIGO_MOTORISTA', primary_key=True)  # Field name made lowercase.
    rut = models.CharField(db_column='RUT', unique=True, max_length=12)  # Field name made lowercase.
    pasaporte = models.CharField(db_column='PASAPORTE', unique=True, max_length=12, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=30)  # Field name made lowercase.
    apellido_paterno = models.CharField(db_column='APELLIDO_PATERNO', max_length=30)  # Field name made lowercase.
    apellido_materno = models.CharField(db_column='APELLIDO_MATERNO', max_length=30)  # Field name made lowercase.
    fecha_nacimiento = models.DateField(db_column='FECHA_NACIMIENTO')  # Field name made lowercase.
    direccion = models.CharField(db_column='DIRECCION', max_length=100, blank=True, null=True)  # Field name made lowercase.
    id_comuna = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='ID_COMUNA', blank=True, null=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=20)  # Field name made lowercase.
    correo = models.CharField(db_column='CORREO', unique=True, max_length=50)  # Field name made lowercase.
    incluye_moto_personal = models.IntegerField(db_column='INCLUYE_MOTO_PERSONAL')  # Field name made lowercase.

    class Meta:
        db_table = 'motorista'

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} ({self.rut})"


class Region(models.Model):
    id_region = models.IntegerField(db_column='ID_REGION', primary_key=True)  # Field name made lowercase.
    nombre_region = models.CharField(db_column='NOMBRE_REGION', max_length=50)  # Field name made lowercase.

    class Meta:
        db_table = 'region'
    
    def __str__(self):
        return self.nombre_region


class Rol(models.Model):
    id_rol = models.IntegerField(db_column='ID_ROL', primary_key=True)  # Field name made lowercase.
    nombre_rol = models.CharField(db_column='NOMBRE_ROL', unique=True, max_length=20)  # Field name made lowercase.

    class Meta:
        db_table = 'rol'


class TipoDespacho(models.Model):
    id_tipo_despacho = models.IntegerField(db_column='ID_TIPO_DESPACHO', primary_key=True)  # Field name made lowercase.
    nombre_tipo = models.CharField(db_column='NOMBRE_TIPO', unique=True, max_length=50)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'tipo_despacho'


class Usuario(models.Model):
    id_usuario = models.IntegerField(db_column='ID_USUARIO', primary_key=True)  # Field name made lowercase.
    nombre_usuario = models.CharField(db_column='NOMBRE_USUARIO', unique=True, max_length=50)  # Field name made lowercase.
    clave_hash = models.CharField(db_column='CLAVE_HASH', max_length=255)  # Field name made lowercase.
    nombre_completo = models.CharField(db_column='NOMBRE_COMPLETO', max_length=100)  # Field name made lowercase.
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='ID_ROL')  # Field name made lowercase.

    class Meta:
        db_table = 'usuario'