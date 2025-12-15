"""
Vistas de autenticación y gestión de usuarios
Archivo: AppDiscopro/auth_views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.utils import timezone
from .models import UsuarioPersonalizado, Rol
from .forms import (
    RegistroUsuarioForm, LoginForm, CambiarPasswordForm, 
    EditarPerfilForm
)
from .decorators import gerente_requerido, GerenteRequeridoMixin
import logging

logger = logging.getLogger('AppDiscopro')


# ============= VISTAS DE AUTENTICACIÓN =============

def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Configurar duración de sesión
                if not remember_me:
                    request.session.set_expiry(0)  # Expira al cerrar navegador
                else:
                    request.session.set_expiry(1209600)  # 2 semanas
                
                # Actualizar último acceso
                user.ultimo_acceso = timezone.now()
                user.save(update_fields=['ultimo_acceso'])
                
                logger.info(f"Usuario {username} ha iniciado sesión exitosamente")
                messages.success(request, f'¡Bienvenido, {user.nombre_completo}!')
                
                # Redirigir según el parámetro 'next' o a home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
                logger.warning(f"Intento de inicio de sesión fallido para usuario: {username}")
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vista de cierre de sesión"""
    username = request.user.nombre_usuario if hasattr(request.user, 'nombre_usuario') else 'Usuario'
    logout(request)
    logger.info(f"Usuario {username} ha cerrado sesión")
    messages.info(request, 'Has cerrado sesión exitosamente')
    return redirect('login')


@gerente_requerido
def registro_usuario_view(request):
    """Vista de registro de usuarios (solo gerentes)"""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f"Nuevo usuario registrado: {user.nombre_usuario} por {request.user.nombre_usuario}")
            messages.success(
                request, 
                f'Usuario {user.nombre_usuario} registrado exitosamente con rol {user.get_rol_display()}'
            )
            return redirect('usuarios_list')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'auth/registro.html', {'form': form})


@login_required
def perfil_view(request):
    """Vista del perfil del usuario"""
    from django.utils import timezone
    from datetime import timedelta
    from .models import Despacho
    
    usuario = request.user
    # Calcular despachos creados (total)
    total_despachos = usuario.despachos_creados.count()
    
    # Calcular despachos de los últimos 30 días
    fecha_hace_30_dias = timezone.now() - timedelta(days=30)
    despachos_30_dias = usuario.despachos_creados.filter(
        fecha_creacion__gte=fecha_hace_30_dias
    ).count()
    
    return render(request, 'auth/perfil.html', {
        'usuario': usuario,
        'total_despachos': total_despachos,
        'despachos_30_dias': despachos_30_dias,
    })


@login_required
def editar_perfil_view(request):
    """Vista para editar el perfil del usuario"""
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            logger.info(f"Usuario {request.user.nombre_usuario} actualizó su perfil")
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = EditarPerfilForm(instance=request.user)
    
    return render(request, 'auth/editar_perfil.html', {'form': form})


@login_required
def cambiar_password_view(request):
    """Vista para cambiar contraseña"""
    if request.method == 'POST':
        form = CambiarPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantener la sesión activa
            logger.info(f"Usuario {request.user.nombre_usuario} cambió su contraseña")
            messages.success(request, 'Contraseña actualizada exitosamente')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = CambiarPasswordForm(request.user)
    
    return render(request, 'auth/cambiar_password.html', {'form': form})


# ============= GESTIÓN DE USUARIOS (SOLO GERENTES) =============

class UsuariosListView(GerenteRequeridoMixin, ListView):
    """Lista de usuarios del sistema (solo gerentes)"""
    model = UsuarioPersonalizado
    template_name = 'auth/usuarios_list.html'
    context_object_name = 'usuarios'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('id_rol')
        query = self.request.GET.get('q')
        rol = self.request.GET.get('rol')
        
        if query:
            queryset = queryset.filter(
                Q(nombre_usuario__icontains=query) |
                Q(nombre_completo__icontains=query) |
                Q(correo__icontains=query)
            )
        
        if rol:
            queryset = queryset.filter(id_rol__nombre_rol=rol)
        
        return queryset.order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['roles'] = Rol.objects.all()
        context['rol_filtro'] = self.request.GET.get('rol', '')
        
        # Estadísticas
        context['total_usuarios'] = UsuarioPersonalizado.objects.count()
        context['usuarios_por_rol'] = UsuarioPersonalizado.objects.values(
            'id_rol__nombre_rol'
        ).annotate(total=Count('id_usuario'))
        
        return context


