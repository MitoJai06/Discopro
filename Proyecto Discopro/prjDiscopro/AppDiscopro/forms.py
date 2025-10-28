from django import forms
from .models import Farmacia, Motorista, Moto, ContactoEmergencia, LicenciaMotorista, DocumentacionMoto

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