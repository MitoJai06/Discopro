from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
from .models import (Farmacia, Motorista, Moto, ContactoEmergencia, 
                     LicenciaMotorista, DocumentacionMoto, AsignacionMotoristaFarmacia, Despacho, TipoDespacho, RecetaDespacho, Incidencia, Region, Comuna)
from .forms import (FarmaciaForm, MotoristaForm, ContactoEmergenciaForm, 
                    LicenciaMotoristaForm, MotoForm, DocumentacionMotoForm, DespachoDirectoForm, DespachoConRecetaForm, DespachoConTrasladoForm, DespachoConReenvioForm, ModificarDespachoForm, IncidenciaForm)
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

# ============= VIEWS FARMACIA =============

class FarmaciaListView(ListView):
    model = Farmacia
    template_name = 'farmacia/list.html'
    context_object_name = 'farmacias'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        
        if query:
            queryset = queryset.filter(
                Q(nombre_farmacia__icontains=query) |
                Q(direccion__icontains=query) |
                Q(telefono__icontains=query) |
                Q(codigo_farmacia__icontains=query)
            )
        
        return queryset.order_by('codigo_farmacia')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class FarmaciaCreateView(SuccessMessageMixin, CreateView):
    model = Farmacia
    form_class = FarmaciaForm
    template_name = 'farmacia/form.html'
    success_url = reverse_lazy('farmacia_list')
    success_message = "Farmacia creada exitosamente"


class FarmaciaUpdateView(SuccessMessageMixin, UpdateView):
    model = Farmacia
    form_class = FarmaciaForm
    template_name = 'farmacia/form.html'
    success_url = reverse_lazy('farmacia_list')
    success_message = "Farmacia actualizada exitosamente"


class FarmaciaDeleteView(SuccessMessageMixin, DeleteView):
    model = Farmacia
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('farmacia_list')
    success_message = "Farmacia eliminada"


def farmacia_detail(request, pk):
    """Vista detalle de farmacia con asignación de motoristas"""
    farmacia = get_object_or_404(Farmacia, codigo_farmacia=pk)
    
    # Obtener asignaciones activas
    asignaciones = AsignacionMotoristaFarmacia.objects.filter(
        id_farmacia=farmacia, 
        es_activo=True
    ).select_related('id_motorista')
    
    # Obtener motoristas disponibles (no asignados a esta farmacia)
    motoristas_asignados_ids = [a.id_motorista.codigo_motorista for a in asignaciones]
    motoristas_disponibles = Motorista.objects.exclude(codigo_motorista__in=motoristas_asignados_ids)
    
    if request.method == 'POST':
        if 'asignar_motorista' in request.POST:
            motorista_id = request.POST.get('motorista_id')
            if motorista_id:
                motorista = get_object_or_404(Motorista, codigo_motorista=motorista_id)
                AsignacionMotoristaFarmacia.objects.create(
                    id_farmacia=farmacia,
                    id_motorista=motorista,
                    es_activo=True
                )
                messages.success(request, f"Motorista {motorista.nombre} asignado exitosamente")
                return redirect('farmacia_detail', pk=pk)
        
        elif 'reemplazar_motorista' in request.POST:
            asignacion_id = request.POST.get('asignacion_id')
            nuevo_motorista_id = request.POST.get('nuevo_motorista_id')
            
            if asignacion_id and nuevo_motorista_id:
                # Desactivar asignación actual
                asignacion_actual = get_object_or_404(AsignacionMotoristaFarmacia, id_asignacion=asignacion_id)
                asignacion_actual.es_activo = False
                asignacion_actual.save()
                
                # Crear nueva asignación
                nuevo_motorista = get_object_or_404(Motorista, codigo_motorista=nuevo_motorista_id)
                AsignacionMotoristaFarmacia.objects.create(
                    id_farmacia=farmacia,
                    id_motorista=nuevo_motorista,
                    es_activo=True
                )
                messages.success(request, f"Motorista reemplazado por {nuevo_motorista.nombre}")
                return redirect('farmacia_detail', pk=pk)
        
        elif 'desasignar_motorista' in request.POST:
            asignacion_id = request.POST.get('asignacion_id')
            if asignacion_id:
                asignacion = get_object_or_404(AsignacionMotoristaFarmacia, id_asignacion=asignacion_id)
                asignacion.es_activo = False
                asignacion.save()
                messages.success(request, "Motorista desasignado exitosamente")
                return redirect('farmacia_detail', pk=pk)
    
    context = {
        'farmacia': farmacia,
        'asignaciones': asignaciones,
        'motoristas_disponibles': motoristas_disponibles,
    }
    
    return render(request, 'farmacia/detail.html', context)


