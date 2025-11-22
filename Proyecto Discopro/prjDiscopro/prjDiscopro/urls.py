"""
URL configuration for prjDiscopro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from AppDiscopro.views import FarmaciaListView

# Configuración de URLs del proyecto.
# Nota: hay dos rutas con path('', ...). El primer path sirve la vista 'home' y
# el segundo incluye todo AppDiscopro.urls. El orden importa: la primera definición
# de path('') se evalúa antes que la inclusión. Mantener claridad en rutas raíz.

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', FarmaciaListView.as_view(), name='home'),
    path('', include('AppDiscopro.urls')),
]


