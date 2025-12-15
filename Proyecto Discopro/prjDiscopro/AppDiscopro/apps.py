from django.apps import AppConfig


class AppdiscoproConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Nombre del módulo Python (debe coincidir con el paquete importable)
    name = 'AppDiscopro'
    # Label explícito para que las referencias históricas en migraciones
    # coincidan con el valor usado en archivos de migración existentes.
    # Usamos 'AppDiscopro' porque algunas migraciones existentes referencian
    # el app label con mayúsculas y cambiarlo evita NodeNotFoundError.
    label = 'AppDiscopro'
