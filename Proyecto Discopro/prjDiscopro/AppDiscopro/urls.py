from django.urls import path
from . import views

urlpatterns = [
    # Farmacia
    path('farmacia/', views.FarmaciaListView.as_view(), name='farmacia_list'),
    path('farmacia/crear/', views.FarmaciaCreateView.as_view(), name='farmacia_create'),
    path('farmacia/<int:pk>/', views.farmacia_detail, name='farmacia_detail'),
    path('farmacia/<int:pk>/editar/', views.FarmaciaUpdateView.as_view(), name='farmacia_update'),
    path('farmacia/<int:pk>/eliminar/', views.FarmaciaDeleteView.as_view(), name='farmacia_delete'),
    
    # Motorista
    path('motorista/', views.MotoristaListView.as_view(), name='motorista_list'),
    path('motorista/crear/', views.MotoristaCreateView.as_view(), name='motorista_create'),
    path('motorista/<int:pk>/', views.motorista_detail, name='motorista_detail'),
    path('motorista/<int:pk>/editar/', views.MotoristaUpdateView.as_view(), name='motorista_update'),
    path('motorista/<int:pk>/eliminar/', views.MotoristaDeleteView.as_view(), name='motorista_delete'),
    
    # Moto
    path('moto/', views.MotoListView.as_view(), name='moto_list'),
    path('moto/crear/', views.MotoCreateView.as_view(), name='moto_create'),
    path('moto/<int:pk>/', views.moto_detail, name='moto_detail'),
    path('moto/<int:pk>/editar/', views.MotoUpdateView.as_view(), name='moto_update'),
    path('moto/<int:pk>/eliminar/', views.MotoDeleteView.as_view(), name='moto_delete'),
]