@gerente_requerido
def usuario_detail_view(request, pk):
    """Vista detalle de un usuario (solo gerentes)"""
    usuario = get_object_or_404(UsuarioPersonalizado, id_usuario=pk)
    
    # Obtener estadísticas de despachos creados por este usuario
    from .models import Despacho
    despachos_creados = Despacho.objects.filter(creado_por=usuario).count()
    despachos_por_estado = Despacho.objects.filter(creado_por=usuario).values(
        'estado'
    ).annotate(total=Count('id_despacho'))
    
    context = {
        'usuario': usuario,
        'despachos_creados': despachos_creados,
        'despachos_por_estado': despachos_por_estado,
    }
    
    return render(request, 'auth/usuario_detail.html', context)


@gerente_requerido
def usuario_toggle_active_view(request, pk):
    """Activar/desactivar usuario (solo gerentes)"""
    if request.method == 'POST':
        usuario = get_object_or_404(UsuarioPersonalizado, id_usuario=pk)
        
        # No permitir desactivar al propio usuario
        if usuario == request.user:
            messages.error(request, 'No puedes desactivar tu propia cuenta')
            return redirect('usuarios_list')
        
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        estado = 'activado' if usuario.is_active else 'desactivado'
        logger.info(f"Usuario {usuario.nombre_usuario} {estado} por {request.user.nombre_usuario}")
        messages.success(request, f'Usuario {usuario.nombre_usuario} {estado} exitosamente')
    
    return redirect('usuarios_list')


@gerente_requerido
def usuario_cambiar_rol_view(request, pk):
    """Cambiar rol de un usuario (solo gerentes)"""
    usuario = get_object_or_404(UsuarioPersonalizado, id_usuario=pk)
    
    if request.method == 'POST':
        nuevo_rol_id = request.POST.get('rol_id')
        
        # No permitir cambiar el rol del propio usuario
        if usuario == request.user:
            messages.error(request, 'No puedes cambiar tu propio rol')
            return redirect('usuarios_list')
        
        try:
            nuevo_rol = Rol.objects.get(id_rol=nuevo_rol_id)
            rol_anterior = usuario.id_rol.get_nombre_rol_display()
            usuario.id_rol = nuevo_rol
            usuario.save()
            
            logger.info(
                f"Rol de usuario {usuario.nombre_usuario} cambiado de {rol_anterior} "
                f"a {nuevo_rol.get_nombre_rol_display()} por {request.user.nombre_usuario}"
            )
            messages.success(
                request, 
                f'Rol de {usuario.nombre_usuario} cambiado a {nuevo_rol.get_nombre_rol_display()}'
            )
        except Rol.DoesNotExist:
            messages.error(request, 'Rol no válido')
    
    return redirect('usuario_detail', pk=pk)


@gerente_requerido
def usuario_resetear_password_view(request, pk):
    """Resetear contraseña de un usuario (solo gerentes)"""
    usuario = get_object_or_404(UsuarioPersonalizado, id_usuario=pk)
    
    if request.method == 'POST':
        nueva_password = request.POST.get('nueva_password')
        confirmar_password = request.POST.get('confirmar_password')
        
        # No permitir resetear la contraseña del propio usuario
        if usuario == request.user:
            messages.error(request, 'No puedes resetear tu propia contraseña desde aquí')
            return redirect('usuarios_list')
        
        if nueva_password and nueva_password == confirmar_password:
            if len(nueva_password) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            else:
                usuario.set_password(nueva_password)
                usuario.save()
                
                logger.warning(
                    f"Contraseña de usuario {usuario.nombre_usuario} reseteada "
                    f"por {request.user.nombre_usuario}"
                )
                messages.success(
                    request, 
                    f'Contraseña de {usuario.nombre_usuario} reseteada exitosamente'
                )
                return redirect('usuario_detail', pk=pk)
        else:
            messages.error(request, 'Las contraseñas no coinciden')
    
    return render(request, 'auth/resetear_password.html', {'usuario': usuario})