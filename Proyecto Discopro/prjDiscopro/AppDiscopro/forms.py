from django import forms
from .models import Farmacia, Motorista, Moto, ContactoEmergencia, LicenciaMotorista, DocumentacionMoto, Despacho, Incidencia, TipoDespacho

# Formularios (ModelForm y Form) usados por las vistas:
# - Los ModelForm encapsulan validación y mapeo entre HTML y modelo.
# - Widgets definen clases CSS y tipos (date, time) para consistencia UI.
# - Validación adicional puede implementarse con clean_<field> o clean().
# Consideración de seguridad:
# - Usar la validación de Django evita inyección directa en los modelos.
# - Los datos post siempre deben revalidarse en vistas antes de guardar.

class FarmaciaForm(forms.ModelForm):
    class Meta:
        model = Farmacia
        fields = ['codigo_farmacia', 'nombre_farmacia', 'direccion', 'id_comuna', 
                  'horario_apertura', 'horario_cierre', 'telefono', 'latitud', 'longitud']
        widgets = {
            'codigo_farmacia': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombre_farmacia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la farmacia'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'id_comuna': forms.Select(attrs={'class': 'form-control'}),
            'horario_apertura': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horario_cierre': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56...'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'placeholder': '-33.000000'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'placeholder': '-70.000000'}),
        }
        labels = {
            'codigo_farmacia': 'Código',
            'nombre_farmacia': 'Nombre',
            'id_comuna': 'Comuna',
            'horario_apertura': 'Apertura',
            'horario_cierre': 'Cierre',
        }


class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = ['codigo_motorista', 'rut', 'pasaporte', 'nombre', 'apellido_paterno', 
                  'apellido_materno', 'fecha_nacimiento', 'direccion', 'id_comuna', 
                  'telefono', 'correo', 'incluye_moto_personal']
        widgets = {
            'codigo_motorista': forms.NumberInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XX.XXX.XXX-X'}),
            'pasaporte': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'id_comuna': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'incluye_moto_personal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'codigo_motorista': 'Código',
            'apellido_paterno': 'Apellido Paterno',
            'apellido_materno': 'Apellido Materno',
            'fecha_nacimiento': 'Fecha Nacimiento',
            'id_comuna': 'Comuna',
            'correo': 'Correo Electrónico',
            'incluye_moto_personal': '¿Incluye Moto Personal?',
        }


class ContactoEmergenciaForm(forms.ModelForm):
    class Meta:
        model = ContactoEmergencia
        fields = ['nombre_completo', 'parentesco', 'telefono']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'parentesco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Madre, Hermano, Cónyuge'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }


class LicenciaMotoristaForm(forms.ModelForm):
    class Meta:
        model = LicenciaMotorista
        fields = ['tipo_licencia', 'fecha_control', 'fecha_vencimiento', 'ruta_adjunto_archivo']
        widgets = {
            'tipo_licencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: A, B, C, etc'}),
            'fecha_control': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ruta_adjunto_archivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ruta del archivo'}),
        }
        labels = {
            'tipo_licencia': 'Tipo de Licencia',
            'fecha_control': 'Último Control',
            'fecha_vencimiento': 'Vencimiento',
            'ruta_adjunto_archivo': 'Archivo',
        }


class MotoForm(forms.ModelForm):
    propietario_choices = [('Empresa', 'Empresa'), ('Motorista', 'Motorista')]
    propietario_moto = forms.ChoiceField(
        choices=propietario_choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Moto
        fields = ['codigo_moto', 'patente', 'marca', 'modelo', 'color', 'anio', 
                  'numero_chasis', 'motor', 'propietario_moto', 'id_motorista_asignado']
        widgets = {
            'codigo_moto': forms.NumberInput(attrs={'class': 'form-control'}),
            'patente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABCD-12'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_chasis': forms.TextInput(attrs={'class': 'form-control'}),
            'motor': forms.TextInput(attrs={'class': 'form-control'}),
            'id_motorista_asignado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'codigo_moto': 'Código',
            'numero_chasis': 'Número de Chasis',
            'id_motorista_asignado': 'Motorista Asignado',
        }


class DocumentacionMotoForm(forms.ModelForm):
    documento_choices = [
        ('Permiso de Circulación', 'Permiso de Circulación'),
        ('Seguro Obligatorio', 'Seguro Obligatorio'),
        ('Revisión Técnica', 'Revisión Técnica')
    ]
    tipo_documento = forms.ChoiceField(
        choices=documento_choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = DocumentacionMoto
        fields = ['anio', 'tipo_documento', 'ruta_adjunto_archivo', 'fecha_vencimiento']
        widgets = {
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'ruta_adjunto_archivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ruta del archivo'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'tipo_documento': 'Tipo de Documento',
            'ruta_adjunto_archivo': 'Archivo',
            'fecha_vencimiento': 'Vencimiento',
        }

class DespachoBaseForm(forms.ModelForm):
    """Formulario base para todos los tipos de despacho"""
    class Meta:
        model = Despacho
        fields = ['codigo_orden_farmacia', 'id_farmacia_origen', 'id_motorista', 
                  'id_moto', 'direccion_entrega', 'observaciones']
        widgets = {
            'codigo_orden_farmacia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de orden de la farmacia'
            }),
            'id_farmacia_origen': forms.Select(attrs={'class': 'form-control'}),
            'id_motorista': forms.Select(attrs={'class': 'form-control'}),
            'id_moto': forms.Select(attrs={'class': 'form-control'}),
            'direccion_entrega': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa de entrega'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales (opcional)'
            }),
        }
        labels = {
            'codigo_orden_farmacia': 'Código de Orden',
            'id_farmacia_origen': 'Farmacia Origen',
            'id_motorista': 'Motorista Asignado',
            'id_moto': 'Moto',
            'direccion_entrega': 'Dirección de Entrega',
            'observaciones': 'Observaciones',
        }