# ============= VIEWS MOTORISTA =============

class MotoristaListView(ListView):
    model = Motorista
    template_name = 'motorista/list.html'
    context_object_name = 'motoristas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) |
                Q(apellido_paterno__icontains=query) |
                Q(apellido_materno__icontains=query) |
                Q(rut__icontains=query) |
                Q(correo__icontains=query) |
                Q(telefono__icontains=query) |
                Q(codigo_motorista__icontains=query)
            )
        
        return queryset.order_by('codigo_motorista')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class MotoristaCreateView(SuccessMessageMixin, CreateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'motorista/form.html'
    success_url = reverse_lazy('motorista_list')
    success_message = "Motorista creado exitosamente"


class MotoristaUpdateView(SuccessMessageMixin, UpdateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'motorista/form.html'
    success_url = reverse_lazy('motorista_list')
    success_message = "Motorista actualizado exitosamente"


class MotoristaDeleteView(SuccessMessageMixin, DeleteView):
    model = Motorista
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('motorista_list')
    success_message = "Motorista eliminado"


def motorista_detail(request, pk):
    motorista = get_object_or_404(Motorista, codigo_motorista=pk)
    contactos = motorista.contactoemergencia_set.all()
    licencia = LicenciaMotorista.objects.filter(id_motorista=motorista).first()
    
    # Obtener farmacias asignadas
    farmacias_asignadas = AsignacionMotoristaFarmacia.objects.filter(
        id_motorista=motorista,
        es_activo=True
    ).select_related('id_farmacia')
    
    if request.method == 'POST':
        if 'add_contacto' in request.POST:
            form = ContactoEmergenciaForm(request.POST)
            if form.is_valid():
                contacto = form.save(commit=False)
                contacto.id_motorista = motorista
                contacto.save()
                return redirect('motorista_detail', pk=pk)
        elif 'add_licencia' in request.POST:
            form = LicenciaMotoristaForm(request.POST)
            if form.is_valid():
                if licencia:
                    licencia.delete()
                lic = form.save(commit=False)
                lic.id_motorista = motorista
                lic.save()
                return redirect('motorista_detail', pk=pk)
    
    contacto_form = ContactoEmergenciaForm()
    licencia_form = LicenciaMotoristaForm()
    
    return render(request, 'motorista/detail.html', {
        'motorista': motorista,
        'contactos': contactos,
        'licencia': licencia,
        'contacto_form': contacto_form,
        'licencia_form': licencia_form,
        'farmacias_asignadas': farmacias_asignadas,
    })


# ============= VIEWS MOTO =============

class MotoListView(ListView):
    model = Moto
    template_name = 'moto/list.html'
    context_object_name = 'motos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        
        if query:
            queryset = queryset.filter(
                Q(patente__icontains=query) |
                Q(marca__icontains=query) |
                Q(modelo__icontains=query) |
                Q(numero_chasis__icontains=query) |
                Q(codigo_moto__icontains=query)
            )
        
        return queryset.order_by('codigo_moto')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class MotoCreateView(SuccessMessageMixin, CreateView):
    model = Moto
    form_class = MotoForm
    template_name = 'moto/form.html'
    success_url = reverse_lazy('moto_list')
    success_message = "Moto creada exitosamente"


class MotoUpdateView(SuccessMessageMixin, UpdateView):
    model = Moto
    form_class = MotoForm
    template_name = 'moto/form.html'
    success_url = reverse_lazy('moto_list')
    success_message = "Moto actualizada exitosamente"


class MotoDeleteView(SuccessMessageMixin, DeleteView):
    model = Moto
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('moto_list')
    success_message = "Moto eliminada"


def moto_detail(request, pk):
    moto = get_object_or_404(Moto, codigo_moto=pk)
    documentacion = DocumentacionMoto.objects.filter(id_moto=moto).order_by('-anio')
    
    if request.method == 'POST' and 'add_doc' in request.POST:
        form = DocumentacionMotoForm(request.POST)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.id_moto = moto
            doc.save()
            return redirect('moto_detail', pk=pk)
    
    doc_form = DocumentacionMotoForm()
    
    return render(request, 'moto/detail.html', {
        'moto': moto,
        'documentacion': documentacion,
        'doc_form': doc_form,
    })

# ============= VIEWS DESPACHO =============

class DespachoListView(ListView):
    model = Despacho
    template_name = 'despacho/list.html'
    context_object_name = 'despachos'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'id_tipo_despacho', 
            'id_farmacia_origen',
            'id_motorista',
            'id_moto'
        )
        
        # Filtros
        query = self.request.GET.get('q')
        estado = self.request.GET.get('estado')
        tipo = self.request.GET.get('tipo')
        fecha = self.request.GET.get('fecha')
        
        if query:
            queryset = queryset.filter(
                Q(id_despacho__icontains=query) |
                Q(codigo_orden_farmacia__icontains=query) |
                Q(direccion_entrega__icontains=query) |
                Q(id_motorista__nombre__icontains=query) |
                Q(id_motorista__apellido_paterno__icontains=query)
            )
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        if tipo:
            queryset = queryset.filter(id_tipo_despacho__id_tipo_despacho=tipo)
        
        if fecha:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_creacion__date=fecha_obj)
        
        return queryset.order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['estados'] = Despacho.ESTADO_CHOICES
        context['tipos_despacho'] = TipoDespacho.objects.all()
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['tipo_filtro'] = self.request.GET.get('tipo', '')
        context['fecha_filtro'] = self.request.GET.get('fecha', '')
        return context


