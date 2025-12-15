"""
Decoradores y Mixins para control de acceso por roles
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


# ============= DECORADORES PARA VISTAS FUNCIONALES =============

def rol_requerido(*roles_permitidos):
    """
    Decorador que verifica si el usuario tiene uno de los roles permitidos
    Uso: @rol_requerido('GERENTE', 'SUPERVISOR')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'id_rol'):
                messages.error(request, 'Tu cuenta no tiene un rol asignado. Contacta al administrador.')
                return redirect('home')
            
            if request.user.id_rol.nombre_rol in roles_permitidos:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request, 
                    f'No tienes permisos para acceder a esta sección. Se requiere rol: {", ".join(roles_permitidos)}'
                )
                return redirect('home')
        return wrapper
    return decorator


def gerente_requerido(view_func):
    """
    Decorador para vistas que solo pueden acceder gerentes
    Uso: @gerente_requerido
    """
    return rol_requerido('GERENTE')(view_func)


def supervisor_o_gerente(view_func):
    """
    Decorador para vistas que pueden acceder supervisores y gerentes
    Uso: @supervisor_o_gerente
    """
    return rol_requerido('GERENTE', 'SUPERVISOR')(view_func)


def operadora_o_gerente(view_func):
    """
    Decorador para vistas que pueden acceder operadoras y gerentes
    Uso: @operadora_o_gerente
    """
    return rol_requerido('GERENTE', 'OPERADORA')(view_func)


# ============= MIXINS PARA VISTAS BASADAS EN CLASES =============

class RolRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para vistas basadas en clases que requieren un rol específico
    Uso: class MiVista(RolRequeridoMixin, ListView):
             roles_permitidos = ['GERENTE', 'SUPERVISOR']
    """
    roles_permitidos = []
    redirect_url = 'home'
    
    def test_func(self):
        """Verifica si el usuario tiene uno de los roles permitidos"""
        if not hasattr(self.request.user, 'id_rol'):
            return False
        return self.request.user.id_rol.nombre_rol in self.roles_permitidos
    
    def handle_no_permission(self):
        """Maneja el caso cuando el usuario no tiene permisos"""
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                f'No tienes permisos para acceder a esta sección. Se requiere rol: {", ".join(self.roles_permitidos)}'
            )
            return redirect(self.redirect_url)
        return super().handle_no_permission()


class GerenteRequeridoMixin(RolRequeridoMixin):
    """Mixin para vistas que solo pueden acceder gerentes"""
    roles_permitidos = ['GERENTE']


class SupervisorOGerenteMixin(RolRequeridoMixin):
    """Mixin para vistas que pueden acceder supervisores y gerentes"""
    roles_permitidos = ['GERENTE', 'SUPERVISOR']


class OperadoraOGerenteMixin(RolRequeridoMixin):
    """Mixin para vistas que pueden acceder operadoras y gerentes"""
    roles_permitidos = ['GERENTE', 'OPERADORA']


class TodosLosRolesMixin(RolRequeridoMixin):
    """Mixin para vistas que pueden acceder todos los roles autenticados"""
    roles_permitidos = ['GERENTE', 'SUPERVISOR', 'OPERADORA']


# ============= FUNCIONES AUXILIARES =============

def usuario_puede_crear_despacho(user):
    """Verifica si el usuario puede crear despachos"""
    if not hasattr(user, 'id_rol'):
        return False
    return user.id_rol.nombre_rol in ['GERENTE', 'OPERADORA']


def usuario_puede_ver_reportes(user):
    """Verifica si el usuario puede ver reportes completos"""
    if not hasattr(user, 'id_rol'):
        return False
    return user.id_rol.nombre_rol in ['GERENTE', 'SUPERVISOR']


def usuario_puede_gestionar_usuarios(user):
    """Verifica si el usuario puede gestionar otros usuarios"""
    if not hasattr(user, 'id_rol'):
        return False
    return user.id_rol.nombre_rol == 'GERENTE'


def usuario_puede_modificar_despacho(user, despacho):
    """
    Verifica si el usuario puede modificar un despacho específico
    - Gerentes pueden modificar cualquier despacho
    - Operadoras solo pueden modificar sus propios despachos
    - Supervisores solo pueden ver, no modificar
    """
    if not hasattr(user, 'id_rol'):
        return False
    
    if user.id_rol.nombre_rol == 'GERENTE':
        return True
    
    if user.id_rol.nombre_rol == 'OPERADORA':
        # Verificar si el despacho fue creado por esta operadora
        return despacho.creado_por == user
    
    return False


def usuario_puede_anular_despacho(user):
    """Verifica si el usuario puede anular despachos"""
    if not hasattr(user, 'id_rol'):
        return False
    return user.id_rol.nombre_rol == 'GERENTE'