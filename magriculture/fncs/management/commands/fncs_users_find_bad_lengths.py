from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# Example usage:
# python manage.py fncs_users_find_bad_lengths


class Command(BaseCommand):
    help = "Search for too long and too short numbers (+260 numbers only)"

    def handle(self, *args, **options):
        users = User.objects.filter(username__startswith='+260')
        total = len(users)
        expected_length = 13

        if total == 0:
            self.stdout.write('No users starting with +260\n')

        self.stdout.write('Short usernames:\n')

        for user in users:
            stripped = user.username.replace(' ', '')
            length = len(stripped)
            if length < expected_length:
                self.stdout.write(user.username + '\n')

        self.stdout.write('\nLong usernames:\n')

        for user in users:
            stripped = user.username.replace(' ', '')
            length = len(stripped)
            if length > expected_length:
                self.stdout.write(user.username + '\n')
