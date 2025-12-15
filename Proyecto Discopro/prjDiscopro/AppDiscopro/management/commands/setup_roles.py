"""
Comando personalizado para configurar roles iniciales
Uso: python manage.py setup_roles
"""
from django.core.management.base import BaseCommand
from AppDiscopro.models import Rol


class Command(BaseCommand):
    help = 'Configura los roles iniciales del sistema'

    def handle(self, *args, **kwargs):
        roles_data = [
            {
                'id_rol': 1,
                'nombre_rol': 'GERENTE',
                'descripcion': 'Acceso completo al sistema, puede gestionar usuarios y ver todos los reportes'
            },
            {
                'id_rol': 2,
                'nombre_rol': 'SUPERVISOR',
                'descripcion': 'Puede supervisar operaciones y ver reportes, pero no puede crear despachos'
            },
            {
                'id_rol': 3,
                'nombre_rol': 'OPERADORA',
                'descripcion': 'Puede crear y gestionar despachos, acceso limitado a reportes'
            },
        ]

        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre_rol=rol_data['nombre_rol'],
                defaults={
                    'descripcion': rol_data['descripcion']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Rol "{rol.get_nombre_rol_display()}" creado')
                )
            else:
                # Actualizar descripción si ya existe
                rol.descripcion = rol_data['descripcion']
                rol.save()
                self.stdout.write(
                    self.style.WARNING(f'⚠ Rol "{rol.get_nombre_rol_display()}" ya existía (actualizado)')
                )

        self.stdout.write(
            self.style.SUCCESS('\n✅ Roles configurados exitosamente')
        )