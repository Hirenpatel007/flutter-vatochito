from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS('Superuser already exists.'))
            return

        username = 'admin'
        email = 'admin@example.com'
        password = 'admin'

        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS(f'Successfully created superuser: {username}'))
