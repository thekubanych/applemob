from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create superuser if not exists'

    def handle(self, *args, **options):
        User = get_user_model()

        if not User.objects.filter(email='kubanychmuhtarov@gmail.com').exists():
            User.objects.create_superuser(
                email='kubanychmuhtarov@gmail.com',
                phone_number='+996555123456',  # Добавьте любой номер
                password='1234'
            )
            self.stdout.write(
                self.style.SUCCESS('Superuser created successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser already exists!')
            )