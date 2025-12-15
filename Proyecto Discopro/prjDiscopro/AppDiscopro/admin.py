"""
Configuración del panel de administración de Django
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    UsuarioPersonalizado, Rol, Farmacia, Motorista, Moto, 
    Comuna, Region, ContactoEmergencia, LicenciaMotorista,
    DocumentacionMoto, AsignacionMotoristaFarmacia, Despacho,
    TipoDespacho, RecetaDespacho, Incidencia
)


# ============= ADMIN USUARIO PERSONALIZADO =============

@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(BaseUserAdmin):
    """Configuración del admin para usuarios personalizados"""
    
    list_display = ['nombre_usuario', 'nombre_completo', 'correo', 'get_rol_badge', 'is_active', 'ultimo_acceso']
    list_filter = ['id_rol', 'is_active', 'is_staff', 'fecha_creacion']
    search_fields = ['nombre_usuario', 'nombre_completo', 'correo']
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        (None, {
            'fields': ('nombre_usuario', 'password')
        }),
        ('Información Personal', {
            'fields': ('nombre_completo', 'correo', 'telefono')
        }),
        ('Permisos', {
            'fields': ('id_rol', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_creacion', 'ultimo_acceso', 'last_login')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nombre_usuario', 'correo', 'nombre_completo', 'id_rol', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'ultimo_acceso', 'last_login']
    
    def get_rol_badge(self, obj):
        """Mostrar el rol con color"""
        colors = {
            'GERENTE': 'red',
            'SUPERVISOR': 'orange',
            'OPERADORA': 'green'
        }
        color = colors.get(obj.id_rol.nombre_rol, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_rol_display()
        )
    get_rol_badge.short_description = 'Rol'


# ============= ADMIN ROL =============

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['id_rol', 'get_nombre_display', 'descripcion', 'total_usuarios']
    search_fields = ['nombre_rol', 'descripcion']
    
    def get_nombre_display(self, obj):
        return obj.get_nombre_rol_display()
    get_nombre_display.short_description = 'Nombre'
    
    def total_usuarios(self, obj):
        return obj.usuarios.count()
    total_usuarios.short_description = 'Total Usuarios'


# ============= ADMIN DESPACHO =============

class IncidenciaInline(admin.TabularInline):
    model = Incidencia
    extra = 0
    fields = ['tipo_incidencia', 'descripcion', 'fecha_incidencia', 'resuelto']
    readonly_fields = ['fecha_incidencia']


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ['id_despacho', 'fecha_creacion', 'id_tipo_despacho', 'get_estado_badge', 
                    'id_farmacia_origen', 'id_motorista', 'creado_por']
    list_filter = ['estado', 'id_tipo_despacho', 'fecha_creacion']
    search_fields = ['id_despacho', 'codigo_orden_farmacia', 'direccion_entrega']
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ['fecha_creacion', 'fecha_finalizacion']
    inlines = [IncidenciaInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('id_tipo_despacho', 'estado', 'codigo_orden_farmacia', 'creado_por')
        }),
        ('Origen y Destino', {
            'fields': ('id_farmacia_origen', 'id_farmacia_origen_secundaria', 'direccion_entrega')
        }),
        ('Asignación', {
            'fields': ('id_motorista', 'id_moto')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_finalizacion')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )
    
    def get_estado_badge(self, obj):
        """Mostrar el estado con color"""
        colors = {
            'CREADO': 'gray',
            'ASIGNADO': 'blue',
            'EN_CURSO': 'orange',
            'FINALIZADO': 'green',
            'CANCELADO': 'black',
            'FALLIDO': 'red'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    get_estado_badge.short_description = 'Estado'


# ============= ADMIN FARMACIA =============

class AsignacionMotoristaInline(admin.TabularInline):
    model = AsignacionMotoristaFarmacia
    extra = 0
    fields = ['id_motorista', 'fecha_asignacion', 'es_activo']
    readonly_fields = ['fecha_asignacion']


@admin.register(Farmacia)
class FarmaciaAdmin(admin.ModelAdmin):
    list_display = ['codigo_farmacia', 'nombre_farmacia', 'direccion', 'telefono', 'id_comuna']
    list_filter = ['id_comuna__id_region']
    search_fields = ['nombre_farmacia', 'direccion', 'telefono']
    inlines = [AsignacionMotoristaInline]


# ============= ADMIN MOTORISTA =============

class ContactoEmergenciaInline(admin.TabularInline):
    model = ContactoEmergencia
    extra = 1


class LicenciaMotoristaInline(admin.StackedInline):
    model = LicenciaMotorista
    extra = 0
    max_num = 1


@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ['codigo_motorista', 'get_nombre_completo', 'rut', 'telefono', 'correo', 'incluye_moto_personal']
    list_filter = ['incluye_moto_personal', 'id_comuna__id_region']
    search_fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'rut', 'correo']
    inlines = [ContactoEmergenciaInline, LicenciaMotoristaInline]
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido_paterno} {obj.apellido_materno}"
    get_nombre_completo.short_description = 'Nombre Completo'


# ============= ADMIN MOTO =============

class DocumentacionMotoInline(admin.TabularInline):
    model = DocumentacionMoto
    extra = 0
    fields = ['anio', 'tipo_documento', 'fecha_vencimiento', 'ruta_adjunto_archivo']


@admin.register(Moto)
class MotoAdmin(admin.ModelAdmin):
    list_display = ['codigo_moto', 'patente', 'marca', 'modelo', 'anio', 'propietario_moto', 'id_motorista_asignado']
    list_filter = ['propietario_moto', 'marca']
    search_fields = ['patente', 'numero_chasis', 'marca', 'modelo']
    inlines = [DocumentacionMotoInline]


# ============= OTROS MODELOS =============

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['id_region', 'nombre_region']
    search_fields = ['nombre_region']


@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    list_display = ['id_comuna', 'nombre_comuna', 'id_region']
    list_filter = ['id_region']
    search_fields = ['nombre_comuna']


@admin.register(TipoDespacho)
class TipoDespachoAdmin(admin.ModelAdmin):
    list_display = ['id_tipo_despacho', 'nombre_tipo', 'descripcion']
    search_fields = ['nombre_tipo']


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ['id_incidencia', 'id_despacho', 'tipo_incidencia', 'fecha_incidencia', 'resuelto']
    list_filter = ['tipo_incidencia', 'resuelto', 'fecha_incidencia']
    search_fields = ['descripcion']
    date_hierarchy = 'fecha_incidencia'


@admin.register(RecetaDespacho)
class RecetaDespachoAdmin(admin.ModelAdmin):
    list_display = ['id_receta', 'id_despacho', 'numero_receta', 'nombre_medico', 'fecha_emision']
    search_fields = ['numero_receta', 'nombre_medico']
    date_hierarchy = 'fecha_emision'


# Personalizar el título del admin
admin.site.site_header = "LogiCo - Administración"
admin.site.site_title = "LogiCo Admin"
admin.site.index_title = "Panel de Administración"