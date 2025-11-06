from django.core.management.base import BaseCommand
from django.db import transaction
from estimator.models import (
    Material, Component, Project, Labor, Equipment, 
    ProjectMaterial, ProjectComponent, ProjectLabor, ProjectEquipment
)

class Command(BaseCommand):
    help = 'Clear all data from estimator app tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL data from estimator tables. '
                    'Use --confirm flag to proceed.'
                )
            )
            return

        try:
            with transaction.atomic():
                # Delete in reverse dependency order
                ProjectEquipment.objects.all().delete()
                ProjectLabor.objects.all().delete() 
                ProjectComponent.objects.all().delete()
                ProjectMaterial.objects.all().delete()
                Project.objects.all().delete()
                Equipment.objects.all().delete()
                Labor.objects.all().delete()
                Component.objects.all().delete()
                Material.objects.all().delete()

                self.stdout.write(
                    self.style.SUCCESS('Successfully cleared all estimator tables')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing tables: {str(e)}')
            )
