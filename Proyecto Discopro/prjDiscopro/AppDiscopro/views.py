from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from .models import (Farmacia, Motorista, Moto, ContactoEmergencia, 
                     LicenciaMotorista, DocumentacionMoto, AsignacionMotoristaFarmacia)
from .forms import (FarmaciaForm, MotoristaForm, ContactoEmergenciaForm, 
                    LicenciaMotoristaForm, MotoForm, DocumentacionMotoForm)


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