def despacho_detail(request, pk):
    """Vista detalle de despacho con incidencias"""
    despacho = get_object_or_404(Despacho, id_despacho=pk)
    incidencias = despacho.incidencias.all()
    
    # Si es despacho con receta, obtener datos de receta
    receta = None
    if despacho.id_tipo_despacho.nombre_tipo == 'DESPACHO CON RECETA':
        receta = RecetaDespacho.objects.filter(id_despacho=despacho).first()
    
    # Si es un reenvío, mostrar despacho original
    despacho_original = despacho.id_despacho_original
    
    # Manejar registro de incidencias
    if request.method == 'POST' and 'add_incidencia' in request.POST:
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            incidencia = form.save(commit=False)
            incidencia.id_despacho = despacho
            incidencia.save()
            messages.success(request, 'Incidencia registrada exitosamente')
            return redirect('despacho_detail', pk=pk)
    
    incidencia_form = IncidenciaForm()
    
    context = {
        'despacho': despacho,
        'incidencias': incidencias,
        'receta': receta,
        'despacho_original': despacho_original,
        'incidencia_form': incidencia_form,
    }
    
    return render(request, 'despacho/detail.html', context)


def despacho_directo_create(request):
    """Crear despacho directo"""
    if request.method == 'POST':
        form = DespachoDirectoForm(request.POST)
        if form.is_valid():
            despacho = form.save(commit=False)
            despacho.id_tipo_despacho = TipoDespacho.objects.get(nombre_tipo='DESPACHO DIRECTO')
            despacho.estado = 'ASIGNADO'
            despacho.save()
            messages.success(request, f'Despacho #{despacho.id_despacho} creado exitosamente')
            return redirect('despacho_detail', pk=despacho.id_despacho)
    else:
        form = DespachoDirectoForm()
    
    return render(request, 'despacho/form_directo.html', {'form': form})


def despacho_receta_create(request):
    """Crear despacho con receta"""
    if request.method == 'POST':
        form = DespachoConRecetaForm(request.POST)
        if form.is_valid():
            despacho = form.save(commit=False)
            despacho.id_tipo_despacho = TipoDespacho.objects.get(nombre_tipo='DESPACHO CON RECETA')
            despacho.estado = 'ASIGNADO'
            despacho.save()
            
            # Crear registro de receta
            RecetaDespacho.objects.create(
                id_despacho=despacho,
                numero_receta=form.cleaned_data.get('numero_receta'),
                nombre_medico=form.cleaned_data.get('nombre_medico'),
                fecha_emision=form.cleaned_data.get('fecha_emision_receta'),
                observaciones=form.cleaned_data.get('observaciones_receta')
            )
            
            messages.success(request, f'Despacho con receta #{despacho.id_despacho} creado exitosamente')
            return redirect('despacho_detail', pk=despacho.id_despacho)
    else:
        form = DespachoConRecetaForm()
    
    return render(request, 'despacho/form_receta.html', {'form': form})