class DespachoDirectoForm(DespachoBaseForm):
    """Formulario para despacho directo"""
    pass


class DespachoConRecetaForm(DespachoBaseForm):
    """Formulario para despacho con receta"""
    numero_receta = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de receta'
        }),
        label='Número de Receta'
    )
    nombre_medico = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del médico'
        }),
        label='Médico'
    )
    fecha_emision_receta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha de Emisión'
    )
    observaciones_receta = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Observaciones de la receta'
        }),
        label='Observaciones de Receta'
    )


class DespachoConTrasladoForm(DespachoBaseForm):
    """Formulario para despacho con traslado"""
    class Meta(DespachoBaseForm.Meta):
        fields = DespachoBaseForm.Meta.fields + ['id_farmacia_origen_secundaria']
        widgets = {
            **DespachoBaseForm.Meta.widgets,
            'id_farmacia_origen_secundaria': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
        }
        labels = {
            **DespachoBaseForm.Meta.labels,
            'id_farmacia_origen_secundaria': 'Farmacia Secundaria (Con Stock)',
        }


class DespachoConReenvioForm(forms.ModelForm):
    """Formulario para despacho con reenvío"""
    id_despacho_original = forms.ModelChoiceField(
        queryset=Despacho.objects.filter(estado='FALLIDO'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Despacho Original',
        help_text='Seleccione el despacho fallido que desea reenviar'
    )
    
    class Meta:
        model = Despacho
        fields = ['id_despacho_original', 'id_motorista', 'id_moto', 
                  'direccion_entrega', 'observaciones']
        widgets = {
            'id_motorista': forms.Select(attrs={'class': 'form-control'}),
            'id_moto': forms.Select(attrs={'class': 'form-control'}),
            'direccion_entrega': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección de entrega (mantener o modificar)'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Motivo del reenvío y observaciones'
            }),
        }
        labels = {
            'id_motorista': 'Motorista para Reenvío',
            'id_moto': 'Moto',
            'direccion_entrega': 'Dirección de Entrega',
            'observaciones': 'Observaciones del Reenvío',
        }


class ModificarDespachoForm(forms.ModelForm):
    """Formulario para modificar un despacho existente"""
    class Meta:
        model = Despacho
        fields = ['id_motorista', 'id_moto', 'direccion_entrega', 'estado', 'observaciones']
        widgets = {
            'id_motorista': forms.Select(attrs={'class': 'form-control'}),
            'id_moto': forms.Select(attrs={'class': 'form-control'}),
            'direccion_entrega': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'id_motorista': 'Motorista',
            'id_moto': 'Moto',
            'direccion_entrega': 'Dirección de Entrega',
            'estado': 'Estado',
            'observaciones': 'Observaciones',
        }


class IncidenciaForm(forms.ModelForm):
    """Formulario para registrar incidencias"""
    class Meta:
        model = Incidencia
        fields = ['tipo_incidencia', 'descripcion']
        widgets = {
            'tipo_incidencia': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa la incidencia en detalle'
            }),
        }
        labels = {
            'tipo_incidencia': 'Tipo de Incidencia',
            'descripcion': 'Descripción',
        }


class FiltroReporteForm(forms.Form):
    """Formulario para filtros de reportes"""
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha Inicio'
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha Fin'
    )
    id_region = forms.ModelChoiceField(
        queryset=None,  # Se establecerá en __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Región',
        empty_label='Todas las regiones'
    )
    id_tipo_despacho = forms.ModelChoiceField(
        queryset=TipoDespacho.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Despacho',
        empty_label='Todos los tipos'
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + Despacho.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Region
        self.fields['id_region'].queryset = Region.objects.all()