from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Clear data from a specific table'

    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str, help='Name of the model to clear')
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of data',
        )

    def handle(self, *args, **options):
        model_name = options['model_name']
        
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    f'This will delete ALL data from {model_name} table. '
                    'Use --confirm flag to proceed.'
                )
            )
            return

        try:
            # Get the model from estimator app
            model = apps.get_model('estimator', model_name)
            count = model.objects.count()
            model.objects.all().delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {count} records from {model_name} table'
                )
            )
        except LookupError:
            self.stdout.write(
                self.style.ERROR(f'Model {model_name} not found in estimator app')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing {model_name} table: {str(e)}')
            )
