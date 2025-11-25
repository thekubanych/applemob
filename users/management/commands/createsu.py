from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create superuser if not exists'

    def handle(self, *args, **options):
        User = get_user_model()

        # Используем phone_number если это основное поле
        if not User.objects.filter(phone_number='+996221093030').exists():
            User.objects.create_superuser(
                phone_number='+996221093030',  # или другое поле
                email='kubanychmuhtarov@gmail.com',
                password='1234'
            )
            self.stdout.write(
                self.style.SUCCESS('Superuser created successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser already exists!')
            )