def despacho_traslado_create(request):
    """Crear despacho con traslado"""
    if request.method == 'POST':
        form = DespachoConTrasladoForm(request.POST)
        if form.is_valid():
            despacho = form.save(commit=False)
            despacho.id_tipo_despacho = TipoDespacho.objects.get(nombre_tipo='DESPACHO CON TRASLADO')
            despacho.estado = 'ASIGNADO'
            despacho.save()
            messages.success(request, f'Despacho con traslado #{despacho.id_despacho} creado exitosamente')
            return redirect('despacho_detail', pk=despacho.id_despacho)
    else:
        form = DespachoConTrasladoForm()
    
    return render(request, 'despacho/form_traslado.html', {'form': form})


def despacho_reenvio_create(request):
    """Crear despacho con reenvío"""
    if request.method == 'POST':
        form = DespachoConReenvioForm(request.POST)
        if form.is_valid():
            despacho_original = form.cleaned_data['id_despacho_original']
            
            # Crear nuevo despacho basado en el original
            despacho = Despacho.objects.create(
                id_tipo_despacho=TipoDespacho.objects.get(nombre_tipo='DESPACHO CON REENVIO'),
                id_farmacia_origen=despacho_original.id_farmacia_origen,
                id_farmacia_origen_secundaria=despacho_original.id_farmacia_origen_secundaria,
                id_motorista=form.cleaned_data['id_motorista'],
                id_moto=form.cleaned_data['id_moto'],
                direccion_entrega=form.cleaned_data['direccion_entrega'],
                estado='ASIGNADO',
                codigo_orden_farmacia=despacho_original.codigo_orden_farmacia,
                id_despacho_original=despacho_original,
                observaciones=form.cleaned_data['observaciones']
            )
            
            messages.success(request, f'Reenvío #{despacho.id_despacho} creado exitosamente')
            return redirect('despacho_detail', pk=despacho.id_despacho)
    else:
        form = DespachoConReenvioForm()
    
    return render(request, 'despacho/form_reenvio.html', {'form': form})


def despacho_update(request, pk):
    """Modificar despacho"""
    despacho = get_object_or_404(Despacho, id_despacho=pk)
    
    # No permitir modificar despachos finalizados o cancelados
    if despacho.estado in ['FINALIZADO', 'CANCELADO']:
        messages.error(request, 'No se puede modificar un despacho finalizado o cancelado')
        return redirect('despacho_detail', pk=pk)
    
    if request.method == 'POST':
        form = ModificarDespachoForm(request.POST, instance=despacho)
        if form.is_valid():
            despacho = form.save(commit=False)
            if despacho.estado == 'FINALIZADO':
                despacho.fecha_finalizacion = timezone.now()
            despacho.save()
            messages.success(request, 'Despacho modificado exitosamente')
            return redirect('despacho_detail', pk=pk)
    else:
        form = ModificarDespachoForm(instance=despacho)
    
    return render(request, 'despacho/form_modificar.html', {
        'form': form,
        'despacho': despacho
    })


def despacho_anular(request, pk):
    """Anular despacho"""
    despacho = get_object_or_404(Despacho, id_despacho=pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        
        # Cambiar estado a CANCELADO
        despacho.estado = 'CANCELADO'
        despacho.observaciones = f"{despacho.observaciones or ''}\n[ANULADO] {motivo}".strip()
        despacho.save()
        
        messages.success(request, f'Despacho #{despacho.id_despacho} anulado exitosamente')
        return redirect('despacho_list')
    
    return render(request, 'despacho/anular.html', {'despacho': despacho})


# ============= REPORTES =============

def reporte_diario(request):
    """Generar reporte diario"""
    fecha = request.GET.get('fecha')
    if fecha:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    else:
        fecha_obj = timezone.now().date()
    
    # Despachos del día
    despachos = Despacho.objects.filter(fecha_creacion__date=fecha_obj)
    
    # Estadísticas
    total_despachos = despachos.count()
    despachos_por_estado = despachos.values('estado').annotate(total=Count('id_despacho'))
    despachos_por_tipo = despachos.values('id_tipo_despacho__nombre_tipo').annotate(total=Count('id_despacho'))
    
    # Despachos por región
    despachos_por_region = despachos.values(
        'id_farmacia_origen__id_comuna__id_region__nombre_region'
    ).annotate(total=Count('id_despacho'))
    
    # Total de incidencias
    total_incidencias = Incidencia.objects.filter(
        id_despacho__fecha_creacion__date=fecha_obj
    ).count()
    
    context = {
        'fecha': fecha_obj,
        'total_despachos': total_despachos,
        'despachos_por_estado': despachos_por_estado,
        'despachos_por_tipo': despachos_por_tipo,
        'despachos_por_region': despachos_por_region,
        'total_incidencias': total_incidencias,
        'despachos': despachos[:10],  # Últimos 10
    }
    
    return render(request, 'despacho/reporte_diario.html', context)


def reporte_mensual(request):
    """Generar reporte mensual"""
    fecha = request.GET.get('fecha')
    if fecha:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    else:
        fecha_obj = timezone.now().date()
    
    # Primer y último día del mes
    primer_dia = fecha_obj.replace(day=1)
    if fecha_obj.month == 12:
        ultimo_dia = fecha_obj.replace(year=fecha_obj.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        ultimo_dia = fecha_obj.replace(month=fecha_obj.month + 1, day=1) - timedelta(days=1)
    
    # Despachos del mes
    despachos = Despacho.objects.filter(
        fecha_creacion__date__gte=primer_dia,
        fecha_creacion__date__lte=ultimo_dia
    )
    
    # Estadísticas
    total_despachos = despachos.count()
    despachos_por_estado = despachos.values('estado').annotate(total=Count('id_despacho'))
    despachos_por_tipo = despachos.values('id_tipo_despacho__nombre_tipo').annotate(total=Count('id_despacho'))
    
    # Despachos por región
    despachos_por_region = despachos.values(
        'id_farmacia_origen__id_comuna__id_region__nombre_region'
    ).annotate(total=Count('id_despacho'))
    
    # Total de incidencias
    total_incidencias = Incidencia.objects.filter(
        id_despacho__fecha_creacion__date__gte=primer_dia,
        id_despacho__fecha_creacion__date__lte=ultimo_dia
    ).count()
    
    context = {
        'fecha': fecha_obj,
        'primer_dia': primer_dia,
        'ultimo_dia': ultimo_dia,
        'total_despachos': total_despachos,
        'despachos_por_estado': despachos_por_estado,
        'despachos_por_tipo': despachos_por_tipo,
        'despachos_por_region': despachos_por_region,
        'total_incidencias': total_incidencias,
    }
    
    return render(request, 'despacho/reporte_mensual.html', context)


def generar_pdf_reporte(request):
    tipo_reporte = request.GET.get('tipo', 'diario')  # diario o mensual
    fecha = request.GET.get('fecha', timezone.now().date())
    
    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
    
    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    if tipo_reporte == 'diario':
        title = f"Reporte Diario de Despachos - {fecha.strftime('%d/%m/%Y')}"
        despachos = Despacho.objects.filter(fecha_creacion__date=fecha)
    else:
        primer_dia = fecha.replace(day=1)
        if fecha.month == 12:
            ultimo_dia = fecha.replace(year=fecha.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            ultimo_dia = fecha.replace(month=fecha.month + 1, day=1) - timedelta(days=1)
        title = f"Reporte Mensual - {fecha.strftime('%B %Y')}"
        despachos = Despacho.objects.filter(
            fecha_creacion__date__gte=primer_dia,
            fecha_creacion__date__lte=ultimo_dia
        )
    
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Estadísticas generales
    data = [['Métrica', 'Valor']]
    data.append(['Total Despachos', str(despachos.count())])
    
    # Por estado
    for estado in Despacho.ESTADO_CHOICES:
        count = despachos.filter(estado=estado[0]).count()
        data.append([f'  {estado[1]}', str(count)])
    
    # Por tipo
    for tipo in TipoDespacho.objects.all():
        count = despachos.filter(id_tipo_despacho=tipo).count()
        data.append([f'  {tipo.nombre_tipo}', str(count)])
    
    # Incidencias
    if tipo_reporte == 'diario':
        incidencias = Incidencia.objects.filter(id_despacho__fecha_creacion__date=fecha)
    else:
        incidencias = Incidencia.objects.filter(
            id_despacho__fecha_creacion__date__gte=primer_dia,
            id_despacho__fecha_creacion__date__lte=ultimo_dia
        )
    data.append(['Total Incidencias', str(incidencias.count())])
    
    # Crear tabla
    table = Table(data, colWidths=[4*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener el valor del BytesIO buffer y escribirlo a la respuesta
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}_{fecha}.pdf"'
    response.write(pdf)
    
    return response